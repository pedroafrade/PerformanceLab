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

def test_training_plan_identifies_competition_block():

    plan = TrainingPlan(
        start_date=date(2026, 7, 29),
        end_date=date(2026, 9, 27),
        primary_event_id="trail-pe-firme",
        competition_event_ids=(
            "sealand",
            "trail-pe-firme",
        ),
    )

    assert (
        plan.primary_event_id
        == "trail-pe-firme"
    )

    assert plan.competition_event_ids == (
        "sealand",
        "trail-pe-firme",
    )


def test_primary_event_must_belong_to_competition_block():

    with pytest.raises(
        ValueError,
        match="must belong",
    ):
        TrainingPlan(
            primary_event_id="other-event",
            competition_event_ids=(
                "sealand",
                "trail-pe-firme",
            ),
        )


def test_competition_event_ids_cannot_repeat():

    with pytest.raises(
        ValueError,
        match="duplicates",
    ):
        TrainingPlan(
            primary_event_id="sealand",
            competition_event_ids=(
                "sealand",
                "sealand",
            ),
        )

def test_training_plan_returns_workout_phase():

    plan = TrainingPlan(
        start_date=date(
            2026,
            9,
            7,
        ),
        end_date=date(
            2026,
            9,
            13,
        ),
    )

    plan.add(
        PlannedWorkout(
            scheduled_at=datetime(
                2026,
                9,
                10,
            ),
            title="Quality Run",
            phase="Taper",
        )
    )

    assert (
        plan.phase_on(
            date(
                2026,
                9,
                10,
            )
        )
        == "Taper"
    )


def test_rest_day_inherits_week_phase():

    plan = TrainingPlan(
        start_date=date(
            2026,
            9,
            7,
        ),
        end_date=date(
            2026,
            9,
            13,
        ),
    )

    plan.add(
        PlannedWorkout(
            scheduled_at=datetime(
                2026,
                9,
                10,
            ),
            title="Quality Run",
            phase="Taper",
        )
    )

    assert (
        plan.phase_on(
            date(
                2026,
                9,
                11,
            )
        )
        == "Taper"
    )


def test_race_day_uses_race_phase():

    plan = TrainingPlan(
        start_date=date(
            2026,
            9,
            7,
        ),
        end_date=date(
            2026,
            9,
            13,
        ),
    )

    plan.add(
        PlannedWorkout(
            scheduled_at=datetime(
                2026,
                9,
                13,
            ),
            title="Race",
            intensity="Race effort",
            phase="Taper",
        )
    )

    assert (
        plan.phase_on(
            date(
                2026,
                9,
                13,
            )
        )
        == "Race"
    )


def test_phase_is_none_outside_plan():

    plan = TrainingPlan(
        start_date=date(
            2026,
            9,
            7,
        ),
        end_date=date(
            2026,
            9,
            13,
        ),
    )

    assert (
        plan.phase_on(
            date(
                2026,
                9,
                14,
            )
        )
        is None
    )

def test_only_race_day_uses_race_phase():

    plan = TrainingPlan(
        start_date=date(
            2026,
            9,
            7,
        ),
        end_date=date(
            2026,
            9,
            13,
        ),
    )

    plan.add(
        PlannedWorkout(
            scheduled_at=datetime(
                2026,
                9,
                12,
            ),
            title="Shakeout Run",
            intensity="Very easy",
            phase="Race",
        )
    )

    plan.add(
        PlannedWorkout(
            scheduled_at=datetime(
                2026,
                9,
                13,
            ),
            title="Race",
            intensity="Race effort",
            phase="Race",
        )
    )

    assert (
        plan.phase_on(
            date(
                2026,
                9,
                11,
            )
        )
        == "Taper"
    )

    assert (
        plan.phase_on(
            date(
                2026,
                9,
                12,
            )
        )
        == "Taper"
    )

    assert (
        plan.phase_on(
            date(
                2026,
                9,
                13,
            )
        )
        == "Race"
    )

def test_training_plan_tracks_reconciliation_date():

    plan = TrainingPlan(
        reconciled_through=date(
            2026,
            8,
            5,
        ),
    )

    assert (
        plan.reconciled_through
        == date(
            2026,
            8,
            5,
        )
    )


def test_reconciliation_date_rejects_datetime():

    with pytest.raises(
        TypeError,
        match="reconciled_through",
    ):
        TrainingPlan(
            reconciled_through=datetime(
                2026,
                8,
                5,
                12,
                0,
            ),
        )