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
from performancelab.authorization import (
    AthleteAuthorizationService,
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
    Load an explicitly authorized athlete profile.

    Authentication establishes who the user is. A persisted
    owner access grant establishes which athlete profile that
    user is allowed to load.
    """

    def __init__(
        self,
        *,
        repository: AthleteRepository,
        authorization: AthleteAuthorizationService,
        reconciler: TrainingPlanReconciler | None = None,
    ) -> None:

        if not isinstance(
            authorization,
            AthleteAuthorizationService,
        ):
            raise TypeError(
                "authorization must be an "
                "AthleteAuthorizationService."
            )

        self._repository = repository
        self._authorization = authorization

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
        Authorize, load and reconcile an athlete.
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
        Resolve only the athlete explicitly owned by the user.
        """

        if not isinstance(
            user,
            User,
        ):
            raise TypeError(
                "user must be a User."
            )

        if not user.is_athlete:

            raise PermissionError(
                "Only athlete accounts are enabled "
                "for the private alpha."
            )

        if user.athlete_id is None:

            raise ValueError(
                "Athlete user has no athlete profile."
            )

        self._authorization.require_access(
            user_id=user.user_id,
            athlete_id=user.athlete_id,
            allowed_permissions=(
                "owner",
            ),
        )

        return self._repository.get(
            user.athlete_id
        )