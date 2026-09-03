"""Persist Daily Brief metadata without prompts, responses or new quota rules."""

from contextlib import nullcontext
import ast
from datetime import datetime, timezone
import io
import json
from pathlib import Path
from runpy import run_path
from unittest.mock import MagicMock
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine, event, insert, text
from sqlalchemy.exc import IntegrityError

from performancelab.coaching.daily_brief_usage_recorder import DailyBriefUsageRecorder
from performancelab.storage.json_training_coach_usage_repository import JsonTrainingCoachUsageRepository
from performancelab.storage.postgresql_training_coach_usage_repository import PostgreSQLTrainingCoachUsageRepository
from performancelab.storage.postgresql_schema import training_coach_usage, metadata
from performancelab.training_coach_usage import TrainingCoachUsageEvent, TrainingCoachUsageStatus


NOW = datetime(2026, 9, 4, 10, tzinfo=timezone.utc)
ROOT = Path(__file__).resolve().parents[1]


def result(**changes):
    return dict(purpose="daily_brief", provider="google-gemini", model="test-model",
                status="generated", prompt_tokens=100, output_tokens=20, total_tokens=130,
                **changes)


@pytest.fixture(params=["json", "sql"])
def storage(request, tmp_path):
    if request.param == "json":
        yield JsonTrainingCoachUsageRepository(tmp_path / "usage"), nullcontext
        return
    engine = create_engine("sqlite://")
    @event.listens_for(engine, "connect")
    def foreign_keys(connection, _):
        connection.execute("PRAGMA foreign_keys=ON")
    with engine.connect() as connection:
        with connection.begin():
            connection.execute(text("CREATE TABLE users (user_id VARCHAR(36) PRIMARY KEY)"))
            connection.execute(text("INSERT INTO users VALUES ('user-a'), ('user-b')"))
            training_coach_usage.create(connection)
        yield PostgreSQLTrainingCoachUsageRepository(connection), connection.begin
    engine.dispose()


def test_recorder_roundtrip_idempotence_and_owner_isolation(storage):
    repo, transaction = storage
    recorder = DailyBriefUsageRecorder(user_id="user-a", occurred_at=NOW,
                                       usage_id="request-a", repository=repo,
                                       transaction_factory=transaction)
    recorder(result())
    recorder(result())
    with transaction():
        rows = repo.list_for_user("user-a")
        assert len(rows) == 1
        saved = rows[0]
        assert saved.purpose == "daily_brief"
        assert (saved.prompt_tokens, saved.output_tokens, saved.total_tokens) == (100, 20, 130)
        assert saved.occurred_at == NOW
        assert saved.error_code is None
        assert saved.latency_ms is None
        assert repo.list_for_user("user-b") == ()
    changed = result()
    changed["total_tokens"] = 131
    with pytest.raises(ValueError, match="usage_id"):
        recorder(changed)


def test_failure_unknown_tokens_and_existing_allowance_semantics(storage):
    repo, transaction = storage
    recorder = DailyBriefUsageRecorder(user_id="user-a", occurred_at=NOW,
                                       repository=repo, transaction_factory=transaction)
    data = result()
    data.update(status="provider_quota", prompt_tokens=None, output_tokens=None, total_tokens=None)
    recorder(data)
    with transaction():
        row = repo.list_for_user("user-a")[0]
        assert row.status is TrainingCoachUsageStatus.FAILED
        assert row.error_code == "provider_quota"
        assert row.total_tokens is None
        assert not row.counts_toward_limit
        assert repo.counts_for_utc_day(user_id="user-a", utc_day=NOW.date()).global_count == 0


@pytest.mark.parametrize("version", [1, 2])
def test_legacy_json_is_activity_with_unknown_tokens(tmp_path, version):
    path = tmp_path / "legacy.json"
    path.write_text(json.dumps({"version": version, "usage_id": "legacy",
                                "user_id": "user-a", "occurred_at": NOW.isoformat(),
                                "status": "generated"}), encoding="utf-8")
    loaded = JsonTrainingCoachUsageRepository(tmp_path).list()[0]
    assert loaded.purpose == "activity"
    assert loaded.prompt_tokens is loaded.output_tokens is loaded.total_tokens is None


@pytest.mark.parametrize("field", ["prompt_tokens", "output_tokens", "total_tokens"])
@pytest.mark.parametrize("value", [-1, True, 1.5, "10"])
def test_invalid_token_counts_are_rejected(field, value):
    with pytest.raises((TypeError, ValueError)):
        TrainingCoachUsageEvent(user_id="user-a", occurred_at=NOW,
                                status=TrainingCoachUsageStatus.GENERATED, **{field: value})


def test_invalid_purpose_rejected():
    with pytest.raises(ValueError, match="purpose"):
        TrainingCoachUsageEvent(user_id="user-a", occurred_at=NOW,
                                status=TrainingCoachUsageStatus.GENERATED, purpose="other")


