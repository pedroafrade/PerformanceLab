from dataclasses import (
    FrozenInstanceError,
    replace,
)
from datetime import (
    date,
    datetime,
    timedelta,
)

import pytest

from performancelab import (
    Athlete,
    Workout,
)
from performancelab.race import (
    Event,
    EventEntry,
)
from performancelab.presentation import (
    ActivityCoachPresenter,
    ActivityListItemData,
)


def create_activity():
    return ActivityListItemData(
        workout_id="workout-1",
        workout_date=date(
            2026,
            8,
            9,
        ),
        sport="Running",
        title="Long Hill Run",
        distance=11.58,
        duration=timedelta(
            hours=1,
            minutes=42,
        ),
        elevation_gain=632.0,
        rpe=7.7,
        outcome_status="modified",
        planned_title="Long Run",
        planned_load=419.0,
        completed_load=789.0,
        load_difference=370.0,
    )


def create_workout():
    workout = Workout()

    workout.info.sport = "Running"
    workout.info.sub_sport = "trail"

    workout.sensors.add(
        "heart_rate",
        [
            {
                "value": 160,
            },
            {
                "value": 168,
            },
            {
                "value": 185,
            },
        ],
    )

    workout.sensors.add(
        "power",
        [
            {
                "value": 190,
            },
            {
                "value": 214,
            },
        ],
    )

    workout.sensors.add(
        "cadence",
        [
            {
                "value": 138,
            },
            {
                "value": 144,
            },
        ],
    )

    workout.environment.temperature = 20.0
    workout.environment.humidity = 89.0
    workout.environment.terrain = "Trail"

    return workout


def test_builds_activity_coach_context():

    context = ActivityCoachPresenter(
        activity=create_activity(),
        workout=create_workout(),
    ).build().context

    assert context.activity.title == (
        "Long Hill Run"
    )

    assert context.heart_rate.average == (
        pytest.approx(171.0)
    )
    assert context.heart_rate.maximum == 185.0

    assert context.power.average == (
        pytest.approx(202.0)
    )
    assert context.power.maximum == 214.0

    assert context.cadence.average == (
        pytest.approx(141.0)
    )
    assert context.cadence.maximum == 144.0

    assert context.sport == "Running"
    assert context.sub_sport == "trail"

    assert context.temperature == 20.0
    assert context.humidity == 89.0
    assert context.terrain == "Trail"


def test_activity_coach_context_is_immutable():

    context = ActivityCoachPresenter(
        activity=create_activity(),
        workout=create_workout(),
    ).build().context

    with pytest.raises(
        FrozenInstanceError
    ):
        context.temperature = 25.0

def test_builds_recent_training_context():

    athlete = Athlete(
        name="Pedro"
    )

    previous = Workout()
    previous.info.title = "Easy Run"
    previous.info.sport = "Running"
    previous.info.date = date(
        2026,
        8,
        6,
    )
    previous.info.duration = timedelta(
        minutes=60
    )
    previous.feedback.rpe = 5.0

    current = create_workout()
    current.info.title = (
        "Long Hill Run"
    )
    current.info.sport = "Running"
    current.info.date = date(
        2026,
        8,
        9,
    )
    current.info.duration = timedelta(
        minutes=102
    )
    current.feedback.rpe = 7.7

    athlete.history.add(
        previous
    )
    athlete.history.add(
        current
    )

    activity = replace(
        create_activity(),
        workout_id=str(
            current.workout_id
        ),
    )

    context = ActivityCoachPresenter(
        activity=activity,
        workout=current,
        athlete=athlete,
    ).build().context

    recent = (
        context.recent_training
    )

    assert recent.window_days == 7
    assert recent.session_count == 2

    assert (
        recent.total_duration_minutes
        == pytest.approx(162.0)
    )

    assert recent.total_load > 0

    assert recent.previous_title == (
        "Easy Run"
    )
    assert (
        recent.previous_days_before
        == 3
    )
    assert (
        recent.previous_load
        == pytest.approx(300.0)
    )


