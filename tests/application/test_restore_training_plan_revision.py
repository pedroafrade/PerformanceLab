from dataclasses import replace
from datetime import date, datetime, timedelta

import pytest

from performancelab import Athlete
from performancelab.race import Event, EventEntry
from performancelab.application import RestoreTrainingPlanRevision
from performancelab.training.planning import (
    PlannedWorkout,
    TrainingPlan,
    TrainingPlanRevision,
)


class Repository:
    def __init__(self, athlete):
        self.athlete = athlete
        self.saved = []

    def get(self, athlete_id):
        return self.athlete

    def save(self, athlete):
        self.saved.append(athlete)


def session(title):
    return PlannedWorkout(
        scheduled_at=datetime(2026, 9, 8, 8),
        sport="Running",
        title=title,
        duration=timedelta(minutes=45),
    )


def test_restores_revision_and_discards_later_versions():
    original = TrainingPlanRevision(
        revision_id="original",
        created_on=date(2026, 9, 1),
        source="generated",
        workouts=(session("Tempo Run"),),
    )
    adapted = TrainingPlanRevision(
        revision_id="adapted",
        created_on=date(2026, 9, 7),
        source="automatic_adaptation",
        workouts=(session("Hill Reps"),),
        parent_revision_id="original",
    )
    athlete = Athlete(name="Pedro")
    athlete.training_plan = TrainingPlan(
        revisions=(original, adapted),
        active_revision_id="adapted",
        workouts=list(adapted.workouts),
    )
    repository = Repository(athlete)

    result = RestoreTrainingPlanRevision(
        repository=repository
    ).execute(
        athlete.athlete_id,
        "original",
        today=date(2026, 9, 8),
    )

    assert result.athlete.training_plan.workouts[0].title == "Tempo Run"
    assert len(result.athlete.training_plan.revisions) == 2
    assert result.athlete.training_plan.revisions[-1].source == "recovery"
    assert all(
        revision.revision_id != "adapted"
        for revision in result.athlete.training_plan.revisions
    )
    assert (
        result.athlete.training_plan.revisions[-1].parent_revision_id
        == "original"
    )
    assert (
        result.athlete.training_plan.original_workouts
        == original.workouts
    )
    assert repository.saved == [athlete]


def test_rejects_unknown_revision():
    athlete = Athlete(name="Pedro")
    repository = Repository(athlete)

    with pytest.raises(LookupError, match="was not found"):
        RestoreTrainingPlanRevision(
            repository=repository
        ).execute(athlete.athlete_id, "missing")


def test_restore_recovers_original_horizon_and_event_snapshot():
    race = EventEntry(
        event=Event(
            event_id="race-13",
            name="Sealand",
            date=date(2026, 9, 13),
            sport="Road Running",
            distance=10,
        ),
        priority="A",
    )
    race_workout = PlannedWorkout(
        scheduled_at=datetime(2026, 9, 13, 8),
        sport="Road Running",
        title="Race",
        duration=timedelta(minutes=50),
        intensity="Race effort",
    )
    revision = TrainingPlanRevision(
        revision_id="before-deletion",
        created_on=date(2026, 9, 9),
        source="manual_edit",
        workouts=(race_workout,),
        start_date=date(2026, 8, 10),
        end_date=date(2026, 10, 4),
        events=(race,),
        primary_event_id="race-13",
        competition_event_ids=("race-13",),
    )
    athlete = Athlete(name="Pedro")
    athlete.training_plan = TrainingPlan(
        start_date=date(2026, 9, 14),
        end_date=date(2026, 10, 4),
        revisions=(revision,),
        active_revision_id="before-deletion",
        workouts=[],
    )
    repository = Repository(athlete)

    result = RestoreTrainingPlanRevision(repository=repository).execute(
        athlete.athlete_id,
        "before-deletion",
        today=date(2026, 9, 9),
    )

    restored = result.athlete.training_plan
    assert restored.start_date == date(2026, 8, 10)
    assert restored.end_date == date(2026, 10, 4)
    assert restored.first.day == date(2026, 9, 13)
    assert result.athlete.events.next.event.name == "Sealand"


