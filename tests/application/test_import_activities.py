from datetime import (
    datetime,
    timedelta,
)

import pytest

from performancelab.application import (
    ImportActivities,
)
from performancelab.athlete import (
    Athlete,
)
from performancelab.storage.in_memory_athlete_repository import (
    InMemoryAthleteRepository,
)
from performancelab.training.planning import (
    TrainingPlan,
)
from performancelab.workout import (
    Workout,
)


class RecordingAthleteRepository(
    InMemoryAthleteRepository
):

    def __init__(
        self,
        athletes=(),
    ) -> None:

        self.save_calls = 0

        super().__init__(
            athletes
        )

        self.save_calls = 0

    def save(
        self,
        athlete,
    ) -> None:

        self.save_calls += 1

        super().save(
            athlete
        )


class FakeReconciler:

    def __init__(
        self,
        *,
        replacement_plan=None,
        error=None,
    ) -> None:

        self.replacement_plan = (
            replacement_plan
        )
        self.error = error
        self.call = None

    def reconcile(
        self,
        *,
        plan,
        history,
        training_state,
        through_day,
    ):

        self.call = {
            "plan": plan,
            "history": history,
            "training_state": (
                training_state
            ),
            "through_day": (
                through_day
            ),
        }

        if self.error is not None:
            raise self.error

        return (
            self.replacement_plan
            if self.replacement_plan
            is not None
            else plan
        )


def workout(
    *,
    workout_id,
    day,
    title="Morning Run",
):

    activity = Workout(
        workout_id=workout_id
    )

    activity.info.title = title
    activity.info.sport = "Running"
    activity.info.date = day
    activity.info.duration = timedelta(
        minutes=60
    )
    activity.info.distance = 10.0

    return activity


def test_empty_import_does_not_save():

    athlete = Athlete(
        name="Pedro"
    )

    repository = (
        RecordingAthleteRepository(
            (
                athlete,
            )
        )
    )

    result = ImportActivities(
        repository=repository,
        reconciler=FakeReconciler(),
    ).execute(
        athlete.athlete_id,
        (),
    )

    assert result.changed is False
    assert result.added_count == 0
    assert result.updated_count == 0
    assert result.duplicate_count == 0
    assert result.outcomes == ()
    assert (
        result.reconciled_through
        is None
    )
    assert repository.save_calls == 0


def test_adds_activity_and_saves_once():

    athlete = Athlete(
        name="Pedro"
    )

    repository = (
        RecordingAthleteRepository(
            (
                athlete,
            )
        )
    )

    activity = workout(
        workout_id="activity-1",
        day=datetime(
            2026,
            8,
            10,
            8,
            0,
        ),
    )

    result = ImportActivities(
        repository=repository,
        reconciler=FakeReconciler(),
    ).execute(
        athlete.athlete_id,
        (
            activity,
        ),
    )

    stored = repository.get(
        athlete.athlete_id
    )

    assert result.changed is True
    assert result.added_count == 1
    assert result.updated_count == 0
    assert result.duplicate_count == 0

    assert len(
        result.outcomes
    ) == 1

    assert (
        result.outcomes[0].workout_id
        == "activity-1"
    )

    assert (
        result.outcomes[0].status
        == "imported"
    )
    assert len(stored.history) == 1
    assert repository.save_calls == 1


def test_matching_activity_counts_as_updated():

    existing = workout(
        workout_id="existing",
        day=datetime(
            2026,
            8,
            10,
            8,
            0,
        ),
        title="10",
    )

    athlete = Athlete(
        name="Pedro"
    )
    athlete.history.add(
        existing
    )

    imported = workout(
        workout_id="imported",
        day=datetime(
            2026,
            8,
            10,
            8,
            2,
        ),
        title="Morning Run",
    )

    repository = (
        RecordingAthleteRepository(
            (
                athlete,
            )
        )
    )

    result = ImportActivities(
        repository=repository,
        reconciler=FakeReconciler(),
    ).execute(
        athlete.athlete_id,
        (
            imported,
        ),
    )

    stored = repository.get(
        athlete.athlete_id
    )

    assert result.added_count == 0
    assert result.updated_count == 1
    assert result.duplicate_count == 0

    assert (
        result.outcomes[0].status
        == "updated"
    )
    assert len(stored.history) == 1
    assert (
        stored.history[0].info.title
        == "Morning Run"
    )
    assert repository.save_calls == 1


def test_reconciles_through_latest_activity_day():

    athlete = Athlete(
        name="Pedro"
    )

    replacement_plan = (
        TrainingPlan(
            plan_id="adapted-plan"
        )
    )

    reconciler = FakeReconciler(
        replacement_plan=(
            replacement_plan
        )
    )

    repository = (
        RecordingAthleteRepository(
            (
                athlete,
            )
        )
    )

    earlier = workout(
        workout_id="earlier",
        day=datetime(
            2026,
            8,
            8,
            8,
            0,
        ),
    )
    later = workout(
        workout_id="later",
        day=datetime(
            2026,
            8,
            12,
            8,
            0,
        ),
    )

    result = ImportActivities(
        repository=repository,
        reconciler=reconciler,
    ).execute(
        athlete.athlete_id,
        (
            later,
            earlier,
        ),
    )

    stored = repository.get(
        athlete.athlete_id
    )

    assert (
        result.reconciled_through.isoformat()
        == "2026-08-12"
    )
    assert (
        reconciler.call[
            "through_day"
        ].isoformat()
        == "2026-08-12"
    )
    assert (
        stored.training_plan.plan_id
        == "adapted-plan"
    )
    assert repository.save_calls == 1


