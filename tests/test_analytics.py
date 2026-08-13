"""
PerformanceLab

Tests for AthleteAnalytics.
"""

import pytest

from datetime import date
from datetime import datetime
from datetime import timedelta

from statistics import pstdev

from performancelab import Athlete
from performancelab.workout import Workout

import performancelab.analysis.time as t

from performancelab.analysis.performance_profile import (
    PerformanceProfile,
)
from performancelab.analysis import (
    HeartRateProfile,
    HeartRateZone,
    TimeAwareTrainingLoad,
)
from performancelab.race import Event

print(t.__file__)
print(hasattr(t, "training_days"))
print(dir(t))

# ======================================================

def create_workout(
    sport,
    workout_date,
    distance,
    duration,
    elevation,
    rpe,
):

    workout = Workout()

    workout.info.sport = sport
    workout.info.date = workout_date
    workout.info.distance = distance
    workout.info.duration = duration

    workout.info.elevation_gain = elevation

    workout.feedback.rpe = rpe

    return workout


# ======================================================

def test_empty_analytics():

    athlete = Athlete(name="Pedro")

    analytics = athlete.analytics

    assert analytics.number_of_workouts == 0

    assert analytics.total_distance == 0

    assert analytics.total_duration == timedelta()

    assert analytics.total_elevation == 0

    assert analytics.average_rpe is None

    assert analytics.training_days == 0

    assert analytics.first_workout is None

    assert analytics.last_workout is None


# ======================================================

def test_number_of_workouts():

    athlete = Athlete()

    athlete.history.add(

        create_workout(

            "Running",

            date(2026, 7, 1),

            10,

            timedelta(hours=1),

            250,

            6,

        )

    )

    athlete.history.add(

        create_workout(

            "Cycling",

            date(2026, 7, 2),

            50,

            timedelta(hours=2),

            600,

            5,

        )

    )

    assert athlete.analytics.number_of_workouts == 2


# ======================================================

def test_total_distance():

    athlete = Athlete()

    athlete.history.add(

        create_workout(

            "Running",

            date(2026, 7, 1),

            10,

            timedelta(hours=1),

            100,

            6,

        )

    )

    athlete.history.add(

        create_workout(

            "Running",

            date(2026, 7, 2),

            15,

            timedelta(hours=1, minutes=30),

            300,

            7,

        )

    )

    assert athlete.analytics.total_distance == 25


# ======================================================

def test_total_duration():

    athlete = Athlete()

    athlete.history.add(

        create_workout(

            "Running",

            date(2026, 7, 1),

            10,

            timedelta(hours=1),

            100,

            6,

        )

    )

    athlete.history.add(

        create_workout(

            "Running",

            date(2026, 7, 2),

            15,

            timedelta(hours=2),

            300,

            7,

        )

    )

    assert athlete.analytics.total_duration == timedelta(hours=3)


# ======================================================

def test_total_elevation():

    athlete = Athlete()

    athlete.history.add(

        create_workout(

            "Running",

            date(2026, 7, 1),

            10,

            timedelta(hours=1),

            350,

            6,

        )

    )

    athlete.history.add(

        create_workout(

            "Running",

            date(2026, 7, 2),

            20,

            timedelta(hours=2),

            650,

            7,

        )

    )

    assert athlete.analytics.total_elevation == 1000


# ======================================================

def test_average_rpe():

    athlete = Athlete()

    athlete.history.add(

        create_workout(

            "Running",

            date(2026, 7, 1),

            10,

            timedelta(hours=1),

            100,

            6,

        )

    )

    athlete.history.add(

        create_workout(

            "Running",

            date(2026, 7, 2),

            10,

            timedelta(hours=1),

            100,

            8,

        )

    )

    assert athlete.analytics.average_rpe == 7

# ======================================================

