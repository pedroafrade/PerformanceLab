"""
Tests for CoachContext.
"""

from datetime import date, timedelta
from types import SimpleNamespace

from performancelab.athlete import Athlete

from performancelab.analysis.training_state import TrainingState

from performancelab.analysis import (
    HeartRateProfile,
    HeartRateZone,
)

from performancelab.coaching import CoachContext

from performancelab.race import (
    Event,
    EventEntry,
)

from performancelab.workout import Workout


def make_athlete(
    *,
    ctl=50.0,
    atl=45.0,
    tsb=5.0,
    next_event=None,
    days_until_event=None,
    sports=("Running",),
    average_rpe=5.5,
    training_plan=None,
):
    """
    Creates a minimal athlete-like object containing the
    analytics interface required by CoachContext.
    """

    if training_plan is None:
        training_plan = object()

    analytics = SimpleNamespace(
        ctl=ctl,
        atl=atl,
        tsb=tsb,
        next_event=next_event,
        days_until_next_event=days_until_event,
        sports=sports,
        average_rpe=average_rpe,
        training_plan=training_plan,
    )

    return SimpleNamespace(
        name="Test Athlete",
        analytics=analytics,
    )


def test_context_uses_athlete_analytics():

    athlete = make_athlete(
        ctl=52.3,
        atl=48.1,
        tsb=4.2,
        sports=("Running", "Cycling"),
        average_rpe=6.0,
    )

    reference_date = date(2026, 3, 10)

    context = CoachContext.from_athlete(
        athlete,
        today=reference_date,
    )

    assert context.athlete is athlete
    assert context.today == reference_date

    assert context.ctl == 52.3
    assert context.atl == 48.1
    assert context.tsb == 4.2

    assert context.sports == (
        "Running",
        "Cycling",
    )

    assert context.average_rpe == 6.0


def test_context_without_events():

    athlete = make_athlete(
        next_event=None,
        days_until_event=None,
    )

    context = CoachContext.from_athlete(
        athlete,
        today=date(2026, 3, 10),
    )

    assert context.next_event is None
    assert context.days_until_event is None


def test_context_with_next_event():

    event_entry = SimpleNamespace(
        event=SimpleNamespace(
            name="Lisbon Half Marathon",
        ),
        priority="A",
    )

    athlete = make_athlete(
        next_event=event_entry,
        days_until_event=84,
    )

    context = CoachContext.from_athlete(
        athlete,
        today=date(2026, 3, 10),
    )

    assert context.next_event is event_entry
    assert context.days_until_event == 84

    assert (
        context.next_event.event.name
        == "Lisbon Half Marathon"
    )


def test_context_preserves_training_plan():

    training_plan = object()

    athlete = make_athlete(
        training_plan=training_plan,
    )

    context = CoachContext.from_athlete(
        athlete,
        today=date(2026, 3, 10),
    )

    assert context.training_plan is training_plan


def test_context_converts_sports_to_tuple():

    athlete = make_athlete(
        sports=[
            "Running",
            "Swimming",
        ],
    )

    context = CoachContext.from_athlete(
        athlete,
        today=date(2026, 3, 10),
    )

    assert isinstance(
        context.sports,
        tuple,
    )

    assert context.sports == (
        "Running",
        "Swimming",
    )


def test_context_accepts_missing_average_rpe():

    athlete = make_athlete(
        average_rpe=None,
    )

    context = CoachContext.from_athlete(
        athlete,
        today=date(2026, 3, 10),
    )

    assert context.average_rpe is None


def make_event_entry(
    event_date: date,
) -> EventEntry:
    return EventEntry(
        event=Event(
            name="Test Race",
            date=event_date,
        ),
    )


def test_context_selects_most_recent_previous_event():
    athlete = Athlete(
        name="Test Athlete",
    )

    today = date(
        2026,
        7,
        20,
    )

    older_event = make_event_entry(
        today - timedelta(
            days=30,
        )
    )

    recent_event = make_event_entry(
        today - timedelta(
            days=3,
        )
    )

    athlete.events.add(
        recent_event
    )

    athlete.events.add(
        older_event
    )

    context = CoachContext.from_athlete(
        athlete,
        today=today,
    )

    assert (
        context.previous_event
        is recent_event
    )

    assert context.days_since_event == 3


def test_context_ignores_future_events_for_previous_event():
    athlete = Athlete(
        name="Test Athlete",
    )

    today = date(
        2026,
        7,
        20,
    )

    athlete.events.add(
        make_event_entry(
            today + timedelta(
                days=5,
            )
        )
    )

    context = CoachContext.from_athlete(
        athlete,
        today=today,
    )

    assert context.previous_event is None
    assert context.days_since_event is None


