"""
PerformanceLab

Tests for the Development presenter.
"""

from datetime import (
    date,
    datetime,
    timedelta,
)

from performancelab import (
    Athlete,
    create_workout,
)
from performancelab.presentation import (
    DevelopmentData,
    DevelopmentPresenter,
)


def test_builds_empty_development_data():

    athlete = Athlete(
        name="Pedro"
    )

    result = DevelopmentPresenter(
        athlete
    ).build()

    assert isinstance(
        result,
        DevelopmentData,
    )

    assert result.dates == ()
    assert result.daily_load == ()
    assert result.fitness == ()
    assert result.fatigue == ()
    assert result.form == ()

    assert result.current_fitness == 0.0
    assert result.current_fatigue == 0.0
    assert result.current_form == 0.0


def test_builds_immutable_development_series():

    athlete = Athlete(
        name="Pedro"
    )

    today = date.today()

    athlete.history.add(
        create_workout(
            sport="Running",
            workout_date=(
                today
                - timedelta(days=3)
            ),
            distance=10.0,
            elevation_gain=0.0,
            duration=timedelta(
                minutes=60,
            ),
            rpe=5,
            title="Easy Run",
        )
    )

    athlete.history.add(
        create_workout(
            sport="Running",
            workout_date=(
                today
                - timedelta(days=2)
            ),
            distance=15.0,
            elevation_gain=0.0,
            duration=timedelta(
                minutes=90,
            ),
            rpe=7,
            title="Long Run",
        )
    )

    result = DevelopmentPresenter(
        athlete
    ).build()

    assert result.dates == (
        today - timedelta(days=3),
        today - timedelta(days=2),
        today - timedelta(days=1),
        today,
    )

    assert result.daily_load == (
        300,
        630,
        0.0,
        0.0,
    )

    assert isinstance(
        result.fitness,
        tuple,
    )
    assert isinstance(
        result.fatigue,
        tuple,
    )
    assert isinstance(
        result.form,
        tuple,
    )

    assert len(result.fitness) == 4
    assert len(result.fatigue) == 4
    assert len(result.form) == 4

    assert (
        result.current_fitness
        == result.fitness[-1]
    )
    assert (
        result.current_fatigue
        == result.fatigue[-1]
    )
    assert (
        result.current_form
        == result.form[-1]
    )

def test_exposes_recovery_and_load_guidance():

    athlete = Athlete(
        name="Pedro"
    )

    result = DevelopmentPresenter(
        athlete
    ).build()

    assert (
        result.recovery_status
        == athlete.analytics
        .training_state
        .recovery_status
    )

    assert (
        result.recovery_recommendation
        == athlete.analytics
        .training_state
        .recovery_recommendation
    )

    assert isinstance(
        result.recovery_score,
        float,
    )
    assert isinstance(
        result.acute_load,
        float,
    )
    assert isinstance(
        result.chronic_load,
        float,
    )
    assert isinstance(
        result.ramp_rate,
        float,
    )
    