def test_average_rpe_uses_estimated_values():

    athlete = Athlete()

    manual_workout = create_workout(
        "Running",
        date(2026, 7, 1),
        10,
        timedelta(hours=1),
        100,
        6,
    )

    estimated_workout = create_workout(
        "Running",
        date(2026, 7, 2),
        10,
        timedelta(hours=1),
        100,
        None,
    )

    estimated_workout.feedback.estimated_rpe = 8

    athlete.history.add(
        manual_workout
    )

    athlete.history.add(
        estimated_workout
    )

    assert athlete.analytics.average_rpe == 7

# ======================================================

def test_training_days():

    athlete = Athlete()

    athlete.history.add(

        create_workout(

            "Running",

            date(2026, 7, 1),

            5,

            timedelta(minutes=30),

            50,

            5,

        )

    )

    athlete.history.add(

        create_workout(

            "Running",

            date(2026, 7, 1),

            5,

            timedelta(minutes=30),

            50,

            5,

        )

    )

    athlete.history.add(

        create_workout(

            "Running",

            date(2026, 7, 2),

            10,

            timedelta(hours=1),

            100,

            6,

        )

    )

    assert athlete.analytics.training_days == 2


# ======================================================

def test_first_and_last_workout():

    athlete = Athlete()

    first = create_workout(

        "Running",

        date(2026, 7, 1),

        10,

        timedelta(hours=1),

        100,

        6,

    )

    last = create_workout(

        "Running",

        date(2026, 7, 10),

        20,

        timedelta(hours=2),

        500,

        8,

    )

    athlete.history.add(last)

    athlete.history.add(first)

    assert athlete.analytics.first_workout == first

    assert athlete.analytics.last_workout == last


# ======================================================
def test_calculates_hours_since_last_workout_end():

    athlete = Athlete()

    workout = create_workout(
        "Running",
        datetime(
            2026,
            8,
            10,
            6,
            30,
        ),
        10,
        timedelta(
            hours=1,
            minutes=30,
        ),
        100,
        6,
    )

    athlete.history.add(
        workout
    )

    timing = (
        athlete.analytics
        .recovery_timing(
            reference_time=datetime(
                2026,
                8,
                11,
                14,
                0,
            )
        )
    )

    assert (
        timing.last_workout_ended_at
        == datetime(
            2026,
            8,
            10,
            8,
            0,
        )
    )

    assert (
        timing.hours_since_last_workout
        == 30.0
    )


def test_uses_latest_completed_workout():

    athlete = Athlete()

    earlier = create_workout(
        "Running",
        datetime(
            2026,
            8,
            10,
            7,
            0,
        ),
        10,
        timedelta(hours=1),
        100,
        6,
    )

    later = create_workout(
        "Cycling",
        datetime(
            2026,
            8,
            11,
            9,
            0,
        ),
        40,
        timedelta(hours=2),
        300,
        5,
    )

    athlete.history.add(
        later
    )
    athlete.history.add(
        earlier
    )

    timing = (
        athlete.analytics
        .recovery_timing(
            reference_time=datetime(
                2026,
                8,
                11,
                17,
                0,
            )
        )
    )

    assert (
        timing.last_workout_ended_at
        == datetime(
            2026,
            8,
            11,
            11,
            0,
        )
    )

    assert (
        timing.hours_since_last_workout
        == 6.0
    )


def test_handles_workout_ending_after_midnight():

    athlete = Athlete()

    workout = create_workout(
        "Running",
        datetime(
            2026,
            8,
            10,
            23,
            30,
        ),
        15,
        timedelta(hours=2),
        200,
        7,
    )

    athlete.history.add(
        workout
    )

    timing = (
        athlete.analytics
        .recovery_timing(
            reference_time=datetime(
                2026,
                8,
                11,
                4,
                0,
            )
        )
    )

    assert (
        timing.last_workout_ended_at
        == datetime(
            2026,
            8,
            11,
            1,
            30,
        )
    )

    assert (
        timing.hours_since_last_workout
        == 2.5
    )


