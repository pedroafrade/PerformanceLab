from dataclasses import replace
from datetime import date, datetime, timedelta

import pytest

from performancelab import Athlete
from performancelab.application import ApplyPlanBuilderDraft
from performancelab.training.planning import (
    PlannedWorkout,
    PlanBuilderDraft,
    TrainingPlan,
    TrainingPlanRevision,
)


class Repository:
    def __init__(self, athlete, *, fail=False):
        self.athlete = athlete
        self.fail = fail
        self.saved = 0

    def get(self, athlete_id):
        return self.athlete

    def save(self, athlete):
        if self.fail:
            raise RuntimeError("storage unavailable")
        self.saved += 1


def workout(day, title):
    return PlannedWorkout(
        scheduled_at=datetime(2026, 9, day, 8),
        sport="Running",
        title=title,
        duration=timedelta(minutes=45),
    )


def athlete_with_plan():
    original = workout(11, "Hill Reps")
    revision = TrainingPlanRevision(
        revision_id="active",
        created_on=date(2026, 9, 9),
        source="generated",
        workouts=(original,),
    )
    athlete = Athlete(name="Pedro")
    athlete.training_plan = TrainingPlan(
        plan_id="plan-1",
        workouts=[original],
        revisions=(revision,),
        active_revision_id="active",
    )
    return athlete


def test_applies_a_complete_edit_flow_once():
    athlete = athlete_with_plan()
    draft = PlanBuilderDraft.from_plan(athlete.training_plan)
    original = draft.workouts[0]
    draft = draft.move_workout_id(
        workout_id=original.planned_workout_id,
        target_day=date(2026, 9, 12),
    )
    draft = draft.update_workout(
        workout_id=original.planned_workout_id,
        title="Hill Reps Short",
        duration_minutes=35,
        distance=6.0,
        elevation_gain=250.0,
        intensity="Hard",
        prescription_summary="6 x 60 s",
        objective="Climbing power",
        structure=("Warm up", "6 x 60 s", "Cool down"),
    )
    draft = draft.add_workout(
        template=workout(15, "Easy Run"),
        workout_day=date(2026, 9, 14),
    )
    removable = workout(16, "Recovery Run")
    draft = draft.add_workout(
        template=removable,
        workout_day=date(2026, 9, 16),
    )
    added_recovery = next(
        item for item in draft.workouts if item.title == "Recovery Run"
    )
    draft = draft.delete_workout(
        workout_id=added_recovery.planned_workout_id
    )
    repository = Repository(athlete)

    result = ApplyPlanBuilderDraft(repository=repository).execute(
        athlete.athlete_id, draft, today=date(2026, 9, 10)
    )

    assert result.changed is True
    assert repository.saved == 1
    assert len(result.athlete.training_plan.workouts) == 2
    assert result.athlete.training_plan.workouts[0].day == date(2026, 9, 12)
    assert result.athlete.training_plan.revisions[-1].workouts == draft.workouts
    assert result.active_revision_id == result.athlete.training_plan.active_revision_id


def test_rejects_stale_draft_without_saving():
    athlete = athlete_with_plan()
    draft = replace(
        PlanBuilderDraft.from_plan(athlete.training_plan),
        source_revision_id="older",
    )
    repository = Repository(athlete)

    with pytest.raises(ValueError, match="active plan changed"):
        ApplyPlanBuilderDraft(repository=repository).execute(
            athlete.athlete_id, draft
        )

    assert repository.saved == 0
    assert athlete.training_plan.active_revision_id == "active"


def test_duplicate_draft_is_idempotent():
    athlete = athlete_with_plan()
    draft = PlanBuilderDraft.from_plan(athlete.training_plan)
    repository = Repository(athlete)

    result = ApplyPlanBuilderDraft(repository=repository).execute(
        athlete.athlete_id, draft
    )

    assert result.changed is False
    assert repository.saved == 0
    assert len(athlete.training_plan.revisions) == 1


def test_storage_failure_restores_active_plan():
    athlete = athlete_with_plan()
    original_plan = athlete.training_plan
    original = original_plan.workouts[0]
    draft = PlanBuilderDraft.from_plan(original_plan).move_workout_id(
        workout_id=original.planned_workout_id,
        target_day=date(2026, 9, 12),
    )

    with pytest.raises(RuntimeError, match="storage unavailable"):
        ApplyPlanBuilderDraft(
            repository=Repository(athlete, fail=True)
        ).execute(athlete.athlete_id, draft)

    assert athlete.training_plan is original_plan
    assert athlete.training_plan.active_revision_id == "active"
