"""
PerformanceLab

Training Coach usage repository contract.
"""

from datetime import (
    date,
)
from typing import (
    Protocol,
)

from performancelab.training_coach_usage import (
    TrainingCoachUsageEvent,
)
from performancelab.training_coach_usage_limits import (
    TrainingCoachUsageCounts,
)


class TrainingCoachUsageRepository(
    Protocol
):
    """
    Persistence contract for Training Coach usage.
    """

    def save(
        self,
        event: TrainingCoachUsageEvent,
    ) -> None:
        """
        Save one factual usage event.
        """

        ...

    def counts_for_utc_day(
        self,
        *,
        user_id: str,
        utc_day: date,
    ) -> TrainingCoachUsageCounts:
        """
        Count successful usage for one user and globally.
        """

        ...