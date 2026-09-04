"""Build the dormant PostgreSQL Daily Brief generation dependencies.

Constructing this service does not generate a Daily Brief and does not enable
the feature.  Login/Dashboard integration must remain behind a separate,
explicitly disabled-by-default runtime setting.
"""

from datetime import datetime, timezone

from performancelab.coaching.quota_limited_daily_brief_generation import (
    QuotaLimitedDailyBriefGeneration,
)
from performancelab.storage.training_coach_quota_store import (
    TrainingCoachQuotaStore,
)
from performancelab.storage.transactional_training_coach_usage_writer import (
    TransactionalTrainingCoachUsageWriter,
)


def _utc_now():
    return datetime.now(timezone.utc)


def build_daily_brief_generation_service(
    *,
    repository_bundle,
    usage_limits,
    provider_type=None,
    clock=_utc_now,
):
    """Return a configured service only for a PostgreSQL repository bundle."""

    if not getattr(repository_bundle, "uses_postgresql", False):
        return None
    engine = getattr(repository_bundle, "engine", None)
    if engine is None:
        raise RuntimeError("PostgreSQL Daily Brief requires a database engine")
    if provider_type is None:
        from performancelab.integrations.gemini_daily_brief import (
            GeminiDailyBriefProvider,
        )
        provider_type = GeminiDailyBriefProvider

    def provider_factory(*, record_usage):
        return provider_type(record_usage=record_usage)

    return QuotaLimitedDailyBriefGeneration(
        quota_store=TrainingCoachQuotaStore(engine),
        usage_repository=TransactionalTrainingCoachUsageWriter(engine),
        usage_limits=usage_limits,
        provider_factory=provider_factory,
        clock=clock,
    )
