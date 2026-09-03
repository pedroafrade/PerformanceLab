"""One stored Training Coach permission for manual and automatic workflows."""

import ast
from contextlib import nullcontext
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock

import pytest


ROOT = Path(__file__).resolve().parents[1]


def load(relative, **dependencies):
    """Load actual module logic without optional provider/app startup imports."""
    tree = ast.parse((ROOT / relative).read_text(encoding="utf-8"))
    tree.body = [
        node for node in tree.body
        if not (isinstance(node, ast.ImportFrom)
                and (node.module or "").startswith("performancelab"))
        and not (isinstance(node, ast.Import)
                 and any(alias.name == "streamlit" for alias in node.names))
    ]
    scope = {"__name__": __name__, **dependencies}
    exec(compile(tree, relative, "exec"), scope)
    return scope


MODEL = load("performancelab/training_coach_consent.py")
Consent = MODEL["TrainingCoachConsent"]
VERSION = MODEL["TRAINING_COACH_CONSENT_VERSION"]
POLICY = load("performancelab/coaching/daily_brief_policy.py",
              TrainingCoachConsent=Consent, TRAINING_COACH_CONSENT_VERSION=VERSION)
Manager = load(
    "performancelab/application/manage_training_coach_consent.py",
    TrainingCoachConsent=Consent, TrainingCoachConsentRepository=object,
    TRAINING_COACH_CONSENT_VERSION=VERSION,
)["ManageTrainingCoachConsent"]
Repository = load(
    "performancelab/storage/json_training_coach_consent_repository.py",
    TrainingCoachConsent=Consent,
)["JsonTrainingCoachConsentRepository"]
NOW = datetime(2026, 9, 4, 10, tzinfo=timezone.utc)


@pytest.fixture
def setup(tmp_path):
    repo = Repository(tmp_path)
    clock = MagicMock(return_value=NOW)
    return repo, Manager(repository=repo, clock=clock), clock


def eligible(manager, user="a"):
    version = POLICY["active_consent_version"](
        consent=manager.current(user_id=user), user_id=user,
    )
    key = POLICY["daily_brief_key"](
        athlete_id="athlete-" + user, now=NOW, timezone_name="UTC", context_digest="x",
    )
    return POLICY["decide_daily_brief"](
        requested=key, now=NOW, enabled=True, consent_version=version,
    ).action == POLICY["BriefAction"].GENERATE


def test_both_workflows_use_one_version_from_the_same_source():
    assert VERSION == "training-coach-consent-v2"
    assert POLICY["CONSENT_VERSION"] == VERSION
    text = (ROOT / "performancelab/coaching/daily_brief_policy.py").read_text(encoding="utf-8")
    assert "CONSENT_VERSION = TRAINING_COACH_CONSENT_VERSION" in text


def test_legacy_manual_permission_needs_confirmation_without_migration(setup):
    repo, manager, clock = setup
    old = Consent(user_id="a", granted_at=NOW, policy_version="training-coach-consent-v1")
    repo.save(old)
    assert not manager.is_permitted(user_id="a")
    assert not eligible(manager)
    assert repo.list_for_user("a") == (old,)
    manager.grant(user_id="a")
    assert manager.is_permitted(user_id="a") and eligible(manager)
    assert len(repo.list_for_user("a")) == 2


def test_one_grant_covers_both_and_survives_repository_reopen(setup, tmp_path):
    repo, manager, clock = setup
    consent = manager.grant(user_id="a")
    assert manager.grant(user_id="a") == consent
    reopened = Manager(repository=Repository(tmp_path), clock=clock)
    assert reopened.is_permitted(user_id="a")
    assert eligible(reopened)
    assert len(repo.list_for_user("a")) == 1
    assert not eligible(reopened, "b")


def test_one_withdrawal_blocks_both_but_preserves_history(setup):
    repo, manager, clock = setup
    manager.grant(user_id="a")
    clock.return_value += timedelta(minutes=1)
    manager.withdraw(user_id="a")
    manager.withdraw(user_id="a")
    assert not manager.is_permitted(user_id="a")
    assert not eligible(manager)
    assert len(repo.list_for_user("a")) == 1
    assert repo.list_for_user("a")[0].withdrawn_at is not None


