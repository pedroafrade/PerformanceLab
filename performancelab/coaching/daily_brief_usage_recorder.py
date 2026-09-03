"""Bind provider metadata to one authorised Daily Brief request's usage record.

Construct per request, after coordinator authorisation. Never reuse a recorder
for different requests or accept user_id/usage_id from provider output. This
records a result; it does NOT reserve quota or authorise a provider call.
"""

from collections.abc import Mapping
from datetime import datetime
from uuid import uuid4

from performancelab.training_coach_usage import TrainingCoachUsageEvent, TrainingCoachUsageStatus


_FIELDS = frozenset(("purpose", "provider", "model", "status",
                     "prompt_tokens", "output_tokens", "total_tokens"))
_STATUSES = frozenset(("generated", "provider_configuration", "provider_authentication",
                      "provider_quota", "provider_request", "provider_safety",
                      "provider_unavailable", "provider_response", "provider_incomplete_or_blocked"))


class DailyBriefUsageRecorder:
    def __init__(self, *, user_id: str, occurred_at: datetime, repository,
                 transaction_factory, usage_id: str | None = None):
        if not callable(transaction_factory):
            raise TypeError("transaction_factory must be callable")
        if not callable(getattr(repository, "save", None)):
            raise TypeError("A usage repository is required")
        # Validate identity/time immediately, before any possible provider work.
        identity = TrainingCoachUsageEvent(
            user_id=user_id, occurred_at=occurred_at, purpose="daily_brief",
            usage_id=str(uuid4()) if usage_id is None else usage_id,
            status=TrainingCoachUsageStatus.FAILED,
        )
        self._identity = identity
        self._repository = repository
        self._transaction_factory = transaction_factory

    def __call__(self, metadata: Mapping) -> None:
        if not isinstance(metadata, Mapping) or set(metadata) != _FIELDS:
            raise ValueError("Unexpected Daily Brief usage metadata fields")
        status = metadata["status"]
        if not isinstance(status, str) or status not in _STATUSES:
            raise ValueError("Unexpected Daily Brief usage status")
        if metadata["purpose"] != "daily_brief" or metadata["provider"] != "google-gemini":
            raise ValueError("Unexpected Daily Brief provider or purpose")
        model = metadata["model"]
        if not isinstance(model, str) or not model.strip() or len(model) > 200:
            raise ValueError("Invalid Daily Brief model")
        event = TrainingCoachUsageEvent(
            user_id=self._identity.user_id, usage_id=self._identity.usage_id,
            occurred_at=self._identity.occurred_at, purpose="daily_brief",
            status=(TrainingCoachUsageStatus.GENERATED if status == "generated"
                    else TrainingCoachUsageStatus.FAILED),
            provider="google-gemini", model=model,
            error_code=None if status == "generated" else status,
            prompt_tokens=metadata["prompt_tokens"], output_tokens=metadata["output_tokens"],
            total_tokens=metadata["total_tokens"],
        )
        # Keep identical callback retries idempotent using the same usage_id.
        # A different result for the same ID remains an error in both stores.
        with self._transaction_factory():
            self._repository.save(event)
