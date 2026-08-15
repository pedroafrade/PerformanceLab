"""
PerformanceLab

Generate training plan application use case.
"""

from dataclasses import (
    dataclass,
)
from datetime import (
    date,
)

from performancelab.athlete import (
    Athlete,
)
from performancelab.coaching import (
    Coach,
)
from performancelab.storage.athlete_repository import (
    AthleteRepository,
)
from performancelab.training.planning import (
    TrainingPlan,
)


@dataclass(
    frozen=True
)
class GenerateTrainingPlanResult:
    """
    Result of generating a persistent training plan.
    """

    athlete: Athlete
    training_plan: TrainingPlan
    previous_plan_id: str
    generated_plan_id: str


class GenerateTrainingPlan:
    """
    Generate and persist a complete training plan atomically.

    The athlete is loaded independently from the repository.
    Persistence only occurs after plan generation finishes
    successfully and returns a valid TrainingPlan.
    """

    def __init__(
        self,
        *,
        repository: AthleteRepository,
        coach: Coach | None = None,
    ) -> None:

        self._repository = repository
        self._coach = (
            coach
            or Coach()
        )

    def execute(
        self,
        athlete_id: str,
        *,
        today: date | None = None,
    ) -> GenerateTrainingPlanResult:
        """
        Generate, validate and persist a new training plan.
        """

        athlete = self._repository.get(
            athlete_id
        )

        previous_plan_id = (
            athlete.training_plan.plan_id
        )

        generated_plan = (
            self._coach.build_training_plan(
                athlete=athlete,
                today=today,
            )
        )

        if not isinstance(
            generated_plan,
            TrainingPlan,
        ):
            raise TypeError(
                "Coach must return a TrainingPlan."
            )

        athlete.training_plan = (
            generated_plan
        )

        self._repository.save(
            athlete
        )

        return GenerateTrainingPlanResult(
            athlete=athlete,
            training_plan=generated_plan,
            previous_plan_id=(
                previous_plan_id
            ),
            generated_plan_id=(
                generated_plan.plan_id
            ),
        )