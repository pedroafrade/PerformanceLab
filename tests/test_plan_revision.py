from datetime import date, datetime, timedelta

import pytest

from performancelab.training.planning import (
    PlannedWorkout,
    TrainingPlan,
    TrainingPlanRevision,
    ensure_plan_revision_history,
)


def workout(day: int) -> PlannedWorkout:
    return PlannedWorkout(
        scheduled_at=datetime(2026, 9, day, 8),
        sport="Running",
        title="Easy Run",
        duration=timedelta(minutes=45),
    )


def test_training_plan_accepts_recoverable_revisions():
    revision = TrainingPlanRevision(
        revision_id="revision-1",
        created_on=date(2026, 9, 1),
        source="generated",
        workouts=(workout(1),),
    )

    plan = TrainingPlan(
        revisions=(revision,),
        active_revision_id="revision-1",
        workouts=list(revision.workouts),
    )

    assert plan.revisions == (revision,)
    assert plan.active_revision_id == "revision-1"


def test_training_plan_rejects_unknown_active_revision():
    with pytest.raises(
        ValueError,
        match="active_revision_id",
    ):
        TrainingPlan(active_revision_id="missing")


def test_backfills_legacy_original_and_current_revisions():
    original = workout(1)
    adapted = PlannedWorkout(
        scheduled_at=original.scheduled_at,
        sport="Running",
        title="Hill Reps",
        duration=timedelta(minutes=45),
    )
    plan = TrainingPlan(
        plan_id="legacy-plan",
        start_date=date(2026, 9, 1),
        end_date=date(2026, 9, 8),
        original_workouts=(original,),
        workouts=[adapted],
    )

    migrated = ensure_plan_revision_history(plan)
    repeated = ensure_plan_revision_history(plan)

    assert len(migrated.revisions) == 2
    assert migrated.revisions[0].workouts == (original,)
    assert migrated.revisions[1].workouts == (adapted,)
    assert migrated.active_revision_id == migrated.revisions[1].revision_id
    assert (
        migrated.revisions[0].revision_id
        == repeated.revisions[0].revision_id
    )