def test_exposes_time_aware_current_state():

    athlete = Athlete(
        name="Pedro"
    )

    workout = create_workout(
        sport="Running",
        workout_date=datetime(
            2026,
            8,
            11,
            7,
            0,
        ),
        distance=10.0,
        elevation_gain=100.0,
        duration=timedelta(
            hours=1,
        ),
        rpe=3.0,
        title="Easy Run",
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

    result = (
        DevelopmentPresenter(
            athlete
        ).build(
            reference_time=(
                reference_time
            )
        )
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
        result.current_fitness
        == state.ctl
    )
    assert (
        result.current_fatigue
        == state.atl
    )
    assert (
        result.current_form
        == state.tsb
    )
    assert (
        result.recovery_score
        == state.recovery_score
    )
    assert (
        result.recovery_status
        == state.recovery_status
    )
    assert (
        result.recovery_reference_time
        == reference_time
    )
    assert (
        result.hours_since_last_workout
        == 30.0
    )
    assert (
        result.recovery_is_time_aware
        is True
    )


def test_preserves_daily_development_series():

    athlete = Athlete(
        name="Pedro"
    )

    reference_day = date.today()

    workout_day = (
        reference_day
        - timedelta(
            days=1,
        )
    )

    workout = create_workout(
        sport="Running",
        workout_date=datetime.combine(
            workout_day,
            datetime.min.time(),
        ).replace(
            hour=7,
        ),
        distance=10.0,
        elevation_gain=100.0,
        duration=timedelta(
            hours=1,
        ),
        rpe=3.0,
        title="Easy Run",
    )

    athlete.history.add(
        workout
    )

    result = (
        DevelopmentPresenter(
            athlete
        ).build(
            reference_time=(
                datetime.combine(
                    reference_day,
                    datetime.min.time(),
                ).replace(
                    hour=14,
                )
            )
        )
    )

    assert result.dates == (
        workout_day,
        reference_day,
    )

    assert result.daily_load == (
        180.0,
        0.0,
    )

    assert len(result.fitness) == 2
    assert len(result.fatigue) == 2
    assert len(result.form) == 2

    assert (
        result.current_fitness
        != result.fitness[-1]
    )
    assert (
        result.current_fatigue
        != result.fatigue[-1]
    )


def test_development_falls_back_to_daily_state():

    athlete = Athlete(
        name="Pedro"
    )

    workout = create_workout(
        sport="Running",
        workout_date=date(
            2026,
            8,
            12,
        ),
        distance=10.0,
        elevation_gain=100.0,
        duration=timedelta(
            hours=1,
        ),
        rpe=6.0,
        title="Run without time",
    )

    athlete.history.add(
        workout
    )

    result = (
        DevelopmentPresenter(
            athlete
        ).build(
            reference_time=datetime(
                2026,
                8,
                12,
                18,
                0,
            )
        )
    )

    daily_state = (
        athlete.analytics.training_state
    )

    assert (
        result.recovery_is_time_aware
        is False
    )
    assert (
        result.hours_since_last_workout
        is None
    )
    assert (
        result.current_fitness
        == daily_state.ctl
    )
    assert (
        result.current_fatigue
        == daily_state.atl
    )
    assert (
        result.current_form
        == daily_state.tsb
    )

def test_aggregates_completed_volume_by_sport():

    athlete = Athlete(
        name="Pedro"
    )

    today = date.today()

    athlete.history.add(
        create_workout(
            sport="Trail Running",
            workout_date=today,
            distance=12.0,
            elevation_gain=400.0,
            duration=timedelta(
                minutes=90,
            ),
            rpe=5,
            title="Trail Run",
        )
    )

    athlete.history.add(
        create_workout(
            sport="Trail Running",
            workout_date=(
                today
                - timedelta(days=1)
            ),
            distance=8.0,
            elevation_gain=200.0,
            duration=timedelta(
                minutes=60,
            ),
            rpe=4,
            title="Easy Trail",
        )
    )

    athlete.history.add(
        create_workout(
            sport="Cycling",
            workout_date=(
                today
                - timedelta(days=2)
            ),
            distance=40.0,
            elevation_gain=300.0,
            duration=timedelta(
                minutes=120,
            ),
            rpe=5,
            title="Bike",
        )
    )

    result = (
        DevelopmentPresenter(
            athlete
        ).build()
    )

    assert (
        len(
            result.sport_volume
        )
        == 2
    )

    assert (
        result.sport_volume[0]
        .sport
        == "Trail Running"
    )

    assert (
        result.sport_volume[0]
        .duration_seconds
        == 9000.0
    )

    assert (
        result.sport_volume[0]
        .distance
        == 20.0
    )

    assert (
        result.sport_volume[0]
        .sessions
        == 2
    )

    assert (
        result.sport_volume[1]
        .sport
        == "Cycling"
    )

    assert (
        result.sport_volume[1]
        .duration_seconds
        == 7200.0
    )

def test_builds_heart_rate_zone_distribution():

    athlete = Athlete(
        name="Pedro",
        max_hr=190,
        resting_hr=50,
    )

    today = date.today()

    workout = create_workout(
        sport="Running",
        workout_date=today,
        distance=5.0,
        elevation_gain=0.0,
        duration=timedelta(
            minutes=30,
        ),
        rpe=6,
        title="Run",
    )

    workout.sensors.add(
        "heart_rate",
        [
            {
                "time": (
                    "2026-08-07T08:00:00"
                ),
                "value": 130,
            },
            {
                "time": (
                    "2026-08-07T08:00:10"
                ),
                "value": 145,
            },
            {
                "time": (
                    "2026-08-07T08:00:20"
                ),
                "value": 160,
            },
        ],
    )

    athlete.history.add(
        workout
    )

    result = (
        DevelopmentPresenter(
            athlete
        ).build()
    )

    assert (
        result.intensity
        is not None
    )

    assert (
        len(
            result.intensity.zones
        )
        == 5
    )

    assert (
        result.intensity
        .heart_rate_seconds
        > 0
    )

    assert (
        result.intensity
        .average_rpe
        == 6.0
    )

def test_builds_performance_references():

    athlete = Athlete(
        name="Pedro",
        max_hr=190,
        resting_hr=50,
        threshold_hr=177,
        ftp=220,
    )

    result = (
        DevelopmentPresenter(
            athlete
        ).build()
    )

    references = (
        result
        .performance_references
    )

    assert references is not None

    assert (
        references.threshold_hr
        == 177
    )

    assert (
        references.ftp
        == 220
    )