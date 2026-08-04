"""
PerformanceLab

Tests for the Development presenter.
"""

from datetime import date, timedelta

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