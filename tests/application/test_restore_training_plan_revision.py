from datetime import date, datetime, timedelta

import pytest

from performancelab import Athlete
from performancelab.application import RestoreTrainingPlanRevision
from performancelab.training.planning import (
    PlannedWorkout,
    TrainingPlan,
    TrainingPlanRevision,
)


class Repository:
    def __init__(self, athlete):
        self.athlete = athlete
        self.saved = []

    def get(self, athlete_id):
        return self.athlete

    def save(self, athlete):
        self.saved.append(athlete)


def session(title):
    return PlannedWorkout(
        scheduled_at=datetime(2026, 9, 8, 8),
        sport="Running",
        title=title,
        duration=timedelta(minutes=45),
    )


def test_restores_revision_without_deleting_current_version():
    original = TrainingPlanRevision(
        revision_id="original",
        created_on=date(2026, 9, 1),
        source="generated",
        workouts=(session("Tempo Run"),),
    )
    adapted = TrainingPlanRevision(
        revision_id="adapted",
        created_on=date(2026, 9, 7),
        source="automatic_adaptation",
        workouts=(session("Hill Reps"),),
        parent_revision_id="original",
    )
    athlete = Athlete(name="Pedro")
    athlete.training_plan = TrainingPlan(
        revisions=(original, adapted),
        active_revision_id="adapted",
        workouts=list(adapted.workouts),
    )
    repository = Repository(athlete)

    result = RestoreTrainingPlanRevision(
        repository=repository
    ).execute(
        athlete.athlete_id,
        "original",
        today=date(2026, 9, 8),
    )

    assert result.athlete.training_plan.workouts[0].title == "Tempo Run"
    assert len(result.athlete.training_plan.revisions) == 3
    assert result.athlete.training_plan.revisions[-1].source == "recovery"
    assert repository.saved == [athlete]


def test_rejects_unknown_revision():
    athlete = Athlete(name="Pedro")
    repository = Repository(athlete)

    with pytest.raises(LookupError, match="was not found"):
        RestoreTrainingPlanRevision(
            repository=repository
        ).execute(athlete.athlete_id, "missing")
