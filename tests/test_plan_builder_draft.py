from datetime import date, datetime, timedelta

import pytest

from performancelab.training.planning import (
    PlannedWorkout,
    PlanBuilderDraft,
    TrainingPlan,
)


def workout(
    day: int,
    title: str,
) -> PlannedWorkout:

    return PlannedWorkout(
        scheduled_at=datetime(
            2026,
            9,
            day,
            8,
        ),
        sport="Running",
        title=title,
        duration=timedelta(
            minutes=45,
        ),
    )


def test_creates_isolated_draft_from_plan():

    planned = workout(
        8,
        "Tempo Run",
    )

    plan = TrainingPlan(
        plan_id="plan-1",
        workouts=[
            planned,
        ],
    )

    draft = (
        PlanBuilderDraft.from_plan(
            plan
        )
    )

    assert draft.workouts == (
        planned,
    )

    assert draft.has_changes is False


def test_moves_workout_to_empty_day():

    draft = PlanBuilderDraft(
        source_plan_id="plan-1",
        source_revision_id=None,
        workouts=(
            workout(
                8,
                "Tempo Run",
            ),
        ),
        baseline_workouts=(
            workout(
                8,
                "Tempo Run",
            ),
        ),
    )

    moved = draft.move_workout(
        source_day=date(
            2026,
            9,
            8,
        ),
        target_day=date(
            2026,
            9,
            9,
        ),
    )

    assert moved.workouts[0].day == date(
        2026,
        9,
        9,
    )

    assert moved.has_changes is True


def test_swaps_two_workouts():

    tempo = workout(
        8,
        "Tempo Run",
    )

    easy = workout(
        9,
        "Easy Run",
    )

    draft = PlanBuilderDraft(
        source_plan_id="plan-1",
        source_revision_id=None,
        workouts=(
            tempo,
            easy,
        ),
        baseline_workouts=(
            tempo,
            easy,
        ),
    )

    moved = draft.move_workout(
        source_day=date(
            2026,
            9,
            8,
        ),
        target_day=date(
            2026,
            9,
            9,
        ),
    )

    assert (
        moved.workouts[0].title
        == "Easy Run"
    )

    assert (
        moved.workouts[1].title
        == "Tempo Run"
    )


def test_deletes_and_resets_workout():

    planned = workout(
        8,
        "Tempo Run",
    )

    draft = PlanBuilderDraft(
        source_plan_id="plan-1",
        source_revision_id=None,
        workouts=(
            planned,
        ),
        baseline_workouts=(
            planned,
        ),
    )

    deleted = draft.delete_workout(
        workout_day=date(
            2026,
            9,
            8,
        ),
    )

    assert deleted.workouts == ()
    assert deleted.has_changes is True

    reset = deleted.reset()

    assert reset.workouts == (
        planned,
    )

    assert reset.has_changes is False


def test_rejects_duplicate_target_day():

    draft = PlanBuilderDraft(
        source_plan_id="plan-1",
        source_revision_id=None,
        workouts=(
            workout(
                8,
                "Tempo Run",
            ),
        ),
        baseline_workouts=(),
    )

    with pytest.raises(
        ValueError,
        match="already contains",
    ):
        draft.add_workout(
            template=workout(
                10,
                "Easy Run",
            ),
            workout_day=date(
                2026,
                9,
                8,
            ),
        )


def test_planned_workout_identity_survives_move():

    planned = workout(
        8,
        "Tempo Run",
    )

    draft = PlanBuilderDraft(
        source_plan_id="plan-1",
        source_revision_id=None,
        workouts=(planned,),
        baseline_workouts=(planned,),
    )

    moved = draft.move_workout(
        source_day=date(2026, 9, 8),
        target_day=date(2026, 9, 9),
    )

    assert (
        moved.workouts[0].planned_workout_id
        == planned.planned_workout_id
    )


def test_edits_and_deletes_one_identified_session():
    first = workout(8, "Tempo Run")
    second = workout(8, "Easy Run")
    draft = PlanBuilderDraft(
        source_plan_id="plan-1",
        source_revision_id=None,
        workouts=(first, second),
        baseline_workouts=(first, second),
    )

    edited = draft.update_workout(
        workout_id=first.planned_workout_id,
        title="Tempo Reps",
        duration_minutes=55,
        distance=9.5,
        elevation_gain=120,
        intensity="Z4",
        prescription_summary="4 x 8 min",
        objective="Threshold",
        structure=("Warm up", "4 x 8 min", "Cool down"),
    )
    assert edited.workouts[0].title == "Tempo Reps"
    assert edited.workouts[1] == second

    deleted = edited.delete_workout(
        workout_id=first.planned_workout_id,
    )
    assert deleted.workouts == (second,)


def test_adds_a_second_session_to_an_occupied_day():
    first = workout(8, "Tempo Run")
    template = workout(10, "Easy Run")
    draft = PlanBuilderDraft(
        source_plan_id="plan-1",
        source_revision_id=None,
        workouts=(first,),
        baseline_workouts=(first, template),
    )

    added = draft.add_workout(
        template=template,
        workout_day=date(2026, 9, 8),
        allow_occupied=True,
    )
    assert len(added.workouts) == 2
    assert added.workouts[1].planned_workout_id != template.planned_workout_id