def test_does_not_invent_time_for_date_only_workout():

    athlete = Athlete()

    workout = create_workout(
        "Running",
        date(
            2026,
            8,
            10,
        ),
        10,
        timedelta(hours=1),
        100,
        6,
    )

    athlete.history.add(
        workout
    )

    timing = (
        athlete.analytics
        .recovery_timing(
            reference_time=datetime(
                2026,
                8,
                11,
                14,
                0,
            )
        )
    )

    assert (
        timing.last_workout_ended_at
        is None
    )

    assert (
        timing.hours_since_last_workout
        is None
    )

def test_intraday_recovery_improves_during_rest_day():

    athlete = Athlete()

    workout = create_workout(
        "Running",
        datetime(
            2026,
            8,
            10,
            7,
            0,
        ),
        10,
        timedelta(hours=1),
        100,
        3,
    )

    athlete.history.add(
        workout
    )

    morning = (
        athlete.analytics
        .time_aware_training_load(
            reference_time=datetime(
                2026,
                8,
                11,
                6,
                0,
            )
        )
    )

    evening = (
        athlete.analytics
        .time_aware_training_load(
            reference_time=datetime(
                2026,
                8,
                11,
                18,
                0,
            )
        )
    )

    assert isinstance(
        morning,
        TimeAwareTrainingLoad,
    )
    assert isinstance(
        evening,
        TimeAwareTrainingLoad,
    )

    assert evening.ctl < morning.ctl
    assert evening.atl < morning.atl

    assert (
        evening.recovery_score
        > morning.recovery_score
    )

def test_intraday_recovery_continues_across_midnight():

    athlete = Athlete()

    workout = create_workout(
        "Running",
        datetime(
            2026,
            8,
            12,
            10,
            0,
        ),
        10,
        timedelta(hours=1),
        100,
        8,
    )

    athlete.history.add(
        workout
    )

    before_midnight = (
        athlete.analytics
        .time_aware_training_load(
            reference_time=datetime(
                2026,
                8,
                13,
                23,
                59,
            )
        )
    )

    after_midnight = (
        athlete.analytics
        .time_aware_training_load(
            reference_time=datetime(
                2026,
                8,
                14,
                0,
                1,
            )
        )
    )

    assert isinstance(
        before_midnight,
        TimeAwareTrainingLoad,
    )

    assert isinstance(
        after_midnight,
        TimeAwareTrainingLoad,
    )

    assert (
        after_midnight.ctl
        <= before_midnight.ctl
    )

    assert (
        after_midnight.atl
        <= before_midnight.atl
    )

    assert (
        after_midnight.tsb
        >= before_midnight.tsb
    )

    assert (
        after_midnight.recovery_score
        >= before_midnight.recovery_score
    )

    assert (
        after_midnight.recovery_score
        - before_midnight.recovery_score
        < 1.0
    )

def test_completed_workout_reduces_intraday_recovery():

    athlete = Athlete()

    workout = create_workout(
        "Running",
        datetime(
            2026,
            8,
            11,
            9,
            0,
        ),
        10,
        timedelta(hours=1),
        100,
        8,
    )

    athlete.history.add(
        workout
    )

    before_completion = (
        athlete.analytics
        .time_aware_training_load(
            reference_time=datetime(
                2026,
                8,
                11,
                9,
                30,
            )
        )
    )

    after_completion = (
        athlete.analytics
        .time_aware_training_load(
            reference_time=datetime(
                2026,
                8,
                11,
                10,
                30,
            )
        )
    )

    assert (
        before_completion
        is not None
    )
    assert (
        after_completion
        is not None
    )

    assert (
        after_completion.recovery_score
        < before_completion.recovery_score
    )


def test_intraday_load_uses_multiple_completed_workouts():

    athlete = Athlete()

    first = create_workout(
        "Running",
        datetime(
            2026,
            8,
            11,
            6,
            0,
        ),
        5,
        timedelta(hours=1),
        50,
        5,
    )

    second = create_workout(
        "Cycling",
        datetime(
            2026,
            8,
            11,
            12,
            0,
        ),
        30,
        timedelta(hours=1),
        100,
        6,
    )

    athlete.history.add(
        first
    )
    athlete.history.add(
        second
    )

    after_first = (
        athlete.analytics
        .time_aware_training_load(
            reference_time=datetime(
                2026,
                8,
                11,
                10,
                0,
            )
        )
    )

    after_second = (
        athlete.analytics
        .time_aware_training_load(
            reference_time=datetime(
                2026,
                8,
                11,
                14,
                0,
            )
        )
    )

    assert after_first is not None
    assert after_second is not None

    assert (
        after_second.atl
        > after_first.atl
    )

    assert (
        after_second.recovery_score
        < after_first.recovery_score
    )


