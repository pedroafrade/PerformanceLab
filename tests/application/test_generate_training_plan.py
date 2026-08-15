from datetime import (
    date,
)

import pytest

from performancelab.application import (
    GenerateTrainingPlan,
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


class FakeCoach:

    def __init__(
        self,
        *,
        generated_plan=None,
        error=None,
    ) -> None:

        self.generated_plan = (
            generated_plan
        )
        self.error = error
        self.call = None

    def build_training_plan(
        self,
        *,
        athlete,
        today=None,
    ):

        self.call = {
            "athlete": athlete,
            "today": today,
        }

        if self.error is not None:
            raise self.error

        return self.generated_plan


def test_generates_and_saves_plan_once():

    athlete = Athlete(
        name="Pedro"
    )

    generated_plan = TrainingPlan(
        plan_id="generated-plan"
    )

    repository = (
        RecordingAthleteRepository(
            (
                athlete,
            )
        )
    )

    coach = FakeCoach(
        generated_plan=generated_plan
    )

    reference_day = date(
        2026,
        8,
        15,
    )

    result = GenerateTrainingPlan(
        repository=repository,
        coach=coach,
    ).execute(
        athlete.athlete_id,
        today=reference_day,
    )

    stored = repository.get(
        athlete.athlete_id
    )

    assert repository.save_calls == 1
    assert (
        coach.call["athlete"].athlete_id
        == athlete.athlete_id
    )
    assert (
        coach.call["today"]
        == reference_day
    )
    assert (
        result.training_plan
        is generated_plan
    )
    assert (
        result.generated_plan_id
        == "generated-plan"
    )
    assert (
        stored.training_plan.plan_id
        == "generated-plan"
    )


def test_reports_replaced_plan_identifier():

    athlete = Athlete(
        name="Pedro"
    )

    athlete.training_plan = TrainingPlan(
        plan_id="previous-plan"
    )

    repository = (
        RecordingAthleteRepository(
            (
                athlete,
            )
        )
    )

    result = GenerateTrainingPlan(
        repository=repository,
        coach=FakeCoach(
            generated_plan=TrainingPlan(
                plan_id="new-plan"
            )
        ),
    ).execute(
        athlete.athlete_id
    )

    assert (
        result.previous_plan_id
        == "previous-plan"
    )
    assert (
        result.generated_plan_id
        == "new-plan"
    )
    assert repository.save_calls == 1


def test_generation_failure_does_not_persist():

    athlete = Athlete(
        name="Pedro"
    )

    original_plan_id = (
        athlete.training_plan.plan_id
    )

    repository = (
        RecordingAthleteRepository(
            (
                athlete,
            )
        )
    )

    with pytest.raises(
        RuntimeError,
        match="generation failed",
    ):
        GenerateTrainingPlan(
            repository=repository,
            coach=FakeCoach(
                error=RuntimeError(
                    "generation failed"
                )
            ),
        ).execute(
            athlete.athlete_id
        )

    stored = repository.get(
        athlete.athlete_id
    )

    assert repository.save_calls == 0
    assert (
        stored.training_plan.plan_id
        == original_plan_id
    )


def test_invalid_generated_plan_does_not_persist():

    athlete = Athlete(
        name="Pedro"
    )

    original_plan_id = (
        athlete.training_plan.plan_id
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
        match="must return a TrainingPlan",
    ):
        GenerateTrainingPlan(
            repository=repository,
            coach=FakeCoach(
                generated_plan=object()
            ),
        ).execute(
            athlete.athlete_id
        )

    stored = repository.get(
        athlete.athlete_id
    )

    assert repository.save_calls == 0
    assert (
        stored.training_plan.plan_id
        == original_plan_id
    )


def test_unknown_athlete_raises():

    with pytest.raises(
        FileNotFoundError,
        match="does not exist",
    ):
        GenerateTrainingPlan(
            repository=(
                RecordingAthleteRepository()
            ),
            coach=FakeCoach(
                generated_plan=TrainingPlan()
            ),
        ).execute(
            "unknown-athlete"
        )