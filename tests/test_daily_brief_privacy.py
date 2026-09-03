"""Privacy hooks with real SQL transactions; no provider or Streamlit startup."""

import ast
from pathlib import Path
from runpy import run_path
from types import SimpleNamespace as NS
from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine, select, text


ROOT = Path(__file__).resolve().parents[1]
SQL = run_path(str(Path(__file__).with_name("test_daily_brief_store.py")))
load, TABLE, NOW = SQL["load"], SQL["TABLE"], SQL["NOW"]
Privacy = load("performancelab/storage/daily_brief_privacy_repository.py",
               daily_briefs=TABLE,
               training_coach_quota_reservations=SQL["SCHEMA"]["training_coach_quota_reservations"]
               )["DailyBriefPrivacyRepository"]
User = load("performancelab/identity.py")["User"]
access_model = load("performancelab/athlete_access.py")
Grant = access_model["AthleteAccessGrant"]
Authorization = load("performancelab/authorization.py", AthleteAccessGrant=Grant,
                     AthleteAccessPermission=access_model["AthleteAccessPermission"],
                     AthleteAccessRepository=object)["AthleteAuthorizationService"]
consent_model = load("performancelab/training_coach_consent.py")
Consent = consent_model["TrainingCoachConsent"]
ConsentRepository = load("performancelab/storage/postgresql_training_coach_consent_repository.py",
                         training_coach_consents=SQL["SCHEMA"]["training_coach_consents"],
                         TrainingCoachConsent=Consent)["PostgreSQLTrainingCoachConsentRepository"]
Manager = load("performancelab/application/manage_training_coach_consent.py",
               TrainingCoachConsentRepository=object, TrainingCoachConsent=Consent,
               TRAINING_COACH_CONSENT_VERSION=consent_model["TRAINING_COACH_CONSENT_VERSION"]
               )["ManageTrainingCoachConsent"]
Exporter = load("performancelab/application/export_participant_data.py",
                AthleteAuthorizationService=Authorization, User=User,
                athlete_to_dict=lambda athlete: {"athlete_id": athlete.athlete_id}
                )["ExportParticipantData"]
Deleter = load("performancelab/application/delete_participant_data.py",
               AthleteAuthorizationService=Authorization, User=User)["DeleteParticipantData"]


@pytest.fixture
def engine(tmp_path):
    fixture = SQL["engine"].__wrapped__(tmp_path)
    value = next(fixture)
    with value.begin() as connection:
        SQL["SCHEMA"]["training_coach_consents"].create(connection)
    yield value
    try:
        next(fixture)
    except StopIteration:
        pass


def populate(engine):
    store = SQL["Store"](engine)
    for user, athlete in (("user-a", "athlete-a"), ("user-b", "athlete-b")):
        lease = store.reserve(user_id=user, key=SQL["key"](athlete=athlete), now=NOW)
        assert store.complete(lease, narrative="Brief for " + user, reason="daily", now=NOW)
    lease = store.reserve(user_id="user-a", key=SQL["key"]("changed"), now=NOW)
    return store, lease


def user_and_repositories():
    user = User(email="a@example.com", user_id="user-a", athlete_id="athlete-a")
    grant = Grant(user_id=user.user_id, athlete_id=user.athlete_id, permission="owner")
    access = MagicMock()
    access.get.return_value = grant
    access.list_for_user.return_value = [grant]
    access.list_for_athlete.return_value = []
    empty = MagicMock()
    empty.list.return_value = []
    empty.list_for_user.return_value = []
    athletes = MagicMock()
    athletes.get.return_value = NS(athlete_id="athlete-a")
    kwargs = dict(athlete_repository=athletes, external_identity_repository=empty,
                  athlete_access_repository=access, alpha_participation_consent_repository=empty,
                  training_coach_consent_repository=empty, training_coach_usage_repository=empty,
                  authorization=Authorization(access))
    return user, kwargs, empty


