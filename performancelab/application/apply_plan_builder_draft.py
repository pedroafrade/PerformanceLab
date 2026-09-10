"""Persist one Plan Builder draft as an immutable plan revision."""

from copy import deepcopy
from dataclasses import dataclass, replace
from datetime import date

from performancelab.storage.athlete_repository import AthleteRepository
from performancelab.training.planning import (
    PlanBuilderDraft,
    TrainingPlanRevision,
)


@dataclass(frozen=True)
class ApplyPlanBuilderDraftResult:
    athlete: object
    changed: bool
    active_revision_id: str | None


class StalePlanBuilderDraftError(ValueError):
    """The draft no longer belongs to the active plan revision."""


class ApplyPlanBuilderDraft:
    """Validate, revision and persist a draft exactly once."""

    def __init__(self, *, repository: AthleteRepository) -> None:
        self._repository = repository

    def execute(
        self,
        athlete_id: str,
        draft: PlanBuilderDraft,
        *,
        today: date | None = None,
    ) -> ApplyPlanBuilderDraftResult:
        athlete = self._repository.get(athlete_id)
        plan = athlete.training_plan
        if (
            draft.source_plan_id != plan.plan_id
            or draft.source_revision_id != plan.active_revision_id
        ):
            raise StalePlanBuilderDraftError(
                "The active plan changed while this draft was open."
            )
        if tuple(draft.workouts) == tuple(plan.workouts):
            return ApplyPlanBuilderDraftResult(
                athlete=athlete,
                changed=False,
                active_revision_id=plan.active_revision_id,
            )

        revision = TrainingPlanRevision(
            created_on=today or date.today(),
            source="manual_edit",
            workouts=tuple(draft.workouts),
            reason="Plan Builder changes applied by the athlete.",
            parent_revision_id=plan.active_revision_id,
            start_date=plan.start_date,
            end_date=plan.end_date,
            events=tuple(deepcopy(tuple(athlete.events))),
            primary_event_id=plan.primary_event_id,
            competition_event_ids=plan.competition_event_ids,
            adaptations=plan.adaptations,
            stimulus_suggestions=plan.stimulus_suggestions,
        )
        revised_plan = replace(
            plan,
            workouts=list(draft.workouts),
            revisions=(*plan.revisions, revision),
            active_revision_id=revision.revision_id,
        )
        athlete.training_plan = revised_plan
        try:
            self._repository.save(athlete)
        except Exception:
            athlete.training_plan = plan
            raise
        return ApplyPlanBuilderDraftResult(
            athlete=athlete,
            changed=True,
            active_revision_id=revision.revision_id,
        )