def test_context_does_not_treat_today_event_as_previous():
    athlete = Athlete(
        name="Test Athlete",
    )

    today = date(
        2026,
        7,
        20,
    )

    athlete.events.add(
        make_event_entry(
            today
        )
    )

    context = CoachContext.from_athlete(
        athlete,
        today=today,
    )

    assert context.previous_event is None
    assert context.days_since_event is None

def test_context_collects_upcoming_events_in_date_order():
    athlete = Athlete(
        name="Test Athlete",
    )

    today = date(
        2026,
        7,
        20,
    )

    later_event = make_event_entry(
        today + timedelta(
            days=60,
        )
    )

    next_event = make_event_entry(
        today + timedelta(
            days=20,
        )
    )

    athlete.events.add(
        later_event
    )

    athlete.events.add(
        next_event
    )

    context = CoachContext.from_athlete(
        athlete,
        today=today,
    )

    assert context.upcoming_events == (
        next_event,
        later_event,
    )

    assert context.next_event is next_event
    assert context.days_until_event == 20


def test_upcoming_events_ignore_past_events():
    athlete = Athlete(
        name="Test Athlete",
    )

    today = date(
        2026,
        7,
        20,
    )

    previous_event = make_event_entry(
        today - timedelta(
            days=10,
        )
    )

    future_event = make_event_entry(
        today + timedelta(
            days=20,
        )
    )

    athlete.events.add(
        previous_event
    )

    athlete.events.add(
        future_event
    )

    context = CoachContext.from_athlete(
        athlete,
        today=today,
    )

    assert context.upcoming_events == (
        future_event,
    )

    assert context.next_event is future_event


def test_context_ignores_events_beyond_planning_horizon():
    athlete = Athlete(
        name="Test Athlete",
    )

    today = date(
        2026,
        7,
        20,
    )

    inside_horizon = make_event_entry(
        today + timedelta(
            days=365,
        )
    )

    outside_horizon = make_event_entry(
        today + timedelta(
            days=366,
        )
    )

    athlete.events.add(
        inside_horizon
    )

    athlete.events.add(
        outside_horizon
    )

    context = CoachContext.from_athlete(
        athlete,
        today=today,
    )

    assert context.upcoming_events == (
        inside_horizon,
    )


def test_context_returns_event_after_current_next_event():
    athlete = Athlete(
        name="Test Athlete",
    )

    today = date(
        2026,
        7,
        20,
    )

    first_event = make_event_entry(
        today + timedelta(
            days=20,
        )
    )

    second_event = make_event_entry(
        today + timedelta(
            days=40,
        )
    )

    athlete.events.add(
        first_event
    )

    athlete.events.add(
        second_event
    )

    context = CoachContext.from_athlete(
        athlete,
        today=today,
    )

    assert (
        context.next_event_after_current
        is second_event
    )

    assert context.days_between_events == 20


def test_context_classifies_close_events_as_cluster():
    athlete = Athlete(
        name="Test Athlete",
    )

    today = date(
        2026,
        7,
        20,
    )

    athlete.events.add(
        make_event_entry(
            today + timedelta(
                days=20,
            )
        )
    )

    athlete.events.add(
        make_event_entry(
            today + timedelta(
                days=60,
            )
        )
    )

    context = CoachContext.from_athlete(
        athlete,
        today=today,
    )

    assert context.days_between_events == 40
    assert context.competition_block == "cluster"


def test_context_classifies_distant_events_as_single():
    athlete = Athlete(
        name="Test Athlete",
    )

    today = date(
        2026,
        7,
        20,
    )

    athlete.events.add(
        make_event_entry(
            today + timedelta(
                days=20,
            )
        )
    )

    athlete.events.add(
        make_event_entry(
            today + timedelta(
                days=100,
            )
        )
    )

    context = CoachContext.from_athlete(
        athlete,
        today=today,
    )

    assert context.days_between_events == 80
    assert context.competition_block == "single"


def test_context_without_future_events_is_season_end():
    athlete = Athlete(
        name="Test Athlete",
    )

    context = CoachContext.from_athlete(
        athlete,
        today=date(
            2026,
            7,
            20,
        ),
    )

    assert context.has_upcoming_event is False
    assert context.competition_block == "season_end"


