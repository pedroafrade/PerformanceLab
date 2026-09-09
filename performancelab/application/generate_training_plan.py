"""
PerformanceLab

Generate training plan application use case.
"""

from copy import deepcopy
from dataclasses import dataclass, replace
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
    ensure_plan_revision_history,
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

        previous_plan = ensure_plan_revision_history(
            athlete.training_plan,
            created_on=today,
        )
        previous_plan_id = previous_plan.plan_id

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

        generated_plan = ensure_plan_revision_history(
            generated_plan,
            created_on=today,
        )

        if previous_plan.revisions:
            generated_plan = replace(
                generated_plan,
                revisions=(
                    *previous_plan.revisions,
                    *generated_plan.revisions,
                ),
                workouts=list(generated_plan.workouts),
            )

        active_revision = next(
            (
                revision
                for revision in generated_plan.revisions
                if revision.revision_id == generated_plan.active_revision_id
            ),
            None,
        )
        if active_revision is not None:
            snapshot = replace(
                active_revision,
                start_date=generated_plan.start_date,
                end_date=generated_plan.end_date,
                events=tuple(deepcopy(tuple(athlete.events))),
                primary_event_id=generated_plan.primary_event_id,
                competition_event_ids=generated_plan.competition_event_ids,
            )
            generated_plan = replace(
                generated_plan,
                revisions=tuple(
                    snapshot if revision.revision_id == snapshot.revision_id else revision
                    for revision in generated_plan.revisions
                ),
                workouts=list(generated_plan.workouts),
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
