"""Restore a previous immutable training-plan revision."""

from dataclasses import dataclass, replace
from datetime import date

from performancelab.storage.athlete_repository import AthleteRepository
from performancelab.training.planning import TrainingPlanRevision


@dataclass(frozen=True)
class RestoreTrainingPlanRevisionResult:
    athlete: object
    restored_revision_id: str
    active_revision_id: str


class RestoreTrainingPlanRevision:

    def __init__(self, *, repository: AthleteRepository) -> None:
        self._repository = repository

    def execute(
        self,
        athlete_id: str,
        revision_id: str,
        *,
        today: date | None = None,
    ) -> RestoreTrainingPlanRevisionResult:
        athlete = self._repository.get(athlete_id)
        plan = athlete.training_plan

        target = next(
            (
                revision
                for revision in plan.revisions
                if revision.revision_id == revision_id
            ),
            None,
        )

        if target is None:
            raise LookupError("Training plan revision was not found.")

        recovery = TrainingPlanRevision(
            created_on=today or date.today(),
            source="recovery",
            workouts=target.workouts,
            reason=f"Recovered revision {target.revision_id}.",
            parent_revision_id=plan.active_revision_id,
        )

        athlete.training_plan = replace(
            plan,
            workouts=list(target.workouts),
            revisions=(*plan.revisions, recovery),
            active_revision_id=recovery.revision_id,
        )
        self._repository.save(athlete)

        return RestoreTrainingPlanRevisionResult(
            athlete=athlete,
            restored_revision_id=target.revision_id,
            active_revision_id=recovery.revision_id,
        )