def test_context_preserves_cluster_after_first_event():
    athlete = Athlete(
        name="Test Athlete",
    )

    first_event_date = date(
        2026,
        7,
        10,
    )

    today = date(
        2026,
        7,
        20,
    )

    first_event = make_event_entry(
        first_event_date
    )

    second_event = make_event_entry(
        first_event_date
        + timedelta(
            days=35,
        )
    )

    athlete.events.add(
        first_event
    )

    athlete.events.add(
        second_event
    )

    context = CoachContext.from_athlete(
        athlete,
        today=today,
    )

    assert context.previous_event is first_event
    assert context.next_event is second_event
    assert context.days_between_events == 35
    assert context.competition_block == "cluster"

def test_context_uses_semantic_training_state():
    athlete = Athlete(
        name="Test Athlete",
    )

    athlete.analytics._training_state = TrainingState(
        ctl=50.0,
        atl=45.0,
        tsb=5.0,
        acute_chronic_ratio=1.4,
        monotony=None,
        strain=None,
        consistency=None,
        weekly_frequency=None,
        days_since_last_workout=None,
        recent_training_load=None,
    )

    context = CoachContext.from_athlete(
        athlete,
        today=date.today(),
    )

    assert context.readiness == "cautious"
    assert context.should_reduce_volume is True
    assert context.can_tolerate_intensity is True
    assert context.can_absorb_more_volume is True

def test_context_preserves_legacy_fallbacks():
    athlete = make_athlete(
        tsb=-15.0,
    )

    context = CoachContext.from_athlete(
        athlete,
        today=date.today(),
    )

    assert context.training_state is None
    assert context.readiness == "easy"
    assert context.should_reduce_volume is True
    assert context.can_tolerate_intensity is False
    assert context.can_absorb_more_volume is False

def test_fatigue_regeneration_uses_training_state():

    athlete = Athlete(
        name="Test Athlete",
    )

    athlete.analytics._training_state = TrainingState(
        ctl=40.0,
        atl=65.0,
        tsb=-25.0,
        acute_chronic_ratio=1.4,
        monotony=None,
        strain=None,
        consistency=None,
        weekly_frequency=None,
        days_since_last_workout=0,
        recent_training_load=600.0,
    )

    context = CoachContext.from_athlete(
        athlete,
        today=date.today(),
    )

    assert context.needs_recovery is True

    assert (
        context.is_fatigue_regeneration
        is True
    )

def test_context_groups_first_competition_block():

    athlete = Athlete(
        name="Test Athlete",
    )

    today = date(
        2026,
        7,
        29,
    )

    first_event = make_event_entry(
        today + timedelta(
            days=46,
        )
    )

    main_event = make_event_entry(
        today + timedelta(
            days=60,
        )
    )

    later_event = make_event_entry(
        today + timedelta(
            days=150,
        )
    )

    athlete.events.add(
        first_event
    )
    athlete.events.add(
        main_event
    )
    athlete.events.add(
        later_event
    )

    context = CoachContext.from_athlete(
        athlete,
        today=today,
    )

    assert (
        context.competition_block_events
        == (
            first_event,
            main_event,
        )
    )

    assert (
        later_event
        not in context.competition_block_events
    )

def test_context_selects_more_demanding_primary_event():

    athlete = Athlete(
        name="Test Athlete",
    )

    today = date(
        2026,
        7,
        29,
    )

    road_event = EventEntry(
        event=Event(
            name="Sealand",
            date=date(
                2026,
                9,
                13,
            ),
            sport="Road Running",
            distance=10,
            elevation_gain=113,
        ),
        priority="A",
    )

    trail_event = EventEntry(
        event=Event(
            name="III Trail Pé Firme",
            date=date(
                2026,
                9,
                27,
            ),
            sport="Trail Running",
            distance=23,
            elevation_gain=950,
        ),
        priority="A",
    )

    athlete.events.add(
        road_event
    )
    athlete.events.add(
        trail_event
    )

    context = CoachContext.from_athlete(
        athlete,
        today=today,
    )

    assert context.next_event is road_event
    assert context.primary_event is trail_event


def test_explicit_priority_precedes_event_demand():

    athlete = Athlete(
        name="Test Athlete",
    )

    today = date(
        2026,
        7,
        29,
    )

    priority_event = EventEntry(
        event=Event(
            name="Priority Road Race",
            date=today + timedelta(
                days=30,
            ),
            sport="Road Running",
            distance=10,
            elevation_gain=100,
        ),
        priority="A",
    )

    demanding_event = EventEntry(
        event=Event(
            name="Secondary Trail",
            date=today + timedelta(
                days=44,
            ),
            sport="Trail Running",
            distance=30,
            elevation_gain=1500,
        ),
        priority="B",
    )

    athlete.events.add(
        priority_event
    )
    athlete.events.add(
        demanding_event
    )

    context = CoachContext.from_athlete(
        athlete,
        today=today,
    )

    assert (
        context.primary_event
        is priority_event
    )