def test_intraday_load_requires_exact_time_today():

    athlete = Athlete()

    workout = create_workout(
        "Running",
        date(
            2026,
            8,
            11,
        ),
        10,
        timedelta(hours=1),
        100,
        7,
    )

    athlete.history.add(
        workout
    )

    result = (
        athlete.analytics
        .time_aware_training_load(
            reference_time=datetime(
                2026,
                8,
                11,
                18,
                0,
            )
        )
    )

    assert result is None

def test_builds_time_aware_training_state():

    athlete = Athlete()

    workout = create_workout(
        "Running",
        datetime(
            2026,
            8,
            11,
            7,
            0,
        ),
        10,
        timedelta(hours=1),
        100,
        5,
    )

    athlete.history.add(
        workout
    )

    reference_time = datetime(
        2026,
        8,
        12,
        14,
        0,
    )

    state = (
        athlete.analytics
        .training_state_at(
            reference_time=(
                reference_time
            )
        )
    )

    assert (
        state.reference_time
        == reference_time
    )
    assert (
        state.hours_since_last_workout
        == 30.0
    )
    assert (
        state.recovery_is_time_aware
        is True
    )

    assert (
        state.ctl
        != athlete.analytics
        .training_state.ctl
    )
    assert (
        state.atl
        != athlete.analytics
        .training_state.atl
    )


def test_time_aware_state_improves_during_rest():

    athlete = Athlete()

    workout = create_workout(
        "Running",
        datetime(
            2026,
            8,
            10,
            7,
            0,
        ),
        10,
        timedelta(hours=1),
        100,
        3,
    )

    athlete.history.add(
        workout
    )

    morning = (
        athlete.analytics
        .training_state_at(
            reference_time=datetime(
                2026,
                8,
                11,
                6,
                0,
            )
        )
    )

    evening = (
        athlete.analytics
        .training_state_at(
            reference_time=datetime(
                2026,
                8,
                11,
                18,
                0,
            )
        )
    )

    assert (
        evening.recovery_score
        > morning.recovery_score
    )

    assert (
        evening.hours_since_last_workout
        > morning.hours_since_last_workout
    )


def test_time_aware_state_falls_back_for_date_only_workout():

    athlete = Athlete()

    workout = create_workout(
        "Running",
        date(
            2026,
            8,
            11,
        ),
        10,
        timedelta(hours=1),
        100,
        6,
    )

    athlete.history.add(
        workout
    )

    daily_state = (
        athlete.analytics.training_state
    )

    result = (
        athlete.analytics
        .training_state_at(
            reference_time=datetime(
                2026,
                8,
                11,
                18,
                0,
            )
        )
    )

    assert (
        result.recovery_is_time_aware
        is False
    )
    assert (
        result.hours_since_last_workout
        is None
    )
    assert result.ctl == daily_state.ctl
    assert result.atl == daily_state.atl
    assert result.tsb == daily_state.tsb
    assert (
        result.recovery_score
        == daily_state.recovery_score
    )


def test_temporal_state_does_not_replace_cached_daily_state():

    athlete = Athlete()

    daily_state = (
        athlete.analytics.training_state
    )

    temporal_state = (
        athlete.analytics
        .training_state_at(
            reference_time=datetime(
                2026,
                8,
                12,
                15,
                0,
            )
        )
    )

    assert temporal_state is not daily_state

    assert (
        athlete.analytics.training_state
        is daily_state
    )

    assert (
        daily_state.reference_time
        is None
    )
    assert (
        daily_state.recovery_is_time_aware
        is False
    )

    
