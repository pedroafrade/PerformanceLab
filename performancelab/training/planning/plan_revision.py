"""
PerformanceLab

Immutable training-plan revision snapshots.
"""

from dataclasses import dataclass, field, replace
from datetime import date, datetime
from uuid import NAMESPACE_URL, uuid4, uuid5

from .planned_workout import PlannedWorkout
from performancelab.race.entry import EventEntry


PLAN_REVISION_SOURCES = {
    "generated",
    "automatic_adaptation",
    "manual_edit",
    "recovery",
}


@dataclass(frozen=True, slots=True)
class TrainingPlanRevision:
    """
    One immutable, recoverable version of a training plan.

    ``workouts`` is a complete snapshot. This intentionally
    keeps recovery independent from the adaptation UI and
    also supports future Plan Builder edits.
    """

    created_on: date
    source: str
    workouts: tuple[PlannedWorkout, ...]

    reason: str = ""
    parent_revision_id: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    events: tuple[EventEntry, ...] | None = None
    primary_event_id: str | None = None
    competition_event_ids: tuple[str, ...] = ()
    revision_id: str = field(
        default_factory=lambda: str(uuid4()),
    )

    def __post_init__(self) -> None:

        if (
            not isinstance(self.created_on, date)
            or isinstance(self.created_on, datetime)
        ):
            raise TypeError("created_on must be a date.")

        if self.source not in PLAN_REVISION_SOURCES:
            raise ValueError(
                "source must describe a supported plan "
                "revision origin."
            )

        if not isinstance(self.workouts, tuple):
            raise TypeError("workouts must be a tuple.")

        if not all(
            isinstance(workout, PlannedWorkout)
            for workout in self.workouts
        ):
            raise TypeError(
                "workouts must contain PlannedWorkout objects."
            )

        if (self.start_date is None) != (self.end_date is None):
            raise ValueError("Revision horizon requires both start and end dates.")
        if self.start_date is not None and self.end_date < self.start_date:
            raise ValueError("Revision end_date cannot precede start_date.")
        if self.events is not None and not all(
            isinstance(entry, EventEntry) for entry in self.events
        ):
            raise TypeError("events must contain EventEntry objects or be None.")

        if (
            not isinstance(self.revision_id, str)
            or not self.revision_id.strip()
        ):
            raise ValueError(
                "revision_id must be a non-empty string."
            )

        if (
            self.parent_revision_id is not None
            and (
                not isinstance(self.parent_revision_id, str)
                or not self.parent_revision_id.strip()
            )
        ):
            raise ValueError(
                "parent_revision_id must be a non-empty "
                "string or None."
            )


def ensure_plan_revision_history(
    plan,
    *,
    created_on: date | None = None,
):
    """Backfills deterministic revisions for legacy plans."""

    if plan.revisions or not plan.workouts:
        return plan

    revision_day = (
        created_on
        or plan.reconciled_through
        or plan.start_date
        or date.today()
    )
    original_workouts = (
        plan.original_workouts
        or tuple(plan.workouts)
    )
    original_id = str(
        uuid5(
            NAMESPACE_URL,
            f"performancelab:{plan.plan_id}:original",
        )
    )
    original = TrainingPlanRevision(
        revision_id=original_id,
        created_on=plan.start_date or revision_day,
        source="generated",
        workouts=tuple(original_workouts),
        reason="Initial generated plan.",
        start_date=plan.start_date,
        end_date=plan.end_date,
        primary_event_id=plan.primary_event_id,
        competition_event_ids=plan.competition_event_ids,
    )

    if tuple(plan.workouts) == tuple(original_workouts):
        revisions = (original,)
        active_revision_id = original_id
    else:
        current = TrainingPlanRevision(
            revision_id=str(
                uuid5(
                    NAMESPACE_URL,
                    f"performancelab:{plan.plan_id}:current",
                )
            ),
            created_on=revision_day,
            source="automatic_adaptation",
            workouts=tuple(plan.workouts),
            reason="Migrated current adapted plan.",
            parent_revision_id=original_id,
            start_date=plan.start_date,
            end_date=plan.end_date,
            primary_event_id=plan.primary_event_id,
            competition_event_ids=plan.competition_event_ids,
        )
        revisions = (original, current)
        active_revision_id = current.revision_id

    return replace(
        plan,
        original_workouts=tuple(original_workouts),
        revisions=revisions,
        active_revision_id=active_revision_id,
        workouts=list(plan.workouts),
    )
