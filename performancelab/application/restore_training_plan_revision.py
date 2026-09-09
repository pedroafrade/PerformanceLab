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

    @staticmethod
    def _is_race_workout(workout) -> bool:
        title = str(workout.title or "").strip().lower()
        intensity = str(workout.intensity or "").strip().lower()
        return (
            intensity == "race effort"
            or title in {"race", "competition", "event"}
        )

    @staticmethod
    def _event_name_from_workout(workout) -> str:
        detail = " ".join(
            str(value or "")
            for value in (
                workout.title,
                workout.description,
                workout.prescription_summary,
                workout.objective,
                workout.purpose,
                workout.focus,
                *workout.structure,
            )
        )
        patterns = (
            r"Registered event:\s*([^\.]+)",
            r"Perform effectively at\s+(.+?)(?:\.|$)",
        )
        for pattern in patterns:
            match = re.search(
                pattern,
                detail,
                flags=re.IGNORECASE,
            )
            if match is not None and match.group(1).strip():
                return match.group(1).strip()
        return str(workout.title or "Recovered race")

    @classmethod
    def _remove_workout_events(cls, events, workouts):
        """Removes events accidentally created from ordinary plan sessions."""
        workouts_by_day = {}
        for workout in workouts:
            workouts_by_day.setdefault(workout.day, []).append(workout)

        cleaned = []
        for entry in events:
            event = entry.event
            same_day = workouts_by_day.get(event.date, ())
            event_name = str(event.name or "").strip().lower()
            remove = False
            for workout in same_day:
                workout_name = str(workout.title or "").strip().lower()
                if cls._is_race_workout(workout):
                    remove = event_name in {
                        "race",
                        "competition",
                        "event",
                    }
                elif (
                    event_name == workout_name
                    or event_name.startswith("pre-race ")
                ):
                    remove = True
                if remove:
                    break
            if not remove:
                cleaned.append(entry)
        return cleaned

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

        target_index = next(
            (
                index
                for index, revision in enumerate(plan.revisions)
                if revision.revision_id == revision_id
            ),
            None,
        )

        if target_index is None:
            raise LookupError("Training plan revision was not found.")

        target = plan.revisions[target_index]
        retained_revisions = plan.revisions[: target_index + 1]

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
            restored_events = self._remove_workout_events(
                restored_events,
                target.workouts,
            )
            existing_days = {
                entry.event.date
                for entry in restored_events
            }
            for workout in target.workouts:
                if (
                    not self._is_race_workout(workout)
                    or workout.day in existing_days
                ):
                    continue
                restored_events.append(
                    EventEntry(
                        event=Event(
                            name=self._event_name_from_workout(workout),
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

        original_revision = next(
            (
                revision
                for revision in retained_revisions
                if revision.source == "generated"
            ),
            target,
        )

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
            original_workouts=original_revision.workouts,
            revisions=(*retained_revisions, recovery),
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