def test_time_aware_recovery_score_is_bounded():

    fresh = TimeAwareTrainingLoad(
        reference_time=datetime(
            2026,
            8,
            11,
            12,
            0,
        ),
        ctl=200,
        atl=0,
    )

    fatigued = TimeAwareTrainingLoad(
        reference_time=datetime(
            2026,
            8,
            11,
            12,
            0,
        ),
        ctl=0,
        atl=200,
    )

    assert fresh.recovery_score == 100
    assert fatigued.recovery_score == 0

def test_summary():

    athlete = Athlete()

    athlete.history.add(

        create_workout(

            "Running",

            date(2026, 7, 1),

            10,

            timedelta(hours=1),

            200,

            7,

        )

    )

    summary = athlete.analytics.summary()

    assert summary["workouts"] == 1

    assert summary["total_distance"] == 10

    assert summary["total_elevation"] == 200

    assert summary["average_rpe"] == 7

# ======================================================

def test_performance_management():

    athlete = Athlete(name="Pedro")

    today = date.today()

    athlete.history.add(

        create_workout(

            "Running",

            today - timedelta(days=4),

            10,

            timedelta(hours=1),

            100,

            5,

        )

    )

    athlete.history.add(

        create_workout(

            "Running",

            today - timedelta(days=2),

            12,

            timedelta(hours=1),

            120,

            6,

        )

    )

    analytics = athlete.analytics

    assert analytics.daily_loads.loads == [

        300,

        0.0,

        360,

        0.0,

        0.0,

    ]

    assert analytics.daily_loads.dates[-1] == today

    assert analytics.pmc is not None

    assert isinstance(

        analytics.ctl,

        float,

    )

    assert isinstance(

        analytics.atl,

        float,

    )

    assert isinstance(

        analytics.tsb,

        float,

    )
    
# ======================================================

def test_current_training_loads_feed_training_state():

    today = date.today()

    athlete = Athlete(name="Pedro")

    athlete.history.add(

        create_workout(

            "Running",

            today - timedelta(days=6),

            10,

            timedelta(hours=1),

            100,

            5,

        )

    )

    athlete.history.add(

        create_workout(

            "Running",

            today,

            12,

            timedelta(hours=1),

            120,

            6,

        )

    )

    analytics = athlete.analytics

    training_state = analytics.training_state

    assert len(analytics.current_training_loads) == 28

    assert analytics.recent_training_load == 660

    assert analytics.acute_training_load == 660 / 7

    assert analytics.chronic_training_load == 660 / 28

    assert training_state.acute_chronic_ratio == 4.0

    weekly_loads = analytics.current_training_loads[-7:]

    expected_monotony = (
        sum(weekly_loads) / 7
    ) / pstdev(weekly_loads)

    assert (
        analytics.training_monotony
        == expected_monotony
    )

    assert (
        training_state.monotony
        == expected_monotony
    )

    assert (
        analytics.training_strain
        == 660 * expected_monotony
    )

    assert (
        training_state.strain
        == 660 * expected_monotony
    )

def test_training_state_refreshes_after_history_change():

    athlete = Athlete(
        name="Pedro"
    )

    initial_state = (
        athlete.analytics.training_state
    )

    athlete.history.add(
        create_workout(
            "Running",
            date.today(),
            10,
            timedelta(hours=1),
            100,
            5,
        )
    )

    refreshed_state = (
        athlete.analytics.training_state
    )

    assert refreshed_state is not initial_state

    assert (
        refreshed_state.recent_training_load
        == 300
    )

def test_typical_weekly_minutes_uses_latest_28_days():

    athlete = Athlete(
        name="Pedro"
    )

    today = date.today()

    for days_ago in (
        3,
        10,
        17,
        24,
    ):
        athlete.history.add(
            create_workout(
                "Running",
                today - timedelta(
                    days=days_ago
                ),
                10,
                timedelta(hours=1),
                100,
                5,
            )
        )

    analytics = athlete.analytics

    assert (
        analytics.typical_weekly_minutes
        == 60
    )

    assert (
        analytics
        .training_state
        .typical_weekly_minutes
        == 60
    )

    assert (
        analytics.typical_weekly_sessions
        == 1
    )

    assert (
        analytics
        .training_state
        .typical_weekly_sessions
        == 1
    )

