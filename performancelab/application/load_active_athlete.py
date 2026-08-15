"""
PerformanceLab

Load active athlete application use case.
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
from performancelab.identity import (
    User,
)
from performancelab.storage.athlete_repository import (
    AthleteRepository,
)
from performancelab.training.planning import (
    TrainingPlanReconciler,
)


@dataclass(
    frozen=True
)
class LoadActiveAthleteResult:
    """
    Result returned after loading and reconciling an athlete.
    """

    athlete: Athlete
    plan_changed: bool


class LoadActiveAthlete:
    """
    Load the active athlete and reconcile closed days.

    Athlete selection for coach users is temporary and
    preserves the current local application behaviour.
    Explicit authorization will replace it before alpha.
    """

    def __init__(
        self,
        *,
        repository: AthleteRepository,
        reconciler: TrainingPlanReconciler | None = None,
    ) -> None:

        self._repository = repository
        self._reconciler = (
            reconciler
            or TrainingPlanReconciler()
        )

    def execute(
        self,
        user: User,
        *,
        today: date | None = None,
    ) -> LoadActiveAthleteResult:
        """
        Load, reconcile and conditionally persist an athlete.
        """

        athlete = self._load_for_user(
            user
        )

        previous_plan = (
            athlete.training_plan
        )

        reconciled_plan = (
            self._reconciler
            .reconcile_closed_days(
                plan=previous_plan,
                history=athlete.history,
                training_state=(
                    athlete
                    .analytics
                    .training_state
                ),
                today=today,
            )
        )

        plan_changed = (
            reconciled_plan
            is not previous_plan
        )

        athlete.training_plan = (
            reconciled_plan
        )

        if plan_changed:
            self._repository.save(
                athlete
            )

        return LoadActiveAthleteResult(
            athlete=athlete,
            plan_changed=plan_changed,
        )

    def _load_for_user(
        self,
        user: User,
    ) -> Athlete:
        """
        Resolve the athlete currently available to a user.
        """

        if user.is_athlete:

            if user.athlete_id is None:
                raise ValueError(
                    "Athlete user has no athlete profile."
                )

            return self._repository.get(
                user.athlete_id
            )

        athletes = (
            self._repository.list()
        )

        if not athletes:
            raise LookupError(
                "No athlete profiles are available."
            )

        return min(
            athletes,
            key=lambda athlete: (
                athlete.name.lower()
            ),
        )