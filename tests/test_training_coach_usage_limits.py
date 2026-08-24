import pytest

from performancelab.training_coach_usage_limits import (
    TrainingCoachUsageCounts,
    TrainingCoachUsageLimits,
)


def test_permits_request_below_both_limits():

    limits = TrainingCoachUsageLimits(
        user_daily_limit=5,
        global_daily_limit=50,
    )

    decision = limits.evaluate(
        TrainingCoachUsageCounts(
            user_count=2,
            global_count=20,
        )
    )

    assert decision.permitted is True
    assert decision.reason is None

    assert (
        decision.remaining_user_requests
        == 3
    )

    assert (
        decision.remaining_global_requests
        == 30
    )


def test_blocks_request_at_user_limit():

    limits = TrainingCoachUsageLimits(
        user_daily_limit=5,
        global_daily_limit=50,
    )

    decision = limits.evaluate(
        TrainingCoachUsageCounts(
            user_count=5,
            global_count=20,
        )
    )

    assert decision.permitted is False

    assert (
        decision.reason
        == "user_daily_limit"
    )

    assert (
        decision.remaining_user_requests
        == 0
    )


def test_blocks_request_at_global_limit():

    limits = TrainingCoachUsageLimits(
        user_daily_limit=5,
        global_daily_limit=50,
    )

    decision = limits.evaluate(
        TrainingCoachUsageCounts(
            user_count=2,
            global_count=50,
        )
    )

    assert decision.permitted is False

    assert (
        decision.reason
        == "global_daily_limit"
    )

    assert (
        decision.remaining_global_requests
        == 0
    )


def test_rejects_negative_usage_counts():

    with pytest.raises(
        ValueError,
        match="cannot be negative",
    ):

        TrainingCoachUsageCounts(
            user_count=-1,
            global_count=0,
        )


def test_rejects_zero_daily_limit():

    with pytest.raises(
        ValueError,
        match="greater than zero",
    ):

        TrainingCoachUsageLimits(
            user_daily_limit=0,
            global_daily_limit=50,
        )


def test_rejects_user_limit_above_global_limit():

    with pytest.raises(
        ValueError,
        match="cannot exceed",
    ):

        TrainingCoachUsageLimits(
            user_daily_limit=60,
            global_daily_limit=50,
        )