def test_export_contains_only_current_owners_saved_content(engine):
    store, lease = populate(engine)
    user, kwargs, _ = user_and_repositories()
    with engine.begin() as connection:
        privacy = Privacy(connection)
        data = Exporter(**kwargs, daily_brief_privacy_repository=privacy).execute(
            user, generated_at=NOW).data
        assert len(data["daily_briefs"]) == 1
        assert data["daily_briefs"][0]["narrative"] == "Brief for user-a"
        assert set(data["daily_briefs"][0]) == {"key", "narrative", "generated_at", "reason"}
        assert lease.token not in str(data)
        assert "user-b" not in str(data)
        assert privacy.export_for_user("user-a", athlete_id="athlete-b") == []
    assert store.is_active(lease, now=NOW)


def test_legacy_local_export_explicitly_has_no_daily_briefs():
    user, kwargs, _ = user_and_repositories()
    assert Exporter(**kwargs).execute(user, generated_at=NOW).data["daily_briefs"] == []


def test_export_requires_owner_before_touching_daily_briefs():
    user, kwargs, _ = user_and_repositories()
    kwargs["athlete_access_repository"].get.side_effect = KeyError("no access")
    privacy = MagicMock()
    with pytest.raises(PermissionError):
        Exporter(**kwargs, daily_brief_privacy_repository=privacy).execute(user, generated_at=NOW)
    privacy.export_for_user.assert_not_called()


def test_withdrawal_cancels_lease_but_preserves_exportable_content(engine):
    store, lease = populate(engine)
    with engine.begin() as connection:
        repo = ConsentRepository(connection)
        repo.save(Consent(user_id="user-a", granted_at=NOW))
    with engine.begin() as connection:
        manager = Manager(repository=ConsentRepository(connection), clock=lambda: NOW,
                          daily_brief_privacy_repository=Privacy(connection))
        assert not manager.withdraw(user_id="user-a").is_active
    assert not store.is_active(lease, now=NOW)
    assert not store.complete(lease, narrative="Too late", reason="daily", now=NOW)
    assert store.export_for_user("user-a")[0]["narrative"] == "Brief for user-a"
    assert store.export_for_user("user-b")[0]["narrative"] == "Brief for user-b"


def test_withdrawal_failure_rolls_back_consent_and_cancellation(engine):
    store, lease = populate(engine)
    with engine.begin() as connection:
        ConsentRepository(connection).save(Consent(user_id="user-a", granted_at=NOW))
    with pytest.raises(RuntimeError, match="later failure"):
        with engine.begin() as connection:
            Manager(repository=ConsentRepository(connection), clock=lambda: NOW,
                    daily_brief_privacy_repository=Privacy(connection)).withdraw(user_id="user-a")
            raise RuntimeError("later failure")
    assert store.is_active(lease, now=NOW)
    with engine.begin() as connection:
        assert Manager(repository=ConsentRepository(connection)).is_permitted(user_id="user-a")


def test_withdrawal_without_active_consent_still_cancels_stale_lease(engine):
    store, lease = populate(engine)
    with engine.begin() as connection:
        manager = Manager(repository=ConsentRepository(connection),
                          daily_brief_privacy_repository=Privacy(connection))
        assert manager.withdraw(user_id="user-a") is None
    assert not store.is_active(lease, now=NOW)


def test_delete_hook_participates_in_account_transaction(engine):
    store, lease = populate(engine)
    user, kwargs, empty = user_and_repositories()
    with engine.connect() as connection:
        users = MagicMock()
        users.delete.side_effect = lambda user_id: connection.execute(
            text("DELETE FROM users WHERE user_id = :id"), {"id": user_id})
        result = Deleter(**kwargs, user_repository=users, invitation_repository=empty,
                         transaction_factory=connection.begin,
                         daily_brief_privacy_repository=Privacy(connection)).execute(user)
        assert result.user_id == "user-a"
    assert store.export_for_user("user-a") == []
    assert not store.complete(lease, narrative="Too late", reason="daily", now=NOW)
    assert len(store.export_for_user("user-b")) == 1


