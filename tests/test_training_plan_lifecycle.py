from datetime import date, datetime

import pytest

from performancelab.training.planning import (
    PlannedWorkout,
    TrainingPlan,
)


def test_training_plan_has_stable_identity():

    first = TrainingPlan()
    second = TrainingPlan()

    assert first.plan_id
    assert second.plan_id
    assert first.plan_id != second.plan_id


def test_training_plan_accepts_complete_horizon():

    plan = TrainingPlan(
        start_date=date(2026, 7, 29),
        end_date=date(2026, 9, 27),
    )

    assert plan.start_date == date(
        2026,
        7,
        29,
    )

    assert plan.end_date == date(
        2026,
        9,
        27,
    )

    assert plan.covers(
        date(2026, 8, 15)
    )


def test_training_plan_requires_both_horizon_dates():

    with pytest.raises(
        ValueError,
        match="both start_date and end_date",
    ):
        TrainingPlan(
            start_date=date(2026, 7, 29),
        )


def test_training_plan_rejects_reversed_horizon():

    with pytest.raises(
        ValueError,
        match="end_date",
    ):
        TrainingPlan(
            start_date=date(2026, 9, 27),
            end_date=date(2026, 7, 29),
        )


def test_training_plan_accepts_workout_inside_horizon():

    plan = TrainingPlan(
        start_date=date(2026, 7, 29),
        end_date=date(2026, 9, 27),
    )

    workout = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            15,
        ),
        sport="Trail Running",
        title="Long Aerobic Run",
    )

    plan.add(workout)

    assert workout in plan


def test_training_plan_rejects_workout_outside_horizon():

    plan = TrainingPlan(
        start_date=date(2026, 7, 29),
        end_date=date(2026, 9, 27),
    )

    workout = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            10,
            1,
        ),
        sport="Trail Running",
    )

    with pytest.raises(
        ValueError,
        match="outside",
    ):
        plan.add(workout)


def test_open_training_plan_remains_backward_compatible():

    plan = TrainingPlan()

    workout = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            10,
            1,
        ),
    )

    plan.add(workout)

    assert workout in plan
    assert plan.start_date is None
    assert plan.end_date is None