def test_context_exposes_competition_plan_metadata():

    athlete = Athlete(
        name="Test Athlete",
    )

    today = date(
        2026,
        7,
        29,
    )

    road_event = EventEntry(
        event=Event(
            event_id="event-sealand",
            name="Sealand",
            date=date(
                2026,
                9,
                13,
            ),
            sport="Road Running",
            distance=10,
            elevation_gain=113,
        ),
        priority="A",
    )

    trail_event = EventEntry(
        event=Event(
            event_id="event-trail-pe-firme",
            name="III Trail Pé Firme",
            date=date(
                2026,
                9,
                27,
            ),
            sport="Trail Running",
            distance=23,
            elevation_gain=950,
        ),
        priority="A",
    )

    athlete.events.add(
        road_event
    )

    athlete.events.add(
        trail_event
    )

    context = CoachContext.from_athlete(
        athlete,
        today=today,
    )

    assert (
        context.primary_event_id
        == "event-trail-pe-firme"
    )

    assert context.competition_event_ids == (
        "event-sealand",
        "event-trail-pe-firme",
    )

    assert (
        context.planning_end_date
        == date(
            2026,
            9,
            27,
        )
    )
    assert (
        context.days_until_primary_event
        == 60
    )


def test_context_without_events_has_no_plan_metadata():

    athlete = Athlete(
        name="Test Athlete",
    )

    context = CoachContext.from_athlete(
        athlete,
        today=date(
            2026,
            7,
            29,
        ),
    )

    assert context.primary_event_id is None

    assert (
        context.competition_event_ids
        == ()
    )

    assert (
        context.planning_end_date
        is None
    )

    assert (
        context.days_until_primary_event
        is None
    )

def test_near_event_temporarily_determines_phase():

    athlete = Athlete(
        name="Test Athlete",
    )

    today = date(
        2026,
        9,
        7,
    )

    sealand = EventEntry(
        event=Event(
            name="Sealand",
            date=date(
                2026,
                9,
                13,
            ),
            sport="Road Running",
            distance=10,
            elevation_gain=113,
        ),
        priority="A",
    )

    trail = EventEntry(
        event=Event(
            name="III Trail Pé Firme",
            date=date(
                2026,
                9,
                27,
            ),
            sport="Trail Running",
            distance=23,
            elevation_gain=950,
        ),
        priority="A",
    )

    athlete.events.add(
        sealand
    )
    athlete.events.add(
        trail
    )

    context = CoachContext.from_athlete(
        athlete,
        today=today,
    )

    assert context.primary_event is trail
    assert context.phase_event is sealand

    assert (
        context.days_until_phase_event
        == 6
    )


def test_primary_event_guides_phase_outside_taper_window():

    athlete = Athlete(
        name="Test Athlete",
    )

    today = date(
        2026,
        8,
        20,
    )

    sealand = EventEntry(
        event=Event(
            name="Sealand",
            date=date(
                2026,
                9,
                13,
            ),
            sport="Road Running",
            distance=10,
            elevation_gain=113,
        ),
        priority="A",
    )

    trail = EventEntry(
        event=Event(
            name="III Trail Pé Firme",
            date=date(
                2026,
                9,
                27,
            ),
            sport="Trail Running",
            distance=23,
            elevation_gain=950,
        ),
        priority="A",
    )

    athlete.events.add(
        sealand
    )
    athlete.events.add(
        trail
    )

    context = CoachContext.from_athlete(
        athlete,
        today=today,
    )

    assert context.primary_event is trail
    assert context.phase_event is trail

def test_context_estimates_non_primary_event_duration():

    athlete = Athlete(
        name="Test Athlete",
    )

    today = date.today()

    workout = Workout()

    workout.info.sport = "Running"
    workout.info.date = today
    workout.info.distance = 10
    workout.info.duration = timedelta(
        minutes=60,
    )

    athlete.history.add(
        workout
    )

    road_event = EventEntry(
        event=Event(
            name="Sealand",
            date=(
                today
                + timedelta(days=45)
            ),
            sport="Road Running",
            distance=10,
            elevation_gain=0,
        ),
        priority="A",
    )

    trail_event = EventEntry(
        event=Event(
            name="III Trail Pé Firme",
            date=(
                today
                + timedelta(days=60)
            ),
            sport="Trail Running",
            distance=23,
            elevation_gain=950,
        ),
        priority="A",
    )

    athlete.events.add(
        road_event
    )

    athlete.events.add(
        trail_event
    )

    context = CoachContext.from_athlete(
        athlete,
        today=today,
    )

    assert context.primary_event is trail_event

    assert (
        context.event_duration(
            road_event
        )
        == timedelta(minutes=60)
    )