@pytest.mark.parametrize("changes", [
    {"user_id": "user-b"}, {"notes": "SECRET"}, {"narrative": "PRIVATE"},
    {"status": "SECRET raw provider exception"}, {"purpose": "activity"},
    {"provider": "other"}, {"total_tokens": True},
])
def test_untrusted_metadata_cannot_select_owner_or_store_text(changes):
    repo, transaction = MagicMock(), MagicMock()
    recorder = DailyBriefUsageRecorder(user_id="user-a", occurred_at=NOW,
                                       repository=repo, transaction_factory=transaction)
    data = result()
    data.update(changes)
    with pytest.raises((TypeError, ValueError)):
        recorder(data)
    repo.save.assert_not_called()
    transaction.assert_not_called()


def test_sql_rollback_and_parent_deletion_cascade(storage):
    repo, transaction = storage
    if not isinstance(repo, PostgreSQLTrainingCoachUsageRepository):
        return
    saved = TrainingCoachUsageEvent(user_id="user-a", occurred_at=NOW, purpose="daily_brief",
                                    status=TrainingCoachUsageStatus.GENERATED, total_tokens=10)
    with pytest.raises(RuntimeError):
        with transaction():
            repo.save(saved)
            raise RuntimeError("rollback")
    with transaction():
        assert repo.list_for_user("user-a") == ()
        repo.save(saved)
    with transaction():
        repo._connection.execute(text("DELETE FROM users WHERE user_id = 'user-a'"))
        assert repo.list_for_user("user-a") == ()


def test_sql_defaults_and_constraints(storage):
    repo, transaction = storage
    if not isinstance(repo, PostgreSQLTrainingCoachUsageRepository):
        return
    values = dict(user_id="user-a", usage_id="old", occurred_at=NOW, status="generated")
    with transaction():
        repo._connection.execute(insert(training_coach_usage).values(**values))
        row = repo.list_for_user("user-a")[0]
        assert row.purpose == "activity" and row.total_tokens is None
    with pytest.raises(IntegrityError), transaction():
        repo._connection.execute(insert(training_coach_usage).values(
            **dict(values, usage_id="bad", prompt_tokens=-1)))


def test_postgresql_migration_sql_matches_metadata_constraint_names():
    from alembic.migration import MigrationContext
    from alembic.operations import Operations
    migration = run_path(str(ROOT / "migrations/versions/20260904_02_training_coach_usage_metadata.py"))
    assert migration["down_revision"] == "20260904_01"
    for direction in ("upgrade", "downgrade"):
        output = io.StringIO()
        context = MigrationContext.configure(dialect_name="postgresql", opts={
            "as_sql": True, "output_buffer": output, "target_metadata": metadata,
        })
        with Operations.context(context):
            migration[direction]()
        sql = output.getvalue()
        assert "ck_training_coach_usage_ck_" not in sql
        for name in ("purpose", "prompt_tokens_nonnegative", "output_tokens_nonnegative", "total_tokens_nonnegative"):
            assert "ck_training_coach_usage_" + name in sql
        if direction == "upgrade":
            assert "DEFAULT 'activity' NOT NULL" in sql
            assert "DROP TABLE" not in sql


def test_export_service_includes_actual_usage_metadata():
    # Exercise the production export service without importing unrelated athlete
    # analytics/provider packages. Only the athlete serializer is substituted.
    class Authorization:
        def require_access(self, **kwargs):
            assert kwargs == dict(user_id="user-a", athlete_id="athlete-a",
                                  allowed_permissions=("owner",))
    path = ROOT / "performancelab/application/export_participant_data.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    tree.body = [node for node in tree.body if not (isinstance(node, ast.ImportFrom)
                 and (node.module or "").startswith("performancelab"))]
    scope = dict(__name__=__name__, AthleteAuthorizationService=Authorization,
                 User=SimpleNamespace, athlete_to_dict=lambda athlete: {"id": "athlete-a"})
    exec(compile(tree, str(path), "exec"), scope)
    empty, usage = MagicMock(), MagicMock()
    empty.list.return_value = []
    empty.list_for_user.return_value = []
    usage.list_for_user.return_value = [TrainingCoachUsageEvent(
        user_id="user-a", occurred_at=NOW, status=TrainingCoachUsageStatus.GENERATED,
        purpose="daily_brief", prompt_tokens=100, output_tokens=20, total_tokens=130,
    )]
    exporter = scope["ExportParticipantData"](
        athlete_repository=empty, external_identity_repository=empty,
        athlete_access_repository=empty, alpha_participation_consent_repository=empty,
        training_coach_consent_repository=empty, training_coach_usage_repository=usage,
        authorization=Authorization(),
    )
    user = SimpleNamespace(user_id="user-a", athlete_id="athlete-a", email="a@example.com",
                           role="athlete", is_athlete=True)
    data = json.loads(exporter.execute(user, generated_at=NOW).to_json())
    row = data["training_coach_usage"][0]
    assert row["purpose"] == "daily_brief"
    assert (row["prompt_tokens"], row["output_tokens"], row["total_tokens"]) == (100, 20, 130)
    usage.list_for_user.assert_called_once_with("user-a")
