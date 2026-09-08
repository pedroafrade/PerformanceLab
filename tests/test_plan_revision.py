from datetime import date, datetime, timedelta

import pytest

from performancelab.training.planning import (
    PlannedWorkout,
    TrainingPlan,
    TrainingPlanRevision,
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