def test_restore_legacy_revision_infers_horizon_and_race_event():
    early_workout = PlannedWorkout(
        scheduled_at=datetime(2026, 8, 12, 8),
        sport="Running",
        title="Easy Run",
    )
    race_workout = PlannedWorkout(
        scheduled_at=datetime(2026, 9, 13, 8),
        sport="Road Running",
        title="Race",
        intensity="Race effort",
        description="Registered event: Sealand.",
    )
    legacy_revision = TrainingPlanRevision(
        revision_id="legacy-before-deletion",
        created_on=date(2026, 9, 9),
        source="manual_edit",
        workouts=(early_workout, race_workout),
    )
    athlete = Athlete(name="Pedro")
    athlete.training_plan = TrainingPlan(
        start_date=date(2026, 9, 14),
        end_date=date(2026, 10, 4),
        revisions=(legacy_revision,),
        active_revision_id=legacy_revision.revision_id,
        workouts=[],
    )
    repository = Repository(athlete)

    result = RestoreTrainingPlanRevision(repository=repository).execute(
        athlete.athlete_id,
        legacy_revision.revision_id,
        today=date(2026, 9, 9),
    )

    restored = result.athlete.training_plan
    assert restored.start_date == date(2026, 8, 10)
    assert restored.end_date == date(2026, 9, 13)
    assert restored.first.day == date(2026, 8, 12)
    assert result.athlete.events.next.event.name == "Sealand"
    assert result.athlete.events.next.event.date == date(2026, 9, 13)


def test_restore_does_not_turn_pre_race_session_into_event():
    pre_race = PlannedWorkout(
        scheduled_at=datetime(2026, 9, 12, 8),
        sport="Running",
        title="Pre-Race Easy Run",
        intensity="Easy",
    )
    race = PlannedWorkout(
        scheduled_at=datetime(2026, 9, 13, 8),
        sport="Road Running",
        title="Race",
        intensity="Race effort",
        objective="Perform effectively at Sealand.",
    )
    revision = TrainingPlanRevision(
        revision_id="legacy-race-week",
        created_on=date(2026, 9, 9),
        source="generated",
        workouts=(pre_race, race),
    )
    athlete = Athlete(name="Pedro")
    athlete.events.add(
        EventEntry(
            event=Event(
                name="Race",
                date=date(2026, 9, 13),
                sport="Road Running",
            ),
            priority="A",
        )
    )
    athlete.events.add(
        EventEntry(
            event=Event(
                name="Pre-Race Easy Run",
                date=date(2026, 9, 12),
                sport="Running",
            ),
            priority="A",
        )
    )
    athlete.training_plan = TrainingPlan(
        revisions=(revision,),
        active_revision_id=revision.revision_id,
        workouts=[],
    )

    result = RestoreTrainingPlanRevision(
        repository=Repository(athlete)
    ).execute(
        athlete.athlete_id,
        revision.revision_id,
        today=date(2026, 9, 9),
    )

    restored_events = tuple(result.athlete.events)
    assert len(restored_events) == 1
    assert restored_events[0].event.name == "Sealand"
    assert restored_events[0].event.date == date(2026, 9, 13)


def test_restore_is_a_complete_consistent_snapshot():
    sealand = EventEntry(
        event=Event(
            event_id="sealand",
            name="Sealand",
            date=date(2026, 9, 13),
            sport="Road Running",
            distance=10,
        ),
        priority="A",
    )
    original_workout = session("Original Tempo")
    restored_workout = replace(
        original_workout,
        scheduled_at=datetime(2026, 9, 12, 8),
        title="Pre-Race Easy Run",
    )
    generated = TrainingPlanRevision(
        revision_id="generated",
        created_on=date(2026, 8, 10),
        source="generated",
        workouts=(original_workout,),
        start_date=date(2026, 8, 10),
        end_date=date(2026, 10, 4),
        events=(sealand,),
    )
    target = TrainingPlanRevision(
        revision_id="target",
        created_on=date(2026, 9, 8),
        source="manual_edit",
        workouts=(restored_workout,),
        parent_revision_id="generated",
        start_date=date(2026, 8, 10),
        end_date=date(2026, 10, 4),
        events=(sealand,),
        primary_event_id="sealand",
        competition_event_ids=("sealand",),
    )
    later = TrainingPlanRevision(
        revision_id="later",
        created_on=date(2026, 9, 9),
        source="automatic_adaptation",
        workouts=(session("Later Hill Reps"),),
        parent_revision_id="target",
    )
    athlete = Athlete(name="Pedro")
    athlete.training_plan = TrainingPlan(
        start_date=date(2026, 9, 7),
        end_date=date(2026, 10, 4),
        workouts=list(later.workouts),
        revisions=(generated, target, later),
        active_revision_id="later",
    )

    result = RestoreTrainingPlanRevision(
        repository=Repository(athlete)
    ).execute(athlete.athlete_id, "target", today=date(2026, 9, 10))

    plan = result.athlete.training_plan
    assert plan.start_date == date(2026, 8, 10)
    assert plan.end_date == date(2026, 10, 4)
    assert tuple(plan.workouts) == target.workouts
    assert plan.original_workouts == generated.workouts
    assert all(item.revision_id != "later" for item in plan.revisions)
    assert plan.revisions[-1].parent_revision_id == "target"
    assert plan.active_revision_id == plan.revisions[-1].revision_id
    assert tuple(result.athlete.events) == (sealand,)
    assert plan.primary_event_id == "sealand"
    assert plan.competition_event_ids == ("sealand",)
