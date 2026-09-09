"""Restore a previous immutable training-plan revision."""

from copy import deepcopy
from dataclasses import dataclass, replace
from datetime import date, timedelta
import re

from performancelab.storage.athlete_repository import AthleteRepository
from performancelab.training.planning import TrainingPlanRevision
from performancelab.race import Event, EventEntry
from performancelab.race.eventbook import EventBook


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

        workout_days = tuple(workout.day for workout in target.workouts)
        if target.start_date is not None:
            start_date = target.start_date
        elif workout_days:
            first_day = min(workout_days)
            start_date = first_day - timedelta(days=first_day.weekday())
        else:
            start_date = plan.start_date

        if target.end_date is not None:
            end_date = target.end_date
        elif workout_days:
            last_day = max(workout_days)
            end_date = last_day + timedelta(days=6 - last_day.weekday())
        else:
            end_date = plan.end_date

        restored_events = (
            list(deepcopy(target.events))
            if target.events is not None
            else list(deepcopy(tuple(athlete.events)))
        )
        if target.events is None:
            existing_days = {
                entry.event.date
                for entry in restored_events
            }
            for workout in target.workouts:
                is_race = (
                    str(workout.intensity or "").strip().lower() == "race effort"
                    or "race" in str(workout.title or "").strip().lower()
                )
                if not is_race or workout.day in existing_days:
                    continue
                detail = " ".join(
                    str(value or "")
                    for value in (
                        workout.description,
                        workout.prescription_summary,
                        workout.objective,
                    )
                )
                match = re.search(
                    r"Registered event:\s*([^\.]+)",
                    detail,
                    flags=re.IGNORECASE,
                )
                event_name = (
                    match.group(1).strip()
                    if match
                    else str(workout.title or "Recovered race")
                )
                restored_events.append(
                    EventEntry(
                        event=Event(
                            name=event_name,
                            date=workout.day,
                            sport=workout.sport or "Running",
                            distance=workout.distance,
                            elevation_gain=workout.elevation_gain,
                        ),
                        priority="A",
                        notes="Recovered with an earlier training-plan revision.",
                    )
                )
                existing_days.add(workout.day)

        athlete.events = EventBook(entries=restored_events)
        athlete.events._sort()
        restored_event_ids = tuple(
            entry.event.event_id
            for entry in athlete.events
            if entry.event.date is not None
        )
        primary_event_id = target.primary_event_id
        if primary_event_id not in restored_event_ids:
            primary_event_id = (
                plan.primary_event_id
                if plan.primary_event_id in restored_event_ids
                else (restored_event_ids[0] if restored_event_ids else None)
            )
        competition_event_ids = tuple(
            event_id
            for event_id in target.competition_event_ids
            if event_id in restored_event_ids
        )
        if not competition_event_ids:
            competition_event_ids = restored_event_ids

        recovery = TrainingPlanRevision(
            created_on=today or date.today(),
            source="recovery",
            workouts=target.workouts,
            reason=f"Recovered revision {target.revision_id}.",
            parent_revision_id=plan.active_revision_id,
            start_date=start_date,
            end_date=end_date,
            events=tuple(deepcopy(tuple(athlete.events))),
            primary_event_id=primary_event_id,
            competition_event_ids=competition_event_ids,
        )

        athlete.training_plan = replace(
            plan,
            start_date=start_date,
            end_date=end_date,
            workouts=list(target.workouts),
            revisions=(*plan.revisions, recovery),
            active_revision_id=recovery.revision_id,
            primary_event_id=primary_event_id,
            competition_event_ids=competition_event_ids,
        )
        self._repository.save(athlete)

        return RestoreTrainingPlanRevisionResult(
            athlete=athlete,
            restored_revision_id=target.revision_id,
            active_revision_id=recovery.revision_id,
        )
