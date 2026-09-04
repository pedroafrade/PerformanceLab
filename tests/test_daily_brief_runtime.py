from datetime import datetime, timezone
from types import SimpleNamespace

from sqlalchemy import create_engine, insert, select
from sqlalchemy.pool import StaticPool

from performancelab.application.daily_brief_runtime import (
    build_daily_brief_generation_service,
)
from performancelab.storage.postgresql_schema import (
    training_coach_quota_reservations,
    training_coach_usage,
    users,
)
from performancelab.training_coach_usage_limits import TrainingCoachUsageLimits


NOW = datetime(2026, 9, 4, 10, tzinfo=timezone.utc)


class Provider:
    provider_name = "fake"
    model_name = "fake-model"
    calls = 0

    def __init__(self, *, record_usage):
        self.record_usage = record_usage

    def __call__(self, context):
        type(self).calls += 1
        self.record_usage({
            "purpose": "daily_brief",
            "provider": self.provider_name,
            "model": self.model_name,
            "status": "generated",
            "prompt_tokens": 12,
            "output_tokens": 8,
            "total_tokens": 20,
        })
        return "Daily guidance."


def limits():
    return TrainingCoachUsageLimits(
        user_daily_limit=3,
        global_daily_limit=8,
    )


def test_local_runtime_does_not_construct_daily_brief_dependencies():
    service = build_daily_brief_generation_service(
        repository_bundle=SimpleNamespace(
            uses_postgresql=False,
            engine=None,
        ),
        usage_limits=limits(),
        provider_type=Provider,
        clock=lambda: NOW,
    )

    assert service is None
    assert Provider.calls == 0


def test_postgresql_composition_persists_usage_in_short_transaction():
    Provider.calls = 0
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    users.create(engine)
    training_coach_usage.create(engine)
    training_coach_quota_reservations.create(engine)
    with engine.begin() as connection:
        connection.execute(insert(users).values(
            user_id="user-1",
            email="athlete@example.test",
            role="athlete",
        ))

    service = build_daily_brief_generation_service(
        repository_bundle=SimpleNamespace(
            uses_postgresql=True,
            engine=engine,
        ),
        usage_limits=limits(),
        provider_type=Provider,
        clock=lambda: NOW,
    )
    result = service.generate(
        user_id="user-1",
        context=object(),
        can_dispatch=lambda: True,
    )

    assert result.status == "generated"
    assert Provider.calls == 1
    with engine.connect() as connection:
        usage = connection.execute(select(training_coach_usage)).mappings().one()
        reservation = connection.execute(
            select(training_coach_quota_reservations)
        ).mappings().one()
    assert usage["usage_id"] == reservation["request_id"]
    assert usage["purpose"] == "daily_brief"
    assert usage["total_tokens"] == 20
    assert reservation["state"] == "generated"


def test_building_service_alone_never_contacts_provider():
    Provider.calls = 0
    engine = create_engine("sqlite+pysqlite:///:memory:")

    service = build_daily_brief_generation_service(
        repository_bundle=SimpleNamespace(
            uses_postgresql=True,
            engine=engine,
        ),
        usage_limits=limits(),
        provider_type=Provider,
        clock=lambda: NOW,
    )

    assert service is not None
    assert Provider.calls == 0
