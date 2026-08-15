from datetime import (
    date,
)

import pytest

from performancelab.application import (
    LoadActiveAthlete,
)
from performancelab.athlete import (
    Athlete,
)
from performancelab.identity import (
    User,
)
from performancelab.storage.in_memory_athlete_repository import (
    InMemoryAthleteRepository,
)
from performancelab.training.planning import (
    TrainingPlan,
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
    ) -> None:

        self.replacement_plan = (
            replacement_plan
        )
        self.call = None

    def reconcile_closed_days(
        self,
        *,
        plan,
        history,
        training_state,
        today=None,
    ):

        self.call = {
            "plan": plan,
            "history": history,
            "training_state": (
                training_state
            ),
            "today": today,
        }

        if (
            self.replacement_plan
            is not None
        ):
            return self.replacement_plan

        return plan


def athlete_user(
    athlete,
):

    return User(
        email="pedro@example.com",
        role="athlete",
        athlete_id=(
            athlete.athlete_id
        ),
    )


def test_loads_athlete_associated_with_user():

    pedro = Athlete(
        name="Pedro"
    )
    maria = Athlete(
        name="Maria"
    )

    repository = (
        RecordingAthleteRepository(
            (
                pedro,
                maria,
            )
        )
    )

    result = LoadActiveAthlete(
        repository=repository,
        reconciler=FakeReconciler(),
    ).execute(
        athlete_user(
            maria
        ),
        today=date(
            2026,
            8,
            15,
        ),
    )

    assert (
        result.athlete.athlete_id
        == maria.athlete_id
    )
    assert result.athlete.name == "Maria"


def test_passes_loaded_domain_state_to_reconciler():

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
    reconciler = FakeReconciler()

    reference_day = date(
        2026,
        8,
        15,
    )

    result = LoadActiveAthlete(
        repository=repository,
        reconciler=reconciler,
    ).execute(
        athlete_user(
            athlete
        ),
        today=reference_day,
    )

    assert (
        reconciler.call["plan"]
        is result.athlete.training_plan
    )
    assert (
        reconciler.call["history"]
        is result.athlete.history
    )
    assert (
        reconciler.call["today"]
        == reference_day
    )
    assert (
        reconciler.call[
            "training_state"
        ]
        is not None
    )


def test_does_not_save_when_plan_is_unchanged():

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

    result = LoadActiveAthlete(
        repository=repository,
        reconciler=FakeReconciler(),
    ).execute(
        athlete_user(
            athlete
        )
    )

    assert result.plan_changed is False
    assert repository.save_calls == 0


def test_saves_when_reconciliation_replaces_plan():

    athlete = Athlete(
        name="Pedro"
    )
    replacement_plan = (
        TrainingPlan()
    )

    repository = (
        RecordingAthleteRepository(
            (
                athlete,
            )
        )
    )

    result = LoadActiveAthlete(
        repository=repository,
        reconciler=FakeReconciler(
            replacement_plan=(
                replacement_plan
            )
        ),
    ).execute(
        athlete_user(
            athlete
        )
    )

    stored = repository.get(
        athlete.athlete_id
    )

    assert result.plan_changed is True
    assert repository.save_calls == 1
    assert (
        result.athlete.training_plan
        is replacement_plan
    )
    assert (
        stored.training_plan
        is not replacement_plan
    )


def test_missing_athlete_raises():

    repository = (
        RecordingAthleteRepository()
    )

    user = User(
        email="pedro@example.com",
        role="athlete",
        athlete_id="missing-athlete",
    )

    with pytest.raises(
        FileNotFoundError,
        match="does not exist",
    ):
        LoadActiveAthlete(
            repository=repository,
            reconciler=FakeReconciler(),
        ).execute(
            user
        )


def test_coach_temporarily_loads_first_athlete():

    pedro = Athlete(
        name="Pedro"
    )
    maria = Athlete(
        name="Maria"
    )

    repository = (
        RecordingAthleteRepository(
            (
                pedro,
                maria,
            )
        )
    )

    coach = User(
        email="coach@example.com",
        role="coach",
    )

    result = LoadActiveAthlete(
        repository=repository,
        reconciler=FakeReconciler(),
    ).execute(
        coach
    )

    assert result.athlete.name == "Maria"


def test_coach_without_athletes_raises():

    coach = User(
        email="coach@example.com",
        role="coach",
    )

    with pytest.raises(
        LookupError,
        match="No athlete profiles",
    ):
        LoadActiveAthlete(
            repository=(
                RecordingAthleteRepository()
            ),
            reconciler=FakeReconciler(),
        ).execute(
            coach
        )