def test_recent_training_context_is_immutable():

    athlete = Athlete(
        name="Pedro"
    )

    context = ActivityCoachPresenter(
        activity=create_activity(),
        workout=create_workout(),
        athlete=athlete,
    ).build().context

    with pytest.raises(
        FrozenInstanceError
    ):
        (
            context
            .recent_training
            .session_count
        ) = 3

def test_builds_plan_event_and_physiology_context():

    athlete = Athlete(
        name="Pedro",
        ftp=220.0,
        threshold_hr=177,
    )

    current = create_workout()
    current.info.title = (
        "Long Hill Run"
    )
    current.info.sport = "Running"
    current.info.date = date(
        2026,
        8,
        9,
    )
    current.info.duration = timedelta(
        minutes=102
    )
    current.feedback.rpe = 7.7

    athlete.history.add(
        current
    )

    athlete.training_plan.schedule(
        scheduled_at=datetime(
            2026,
            8,
            9,
            8,
            0,
        ),
        sport="Trail Running",
        title="Long Run",
        duration=timedelta(
            minutes=90
        ),
        phase="Build",
    )

    athlete.events.add(
        EventEntry(
            event=Event(
                name="PéFirme",
                date=date(
                    2026,
                    9,
                    13,
                ),
                sport="Trail Running",
                distance=23.0,
                elevation_gain=950.0,
                terrain="Trail",
            ),
            priority="A",
        )
    )

    activity = replace(
        create_activity(),
        workout_id=str(
            current.workout_id
        ),
    )

    context = ActivityCoachPresenter(
        activity=activity,
        workout=current,
        athlete=athlete,
    ).build().context

    assert context.plan.phase == "Build"

    assert context.event.name == "PéFirme"
    assert (
        context.event.distance
        == 23.0
    )
    assert (
        context.event.elevation_gain
        == 950.0
    )
    assert (
        context.event.priority
        == "A"
    )
    assert (
        context.event.days_until_event
        == 35
    )

    assert (
        context.physiology.threshold_hr
        == 177
    )
    assert context.physiology.ftp == 220.0
    assert (
        context.physiology.state_is_current
        is True
    )
    assert (
        context.physiology.readiness
        is not None
    )
    assert (
        context.physiology.recovery_score
        is not None
    )


def test_does_not_present_current_state_as_historical():

    athlete = Athlete(
        name="Pedro"
    )

    selected = create_workout()
    selected.info.date = date(
        2026,
        8,
        9,
    )
    selected.info.duration = timedelta(
        minutes=60
    )
    selected.feedback.rpe = 6.0

    later = Workout()
    later.info.date = date(
        2026,
        8,
        10,
    )
    later.info.duration = timedelta(
        minutes=45
    )
    later.feedback.rpe = 5.0

    athlete.history.add(
        selected
    )
    athlete.history.add(
        later
    )

    activity = replace(
        create_activity(),
        workout_id=str(
            selected.workout_id
        ),
    )

    context = ActivityCoachPresenter(
        activity=activity,
        workout=selected,
        athlete=athlete,
    ).build().context

    assert (
        context.physiology.state_is_current
        is False
    )
    assert (
        context.physiology.readiness
        is None
    )
    assert (
        context.physiology.recovery_score
        is None
    )



def test_builds_activity_coach_assessment():

    assessment = ActivityCoachPresenter(
        activity=create_activity(),
        workout=create_workout(),
    ).build()

    assert assessment.context.activity.title == (
        "Long Hill Run"
    )

    signal_codes = tuple(
        signal.code
        for signal in assessment.signals
    )

    assert "load_above_plan" in signal_codes
    assert isinstance(
        assessment.signals,
        tuple,
    )


def test_activity_coach_assessment_is_immutable():

    assessment = ActivityCoachPresenter(
        activity=create_activity(),
        workout=create_workout(),
    ).build()

    with pytest.raises(
        FrozenInstanceError
    ):
        assessment.signals = ()