def test_reconciliation_failure_does_not_persist():

    athlete = Athlete(
        name="Pedro"
    )

    repository = (
        RecordingAthleteRepository(
            (
                athlete,
            )
        )
    )

    activity = workout(
        workout_id="activity-1",
        day=datetime(
            2026,
            8,
            10,
            8,
            0,
        ),
    )

    with pytest.raises(
        RuntimeError,
        match="reconciliation failed",
    ):
        ImportActivities(
            repository=repository,
            reconciler=FakeReconciler(
                error=RuntimeError(
                    "reconciliation failed"
                )
            ),
        ).execute(
            athlete.athlete_id,
            (
                activity,
            ),
        )

    stored = repository.get(
        athlete.athlete_id
    )

    assert len(stored.history) == 0
    assert repository.save_calls == 0


def test_rejects_non_workout_input():

    athlete = Athlete(
        name="Pedro"
    )

    repository = (
        RecordingAthleteRepository(
            (
                athlete,
            )
        )
    )

    with pytest.raises(
        TypeError,
        match="Workout objects",
    ):
        ImportActivities(
            repository=repository,
            reconciler=FakeReconciler(),
        ).execute(
            athlete.athlete_id,
            (
                object(),
            ),
        )

    assert repository.save_calls == 0


def test_unknown_athlete_raises():

    with pytest.raises(
        FileNotFoundError,
        match="does not exist",
    ):
        ImportActivities(
            repository=(
                RecordingAthleteRepository()
            ),
            reconciler=FakeReconciler(),
        ).execute(
            "unknown-athlete",
            (),
        )

def test_identical_activity_is_reported_as_duplicate():

    existing = workout(
        workout_id="existing",
        day=datetime(
            2026,
            8,
            10,
            8,
            0,
        ),
        title="Morning Run",
    )

    athlete = Athlete(
        name="Pedro"
    )

    athlete.history.add(
        existing
    )

    duplicate = workout(
        workout_id="duplicate-import",
        day=datetime(
            2026,
            8,
            10,
            8,
            0,
        ),
        title="Morning Run",
    )

    repository = (
        RecordingAthleteRepository(
            (
                athlete,
            )
        )
    )

    reconciler = FakeReconciler()

    result = ImportActivities(
        repository=repository,
        reconciler=reconciler,
    ).execute(
        athlete.athlete_id,
        (
            duplicate,
        ),
    )

    assert result.changed is False
    assert result.added_count == 0
    assert result.updated_count == 0
    assert result.duplicate_count == 1

    assert result.outcomes == (
        result.outcomes[0],
    )

    assert (
        result.outcomes[0].workout_id
        == "duplicate-import"
    )

    assert (
        result.outcomes[0].status
        == "duplicate"
    )

    assert (
        result.reconciled_through
        is None
    )

    assert reconciler.call is None
    assert repository.save_calls == 0

def test_fit_reimport_persists_corrected_metrics():

    existing = workout(
        workout_id="existing-fit",
        day=datetime(
            2026,
            8,
            30,
            8,
            0,
        ),
    )

    existing.info.source = "fit"
    existing.info.distance = 51.26
    existing.info.duration = timedelta(
        hours=2,
        minutes=47,
    )
    existing.info.elevation_gain = 980.0
    existing.feedback.rpe = 7.0
    existing.feedback.notes = (
        "Manual athlete note."
    )

    athlete = Athlete(
        name="Pedro"
    )

    athlete.history.add(
        existing
    )

    imported = workout(
        workout_id="reimported-fit",
        day=datetime(
            2026,
            8,
            30,
            8,
            0,
            20,
        ),
    )

    imported.info.source = "fit"
    imported.info.distance = 51.26
    imported.info.duration = timedelta(
        hours=2,
        minutes=29,
        seconds=15,
    )
    imported.info.elevation_gain = 930.0

    repository = (
        RecordingAthleteRepository(
            (
                athlete,
            )
        )
    )

    result = ImportActivities(
        repository=repository,
        reconciler=FakeReconciler(),
    ).execute(
        athlete.athlete_id,
        (
            imported,
        ),
    )

    stored = repository.get(
        athlete.athlete_id
    )

    assert result.added_count == 0
    assert result.updated_count == 1
    assert result.duplicate_count == 0
    assert len(stored.history) == 1

    stored_workout = (
        stored.history[0]
    )

    assert (
        stored_workout.info.duration
        == timedelta(
            hours=2,
            minutes=29,
            seconds=15,
        )
    )
    assert (
        stored_workout.info.elevation_gain
        == 930.0
    )
    assert (
        stored_workout.feedback.rpe
        == 7.0
    )
    assert (
        stored_workout.feedback.notes
        == "Manual athlete note."
    )
    assert repository.save_calls == 1