def test_context_estimates_primary_event_duration():

    athlete = Athlete(
        name="Test Athlete",
    )

    today = date.today()

    workout = Workout()

    workout.info.sport = "Running"
    workout.info.date = today
    workout.info.distance = 10
    workout.info.duration = timedelta(
        minutes=60,
    )

    athlete.history.add(
        workout
    )

    athlete.events.add(
        EventEntry(
            event=Event(
                name="III Trail Pé Firme",
                date=(
                    today
                    + timedelta(days=60)
                ),
                sport="Trail Running",
                distance=23,
                elevation_gain=950,
            ),
            priority="A",
        )
    )

    context = CoachContext.from_athlete(
        athlete,
        today=today,
    )

    assert (
        context.primary_event_duration
        == timedelta(
            hours=3,
            minutes=15,
        )
    )


def test_target_time_precedes_estimated_duration():

    athlete = Athlete(
        name="Test Athlete",
    )

    today = date.today()

    workout = Workout()

    workout.info.sport = "Running"
    workout.info.date = today
    workout.info.distance = 10
    workout.info.duration = timedelta(
        minutes=60,
    )

    athlete.history.add(
        workout
    )

    athlete.events.add(
        EventEntry(
            event=Event(
                name="III Trail Pé Firme",
                date=(
                    today
                    + timedelta(days=60)
                ),
                sport="Trail Running",
                distance=23,
                elevation_gain=950,
            ),
            priority="A",
            target_time=timedelta(
                hours=2,
                minutes=45,
            ),
        )
    )

    context = CoachContext.from_athlete(
        athlete,
        today=today,
    )

    assert (
        context.primary_event_duration
        == timedelta(
            hours=2,
            minutes=45,
        )
    )

# ======================================================

def test_context_exposes_heart_rate_profile():

    athlete = Athlete(
        name="Test Athlete",
        max_hr=205,
        resting_hr=65,
        threshold_hr=177,
        manual_heart_rate_zones=(

            HeartRateZone(
                name="Z1",
                lower_bpm=1,
                upper_bpm=120,
            ),

            HeartRateZone(
                name="Z2",
                lower_bpm=121,
                upper_bpm=156,
            ),

            HeartRateZone(
                name="Z3",
                lower_bpm=157,
                upper_bpm=176,
            ),

            HeartRateZone(
                name="Z4",
                lower_bpm=177,
                upper_bpm=186,
            ),

            HeartRateZone(
                name="Z5",
                lower_bpm=187,
                upper_bpm=205,
            ),

        ),
    )

    context = CoachContext.from_athlete(
        athlete,
        today=date(
            2026,
            7,
            31,
        ),
    )

    assert isinstance(
        context.heart_rate_profile,
        HeartRateProfile,
    )

    assert (
        context.heart_rate_profile.source
        == "manual"
    )

    assert (
        context.heart_rate_profile
        .zone("Z4")
        .lower_bpm
        == 177
    )


# ======================================================

def test_context_without_heart_rate_profile():

    athlete = make_athlete()

    context = CoachContext.from_athlete(
        athlete,
        today=date(
            2026,
            7,
            31,
        ),
    )

    assert (
        context.heart_rate_profile
        is None
    )

def test_future_context_does_not_project_current_physiology():

    context = CoachContext(
        athlete=SimpleNamespace(
            name="Test Athlete",
        ),
        today=date(
            2026,
            8,
            17,
        ),
        ctl=30.0,
        atl=90.0,
        tsb=-60.0,
        next_event=SimpleNamespace(
            event=SimpleNamespace(
                name="Target Race",
            ),
        ),
        days_until_event=27,
        sports=("Running",),
        average_rpe=6.0,
        training_plan=object(),
        physiology_is_current=False,
    )

    assert context.training_state is None
    assert not context.needs_recovery
    assert context.readiness == "unknown"
    assert not context.should_reduce_volume
    assert context.can_tolerate_intensity
    assert not context.can_absorb_more_volume
    assert not context.is_fatigue_regeneration