def test_failed_account_delete_rolls_back_daily_brief_deletion(engine):
    store, lease = populate(engine)
    user, kwargs, empty = user_and_repositories()
    users = MagicMock()
    users.delete.side_effect = RuntimeError("delete failed")
    with engine.connect() as connection, pytest.raises(RuntimeError, match="delete failed"):
        Deleter(**kwargs, user_repository=users, invitation_repository=empty,
                transaction_factory=connection.begin,
                daily_brief_privacy_repository=Privacy(connection)).execute(user)
    assert len(store.export_for_user("user-a")) == 1
    assert store.is_active(lease, now=NOW)


def test_delete_requires_owner_before_entering_transaction():
    user, kwargs, empty = user_and_repositories()
    kwargs["athlete_access_repository"].get.side_effect = KeyError("no access")
    privacy, transaction = MagicMock(), MagicMock()
    with pytest.raises(PermissionError):
        Deleter(**kwargs, user_repository=empty, invitation_repository=empty,
                transaction_factory=transaction, daily_brief_privacy_repository=privacy).execute(user)
    transaction.assert_not_called()
    privacy.delete_for_user.assert_not_called()


def test_unmigrated_database_is_empty_without_creating_tables():
    engine = create_engine("sqlite://")
    try:
        with engine.begin() as connection:
            privacy = Privacy(connection)
            assert privacy.export_for_user("user-a", athlete_id="athlete-a") == []
            privacy.cancel_for_user("user-a")
            privacy.delete_for_user("user-a")
            assert not connection.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )).all()
    finally:
        engine.dispose()


@pytest.mark.parametrize("identity", [None, "", " ", 42, "x" * 37])
def test_invalid_identity_rejected_before_database_use(identity):
    engine = create_engine("sqlite://")
    try:
        with engine.connect() as connection, pytest.raises(ValueError):
            Privacy(connection).cancel_for_user(identity)
    finally:
        engine.dispose()


def test_closed_connection_errors_are_not_treated_as_missing_table(engine):
    connection = engine.connect()
    privacy = Privacy(connection)
    connection.close()
    with pytest.raises(Exception):
        privacy.export_for_user("user-a", athlete_id="athlete-a")


def test_application_wires_all_three_privacy_consumers():
    tree = ast.parse((ROOT / "app/app.py").read_text(encoding="utf-8"))
    for name in ("ManageTrainingCoachConsent", "ExportParticipantData", "DeleteParticipantData"):
        calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
                 and isinstance(node.func, ast.Name) and node.func.id == name]
        assert calls
        for call in calls:
            value = next(keyword.value for keyword in call.keywords
                         if keyword.arg == "daily_brief_privacy_repository")
            assert ast.unparse(value) == "repository_bundle.daily_brief_privacy_repository"


def test_factory_keeps_json_without_sql_and_binds_privacy_to_shared_connection():
    path = "performancelab/storage/repository_factory.py"
    tree = ast.parse((ROOT / path).read_text(encoding="utf-8"))
    # Repository constructors unrelated to this change are simple injected fakes.
    dependencies = {alias.name: MagicMock() for node in tree.body
                    if isinstance(node, ast.ImportFrom)
                    and (node.module or "").startswith("performancelab")
                    for alias in node.names}
    class Configuration:
        def __init__(self, local):
            self.uses_json = local
            self.uses_postgresql = not local
            self.database_url = "sqlite://"
    dependencies.update(RuntimeConfiguration=Configuration, DailyBriefPrivacyRepository=Privacy)
    factory = load(path, **dependencies)["build_repository_bundle"]
    no_engine = MagicMock(side_effect=AssertionError("JSON must not create an engine"))
    local = factory(Configuration(True), engine_factory=no_engine)
    assert local.daily_brief_privacy_repository is None
    no_engine.assert_not_called()
    bundle = factory(Configuration(False))
    try:
        assert isinstance(bundle.daily_brief_privacy_repository, Privacy)
        assert bundle.daily_brief_privacy_repository._connection is bundle.connection
    finally:
        bundle.close()