def test_consent_from_other_user_does_not_authorize(setup):
    consent = setup[1].grant(user_id="a")
    assert POLICY["active_consent_version"](consent=consent, user_id="b") is None


def test_consent_alone_does_not_enable_generation(setup):
    consent = setup[1].grant(user_id="a")
    key = POLICY["daily_brief_key"](
        athlete_id="a", now=NOW, timezone_name="UTC", context_digest="x",
    )
    assert POLICY["decide_daily_brief"](
        requested=key, now=NOW, consent_version=consent.policy_version,
    ).reason == "feature_disabled"


def ui():
    st = MagicMock()
    st.dialog.return_value = lambda function: function
    st.columns.return_value = [MagicMock(), MagicMock()]
    return st, load("app/components/training_coach_consent.py", st=st)


@pytest.mark.parametrize("allow", [False, True])
def test_existing_dialog_is_the_only_grant_action(allow):
    st, scope = ui()
    st.button.side_effect = [False, allow]
    callback = MagicMock()
    scope["show_training_coach_consent_dialog"](on_allow=callback)
    assert callback.call_count == int(allow)
    assert [call.args[0] for call in st.button.call_args_list] == ["Not now", "Allow Training Coach"]
    st.checkbox.assert_not_called()


@pytest.mark.parametrize("permitted", [False, True])
def test_settings_keeps_one_permission_button(permitted):
    st, scope = ui()
    allow, withdraw = MagicMock(), MagicMock()
    scope["show_training_coach_consent_settings"](
        permitted=permitted, on_allow=allow, on_withdraw=withdraw,
    )
    st.button.assert_called_once()
    assert st.button.call_args.kwargs["on_click"] is (withdraw if permitted else allow)
    allow.assert_not_called()
    withdraw.assert_not_called()
    st.checkbox.assert_not_called()
    written = " ".join(str(c.args[0]) for c in st.write.call_args_list + st.caption.call_args_list)
    assert "automatic Daily Brief" in written
    assert "not active yet" in written


class User:
    user_id = "a"
    athlete_id = "athlete-a"
    email = "a@example.test"
    role = "athlete"
    is_athlete = True


class Authorization:
    def require_access(self, **kwargs):
        assert kwargs == dict(user_id="a", athlete_id="athlete-a", allowed_permissions=("owner",))


def empty_repository():
    repo = MagicMock()
    repo.list.return_value = ()
    repo.list_for_user.return_value = ()
    repo.list_for_athlete.return_value = ()
    return repo


def test_export_includes_unified_consent_and_legacy_history_for_owner_only(setup):
    repo, manager, clock = setup
    repo.save(Consent(user_id="a", granted_at=NOW, policy_version="training-coach-consent-v1"))
    manager.grant(user_id="a")
    manager.grant(user_id="b")
    service = load(
        "performancelab/application/export_participant_data.py",
        User=User, AthleteAuthorizationService=Authorization, athlete_to_dict=lambda athlete: {},
    )["ExportParticipantData"](
        athlete_repository=empty_repository(), external_identity_repository=empty_repository(),
        athlete_access_repository=empty_repository(),
        alpha_participation_consent_repository=empty_repository(),
        training_coach_consent_repository=repo, training_coach_usage_repository=empty_repository(),
        authorization=Authorization(),
    )
    records = service.execute(User(), generated_at=NOW).data["training_coach_consents"]
    assert {r["policy_version"] for r in records} == {VERSION, "training-coach-consent-v1"}
    assert all(r["user_id"] == "a" for r in records)


def test_account_deletion_removes_unified_consent_for_owner_only(setup):
    repo, manager, clock = setup
    manager.grant(user_id="a")
    manager.grant(user_id="b")
    service = load(
        "performancelab/application/delete_participant_data.py",
        User=User, AthleteAuthorizationService=Authorization,
    )["DeleteParticipantData"](
        athlete_repository=empty_repository(), user_repository=empty_repository(),
        external_identity_repository=empty_repository(), invitation_repository=empty_repository(),
        athlete_access_repository=empty_repository(),
        alpha_participation_consent_repository=empty_repository(),
        training_coach_consent_repository=repo, training_coach_usage_repository=empty_repository(),
        authorization=Authorization(), transaction_factory=nullcontext,
    )
    service.execute(User())
    assert not repo.list_for_user("a")
    assert manager.is_permitted(user_id="b")