def test_typical_running_long_session_uses_weekly_longest():

    athlete = Athlete(
        name="Pedro"
    )

    today = date.today()

    running_workouts = (
        (3, 90, 300),
        (5, 60, 500),
        (10, 120, 400),
        (17, 75, 200),
        (24, 105, 350),
    )

    for (
        days_ago,
        minutes,
        elevation_gain,
    ) in running_workouts:

        athlete.history.add(
            create_workout(
                "Running",
                today - timedelta(
                    days=days_ago
                ),
                10,
                timedelta(
                    minutes=minutes
                ),
                elevation_gain,
                5,
            )
        )

    athlete.history.add(
        create_workout(
            "Cycling",
            today - timedelta(days=2),
            60,
            timedelta(hours=4),
            800,
            5,
        )
    )

    athlete.history.add(
        create_workout(
            "Running",
            today - timedelta(days=40),
            25,
            timedelta(hours=3),
            500,
            7,
        )
    )

    analytics = athlete.analytics

    assert (
        analytics
        .typical_running_long_session_minutes
        == 97.5
    )
    assert (
        analytics
        .typical_running_long_session_elevation_gain
        == 312.5
    )

    assert (
        analytics
        .training_state
        .typical_running_long_session_elevation_gain
        == 312.5
    )
    assert (
        analytics
        .typical_running_long_session_effort_pace
        == pytest.approx(
            7.380570818
        )
    )

    assert (
        analytics
        .training_state
        .typical_running_long_session_effort_pace
        == pytest.approx(
            7.380570818
        )
    )
    assert (
        analytics
        .training_state
        .typical_running_long_session_minutes
        == 97.5
    )

def test_builds_performance_profile():

    athlete = Athlete(
        name="Pedro"
    )

    athlete.ftp = 220
    athlete.max_hr = 190
    athlete.resting_hr = 50
    athlete.threshold_hr = 180

    athlete.manual_heart_rate_zones = (

        HeartRateZone(
            name="Z1",
            lower_bpm=120,
            upper_bpm=139,
        ),

        HeartRateZone(
            name="Z2",
            lower_bpm=140,
            upper_bpm=154,
        ),

        HeartRateZone(
            name="Z3",
            lower_bpm=155,
            upper_bpm=169,
        ),

        HeartRateZone(
            name="Z4",
            lower_bpm=170,
            upper_bpm=184,
        ),

        HeartRateZone(
            name="Z5",
            lower_bpm=185,
            upper_bpm=190,
        ),

    )

    profile = (
        athlete.analytics.performance_profile
    )

    assert isinstance(
        profile,
        PerformanceProfile,
    )

    assert profile.ftp == 220
    assert profile.threshold_power == 220
    assert profile.max_hr == 190
    assert profile.resting_hr == 50
    assert profile.threshold_hr == 180
    assert profile.threshold_pace is None

    assert isinstance(
        profile.heart_rate_profile,
        HeartRateProfile,
    )

    assert (
        profile.heart_rate_profile.source
        == "manual"
    )

    assert (
        profile.heart_rate_profile
        .zone("Z4")
        .lower_bpm
        == 170
    )

    assert profile.has_heart_rate_profile

def test_typical_running_pace_uses_recent_running_workouts():

    athlete = Athlete(
        name="Pedro"
    )

    today = date.today()

    athlete.history.add(
        create_workout(
            "Running",
            today - timedelta(days=3),
            10,
            timedelta(minutes=60),
            100,
            5,
        )
    )

    athlete.history.add(
        create_workout(
            "Trail Running",
            today - timedelta(days=10),
            5,
            timedelta(minutes=30),
            200,
            6,
        )
    )

    athlete.history.add(
        create_workout(
            "Cycling",
            today - timedelta(days=2),
            50,
            timedelta(hours=2),
            500,
            5,
        )
    )

    athlete.history.add(
        create_workout(
            "Running",
            today - timedelta(days=40),
            10,
            timedelta(minutes=40),
            100,
            7,
        )
    )

    assert (
        athlete.analytics.typical_running_pace
        == 6.0
    )