def test_includes_only_recorded_athlete_feedback():

    workout = create_workout()

    workout.feedback.rpe = 7.7
    workout.feedback.estimated_rpe = 8.5
    workout.feedback.feeling = 6.0
    workout.feedback.sleep_quality = 4.0
    workout.feedback.motivation = 7.0
    workout.feedback.stress = 5.0
    workout.feedback.muscle_soreness = 3.0
    workout.feedback.notes = (
        "Felt tired on the final climb."
    )

    assessment = ActivityCoachPresenter(
        activity=create_activity(),
        workout=workout,
    ).build()

    feedback = (
        assessment.context.feedback
    )

    assert feedback.rpe == 7.7
    assert feedback.feeling == 6.0
    assert feedback.sleep_quality == 4.0
    assert feedback.motivation == 7.0
    assert feedback.stress == 5.0
    assert feedback.muscle_soreness == 3.0
    assert feedback.notes == (
        "Felt tired on the final climb."
    )

    assert not hasattr(
        feedback,
        "estimated_rpe",
    )


def test_uses_none_for_unrecorded_feedback():

    assessment = ActivityCoachPresenter(
        activity=create_activity(),
        workout=create_workout(),
    ).build()

    feedback = (
        assessment.context.feedback
    )

    assert feedback.rpe is None
    assert feedback.feeling is None
    assert feedback.sleep_quality is None
    assert feedback.motivation is None
    assert feedback.stress is None
    assert feedback.muscle_soreness is None
    assert feedback.notes is None



def test_ignores_missing_recent_training_load():

    athlete = Athlete(
        name="Pedro"
    )

    previous = Workout()
    previous.info.title = (
        "Activity without RPE"
    )
    previous.info.sport = "Running"
    previous.info.date = date(
        2026,
        8,
        6,
    )
    previous.info.duration = timedelta(
        minutes=30
    )

    current = Workout()
    current.info.title = (
        "Current activity"
    )
    current.info.sport = "Running"
    current.info.date = date(
        2026,
        8,
        9,
    )
    current.info.duration = timedelta(
        minutes=45
    )

    athlete.history.add(
        previous
    )
    athlete.history.add(
        current
    )

    activity = replace(
        create_activity(),
        workout_id=str(
            current.workout_id
        ),
    )

    context = ActivityCoachPresenter(
        activity=activity,
        workout=current,
        athlete=athlete,
    ).build().context

    recent = (
        context.recent_training
    )

    assert recent.session_count == 2

    assert (
        recent.total_duration_minutes
        == pytest.approx(75.0)
    )

    assert recent.total_load == 0.0

    assert (
        recent.previous_title
        == "Activity without RPE"
    )

    assert (
        recent.previous_load
        is None
    )

def test_outside_plan_activity_has_no_plan_or_event_context():

    athlete = Athlete(
        name="Pedro"
    )

    workout = create_workout()
    workout.info.title = "Historical Run"
    workout.info.sport = "Running"
    workout.info.date = date(
        2026,
        7,
        18,
    )
    workout.info.duration = timedelta(
        hours=2
    )
    workout.feedback.rpe = 7.0

    athlete.history.add(
        workout
    )

    athlete.training_plan.schedule(
        scheduled_at=datetime(
            2026,
            8,
            15,
            8,
            0,
        ),
        sport="Trail Running",
        title="Easy Run",
        duration=timedelta(
            minutes=60
        ),
        phase="Build",
    )

    athlete.events.add(
        EventEntry(
            event=Event(
                name="III Trail Pé Firme",
                date=date(
                    2026,
                    9,
                    27,
                ),
                sport="Trail Running",
                distance=23.0,
                elevation_gain=950.0,
                terrain="Trail",
            ),
            priority="A",
        )
    )

    activity = replace(
        create_activity(),
        workout_id=str(
            workout.workout_id
        ),
        workout_date=workout.date,
        outcome_status="outside_plan",
        planned_title=None,
        planned_load=None,
    )

    context = ActivityCoachPresenter(
        activity=activity,
        workout=workout,
        athlete=athlete,
    ).build().context

    assert context.plan.phase is None
    assert context.event.name is None
    assert context.event.distance is None

    assert (
        context.recent_training.session_count
        == 1
    )
    assert (
        context.recent_training.total_load
        > 0
    )


