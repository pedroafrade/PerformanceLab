"""
PerformanceLab

Configurable Training Coach usage limits.
"""

from dataclasses import (
    dataclass,
)


def _validated_count(
    value,
    *,
    field_name: str,
) -> int:
    """
    Require a non-negative integer count.
    """

    if (
        not isinstance(
            value,
            int,
        )
        or isinstance(
            value,
            bool,
        )
    ):

        raise TypeError(
            f"{field_name} must be an integer."
        )

    if value < 0:

        raise ValueError(
            f"{field_name} cannot be negative."
        )

    return value


def _validated_limit(
    value,
    *,
    field_name: str,
) -> int:
    """
    Require a positive integer limit.
    """

    value = _validated_count(
        value,
        field_name=field_name,
    )

    if value == 0:

        raise ValueError(
            f"{field_name} must be greater than zero."
        )

    return value


@dataclass(
    frozen=True
)
class TrainingCoachUsageCounts:
    """
    Factual request counts for the current UTC day.
    """

    user_count: int
    global_count: int

    def __post_init__(
        self,
    ) -> None:

        object.__setattr__(
            self,
            "user_count",
            _validated_count(
                self.user_count,
                field_name="user_count",
            ),
        )

        object.__setattr__(
            self,
            "global_count",
            _validated_count(
                self.global_count,
                field_name="global_count",
            ),
        )


@dataclass(
    frozen=True
)
class TrainingCoachUsageDecision:
    """
    Immutable result of checking the daily limits.
    """

    permitted: bool
    reason: str | None
    remaining_user_requests: int
    remaining_global_requests: int


@dataclass(
    frozen=True
)
class TrainingCoachUsageLimits:
    """
    Daily Training Coach request limits.

    The values will later be supplied by the runtime
    configuration instead of being fixed in the UI.
    """

    user_daily_limit: int
    global_daily_limit: int

    def __post_init__(
        self,
    ) -> None:

        user_daily_limit = (
            _validated_limit(
                self.user_daily_limit,
                field_name=(
                    "user_daily_limit"
                ),
            )
        )

        global_daily_limit = (
            _validated_limit(
                self.global_daily_limit,
                field_name=(
                    "global_daily_limit"
                ),
            )
        )

        if (
            user_daily_limit
            > global_daily_limit
        ):

            raise ValueError(
                "user_daily_limit cannot exceed "
                "global_daily_limit."
            )

        object.__setattr__(
            self,
            "user_daily_limit",
            user_daily_limit,
        )

        object.__setattr__(
            self,
            "global_daily_limit",
            global_daily_limit,
        )

    def evaluate(
        self,
        counts: TrainingCoachUsageCounts,
    ) -> TrainingCoachUsageDecision:
        """
        Decide whether another request can be started.
        """

        if not isinstance(
            counts,
            TrainingCoachUsageCounts,
        ):

            raise TypeError(
                "counts must be "
                "TrainingCoachUsageCounts."
            )

        remaining_user = max(
            self.user_daily_limit
            - counts.user_count,
            0,
        )

        remaining_global = max(
            self.global_daily_limit
            - counts.global_count,
            0,
        )

        if remaining_user == 0:

            return TrainingCoachUsageDecision(
                permitted=False,
                reason="user_daily_limit",
                remaining_user_requests=0,
                remaining_global_requests=(
                    remaining_global
                ),
            )

        if remaining_global == 0:

            return TrainingCoachUsageDecision(
                permitted=False,
                reason="global_daily_limit",
                remaining_user_requests=(
                    remaining_user
                ),
                remaining_global_requests=0,
            )

        return TrainingCoachUsageDecision(
            permitted=True,
            reason=None,
            remaining_user_requests=(
                remaining_user
            ),
            remaining_global_requests=(
                remaining_global
            ),
        )