def test_typical_running_pace_without_running_data():

    athlete = Athlete(
        name="Pedro"
    )

    athlete.history.add(
        create_workout(
            "Cycling",
            date.today(),
            50,
            timedelta(hours=2),
            500,
            5,
        )
    )

    assert (
        athlete.analytics.typical_running_pace
        is None
    )

def test_typical_easy_running_pace_uses_low_rpe_and_hr():

    athlete = Athlete(
        name="Pedro",
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

    zone_2_workout = create_workout(
        "Running",
        date.today(),
        10,
        timedelta(minutes=60),
        100,
        5.5,
    )

    zone_2_workout.sensors.add(
        "heart_rate",
        [
            {"value": 145},
            {"value": 150},
            {"value": 155},
        ],
    )

    low_zone_3_workout = create_workout(
        "Trail Running",
        date.today() - timedelta(days=7),
        8,
        timedelta(minutes=50),
        200,
        6.0,
    )

    low_zone_3_workout.sensors.add(
        "heart_rate",
        [
            {"value": 158},
            {"value": 160},
            {"value": 162},
        ],
    )

    hard_workout = create_workout(
        "Running",
        date.today() - timedelta(days=3),
        10,
        timedelta(minutes=50),
        50,
        8.0,
    )

    hard_workout.sensors.add(
        "heart_rate",
        [
            {"value": 175},
            {"value": 180},
        ],
    )

    athlete.history.add(
        zone_2_workout
    )

    athlete.history.add(
        low_zone_3_workout
    )

    athlete.history.add(
        hard_workout
    )

    expected_pace = (
        110
        / (
            10
            + 1
            + 8
            + 2
        )
    )

    assert (
        athlete.analytics
        .typical_easy_running_pace
        == pytest.approx(
            expected_pace
        )
    )

    assert (
        athlete.analytics
        .training_state
        .typical_easy_running_pace
        == pytest.approx(
            expected_pace
        )
    )

def test_typical_easy_running_pace_requires_easy_data():

    athlete = Athlete(
        name="Pedro",
        max_hr=205,
        resting_hr=65,
    )

    workout = create_workout(
        "Running",
        date.today(),
        10,
        timedelta(minutes=50),
        50,
        8.0,
    )

    workout.sensors.add(
        "heart_rate",
        [
            {"value": 180},
            {"value": 185},
        ],
    )

    athlete.history.add(
        workout
    )

    assert (
        athlete.analytics
        .typical_easy_running_pace
        is None
    )

    assert (
        athlete.analytics
        .training_state
        .typical_easy_running_pace
        == 0.0
    )

def test_road_10k_performance_pace_uses_hard_high_hr_run():

    athlete = Athlete(
        name="Pedro",
        max_hr=200,
    )

    race_workout = create_workout(
        "Running",
        date.today(),
        10.16,
        timedelta(minutes=50.3),
        89,
        9.8,
    )

    race_workout.info.title = (
        "S. Silvestre 2025"
    )

    race_workout.sensors.add(
        "heart_rate",
        [
            {"value": 180},
            {"value": 189},
            {"value": 197},
        ],
    )

    easy_workout = create_workout(
        "Running",
        date.today(),
        10.0,
        timedelta(minutes=60),
        50,
        5.5,
    )

    easy_workout.info.title = "Easy Run"

    easy_workout.sensors.add(
        "heart_rate",
        [
            {"value": 145},
            {"value": 150},
            {"value": 155},
        ],
    )

    athlete.history.add(
        race_workout
    )

    athlete.history.add(
        easy_workout
    )

    assert (
        athlete.analytics
        .road_10k_performance_pace
        == pytest.approx(
            50.3
            / (
                10.16
                + 0.89
            )
        )
    )
    expected_raw_pace = (
        50.3 / 10.16
    )

    expected_lt2_pace = (
        5
        + 5 / 60
    )

    assert (
        athlete.analytics
        .road_10k_raw_performance_pace
        == pytest.approx(
            expected_raw_pace
        )
    )

    assert (
        athlete.analytics
        .lt2_running_pace
        == pytest.approx(
            expected_lt2_pace
        )
    )

    assert (
        athlete.analytics
        .performance_profile
        .threshold_pace
        == pytest.approx(
            expected_lt2_pace
        )
    )
    expected_tempo_pace = (
        5
        + 15 / 60
    )

    assert (
        athlete.analytics
        .performance_profile
        .tempo_pace
        == pytest.approx(
            expected_tempo_pace
        )
    )

def test_road_10k_performance_pace_requires_high_effort():

    athlete = Athlete(
        name="Pedro",
        max_hr=200,
    )

    easy_workout = create_workout(
        "Running",
        date.today(),
        10.0,
        timedelta(minutes=55),
        50,
        5.0,
    )

    easy_workout.sensors.add(
        "heart_rate",
        [
            {"value": 145},
            {"value": 150},
        ],
    )

    athlete.history.add(
        easy_workout
    )

    assert (
        athlete.analytics
        .road_10k_performance_pace
        is None
    )

def test_estimates_road_10k_from_performance_pace():

    athlete = Athlete(
        name="Pedro",
        max_hr=200,
    )

    performance_workout = create_workout(
        "Running",
        date.today(),
        10.16,
        timedelta(minutes=50.3),
        89,
        9.8,
    )

    performance_workout.info.title = (
        "S. Silvestre 2025"
    )

    performance_workout.sensors.add(
        "heart_rate",
        [
            {"value": 180},
            {"value": 189},
            {"value": 197},
        ],
    )

    athlete.history.add(
        performance_workout
    )

    event = Event(
        name="Sealand",
        sport="Road Running",
        distance=10,
        elevation_gain=113,
    )

    performance_pace = (
        50.3
        / (
            10.16
            + 0.89
        )
    )

    expected_duration = (
        event.estimated_duration_at_pace(
            performance_pace
        )
    )

    duration = (
        athlete.analytics
        .estimated_event_duration(
            event
        )
    )

    assert duration == expected_duration

def test_estimates_event_duration_from_recent_running_pace():

    athlete = Athlete(
        name="Pedro"
    )

    athlete.history.add(
        create_workout(
            "Running",
            date.today(),
            10,
            timedelta(minutes=60),
            100,
            6,
        )
    )

    event = Event(
        name="III Trail Pé Firme",
        sport="Trail Running",
        distance=23,
        elevation_gain=950,
    )

    duration = (
        athlete.analytics
        .estimated_event_duration(
            event
        )
    )

    assert duration == timedelta(
        hours=3,
        minutes=15,
    )


def test_event_duration_without_running_history_is_unknown():

    athlete = Athlete(
        name="Pedro"
    )

    event = Event(
        sport="Road Running",
        distance=10,
        elevation_gain=100,
    )

    assert (
        athlete.analytics
        .estimated_event_duration(
            event
        )
        is None
    )

# ======================================================

def test_analytics_calculates_heart_rate_zones():

    athlete = Athlete(
        name="Pedro",
        max_hr=190,
        resting_hr=50,
    )

    profile = (
        athlete.analytics
        .heart_rate_profile
    )

    assert isinstance(
        profile,
        HeartRateProfile,
    )

    assert profile.source == "karvonen"
    assert profile.has_zones
    assert profile.zone("Z4") is not None


# ======================================================

def test_manual_heart_rate_zones_take_precedence():

    athlete = Athlete(
        name="Pedro",
        max_hr=190,
        resting_hr=50,
        manual_heart_rate_zones=(

            HeartRateZone(
                name="Z4",
                lower_bpm=168,
                upper_bpm=182,
            ),

        ),
    )

    profile = (
        athlete.analytics
        .heart_rate_profile
    )

    assert profile is not None
    assert profile.source == "manual"

    assert (
        profile.zone("Z4").lower_bpm
        == 168
    )