def test_unplanned_activity_keeps_plan_and_event_context():

    athlete = Athlete(
        name="Pedro"
    )

    workout = create_workout()
    workout.info.title = "Unplanned Run"
    workout.info.sport = "Running"
    workout.info.date = date(
        2026,
        8,
        9,
    )
    workout.info.duration = timedelta(
        minutes=75
    )
    workout.feedback.rpe = 6.0

    athlete.history.add(
        workout
    )

    athlete.training_plan.schedule(
        scheduled_at=datetime(
            2026,
            8,
            9,
            8,
            0,
        ),
        sport="Trail Running",
        title="Easy Run",
        duration=timedelta(
            minutes=60
        ),
        phase="Peak",
    )

    athlete.events.add(
        EventEntry(
            event=Event(
                name="III Trail Pé Firme",
                date=date(
                    2026,
                    9,
                    27,
                ),
                sport="Trail Running",
                distance=23.0,
                elevation_gain=950.0,
                terrain="Trail",
            ),
            priority="A",
        )
    )

    activity = replace(
        create_activity(),
        workout_id=str(
            workout.workout_id
        ),
        workout_date=workout.date,
        outcome_status="unplanned",
        planned_title=None,
        planned_load=None,
    )

    context = ActivityCoachPresenter(
        activity=activity,
        workout=workout,
        athlete=athlete,
    ).build().context

    assert context.plan.phase == "Peak"

    assert (
        context.event.name
        == "III Trail Pé Firme"
    )
    assert context.event.distance == 23.0

    assert (
        context.recent_training.session_count
        == 1
    )
    assert (
        context.recent_training.total_load
        > 0
    )


def test_uses_primary_event_instead_of_nearest_event():

    athlete = Athlete(
        name="Pedro"
    )

    workout = create_workout()
    workout.info.title = "Peak Run"
    workout.info.sport = "Running"
    workout.info.date = date(
        2026,
        8,
        9,
    )
    workout.info.duration = timedelta(
        minutes=75
    )
    workout.feedback.rpe = 6.0

    athlete.history.add(
        workout
    )

    athlete.training_plan.schedule(
        scheduled_at=datetime(
            2026,
            8,
            9,
            8,
            0,
        ),
        sport="Trail Running",
        title="Peak Run",
        duration=timedelta(
            minutes=75
        ),
        phase="Peak",
    )

    athlete.events.add(
        EventEntry(
            event=Event(
                name="Sealand",
                date=date(
                    2026,
                    9,
                    13,
                ),
                sport="Road Running",
                distance=10.0,
                elevation_gain=113.0,
            ),
            priority="A",
        )
    )

    athlete.events.add(
        EventEntry(
            event=Event(
                name="III Trail Pé Firme",
                date=date(
                    2026,
                    9,
                    27,
                ),
                sport="Trail Running",
                distance=23.0,
                elevation_gain=950.0,
                terrain="Trail",
            ),
            priority="A",
        )
    )

    activity = replace(
        create_activity(),
        workout_id=str(
            workout.workout_id
        ),
        workout_date=workout.date,
        outcome_status="unplanned",
        planned_title=None,
        planned_load=None,
    )

    context = ActivityCoachPresenter(
        activity=activity,
        workout=workout,
        athlete=athlete,
    ).build().context

    assert (
        context.event.name
        == "III Trail Pé Firme"
    )
    assert context.event.distance == 23.0
    assert context.event.elevation_gain == 950.0

    assert (
        context.event.days_until_event
        == 49
    )