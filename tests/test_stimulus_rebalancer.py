"""
Tests for safe stimulus rebalancing suggestions.
"""

from datetime import date, datetime, timedelta
from types import SimpleNamespace

from performancelab.training.planning import (
    PlannedWorkout,
    StimulusRebalancer,
    WorkoutStimulus,
)


def workout(
    day,
    *,
    title,
    purpose,
    focus=None,
    phase="Peak",
):
    return PlannedWorkout(
        scheduled_at=datetime(
            2026,
            9,
            day,
            8,
            0,
        ),
        sport="Trail Running",
        title=title,
        duration=timedelta(
            minutes=60,
        ),
        intensity=(
            "Hard"
            if purpose == "intensity"
            else "Easy"
        ),
        purpose=purpose,
        focus=focus,
        phase=phase,
    )


def gap(
    source,
    *,
    planned,
    completed,
):
    return SimpleNamespace(
        planned_workout=source,
        has_stimulus_gap=True,
        planned_stimulus=planned,
        completed_stimulus=completed,
    )


def ready_state():
    return SimpleNamespace(
        can_tolerate_intensity=True,
    )


def test_hills_gap_uses_future_intensity_slot():

    source = workout(
        2,
        title="Hill Run",
        purpose="intensity",
        focus="hills",
    )

    tempo = workout(
        7,
        title="Tempo Run",
        purpose="intensity",
        focus="tempo",
    )

    long_run = workout(
        9,
        title="Long Run",
        purpose="long",
    )

    race = workout(
        13,
        title="Race",
        purpose="race",
        phase="Race",
    )

    suggestions = (
        StimulusRebalancer()
        .suggest(
            workouts=(
                source,
                tempo,
                long_run,
                race,
            ),
            outcomes=(
                gap(
                    source,
                    planned=(
                        WorkoutStimulus.HILLS
                    ),
                    completed=(
                        WorkoutStimulus.TEMPO
                    ),
                ),
            ),
            training_state=ready_state(),
            reference_day=date(
                2026,
                9,
                3,
            ),
        )
    )

    assert len(suggestions) == 1

    suggestion = suggestions[0]

    assert (
        suggestion.missing_stimulus
        is WorkoutStimulus.HILLS
    )
    assert (
        suggestion.candidate_workout_day
        == date(2026, 9, 7)
    )
    assert "Long Run is preserved" in (
        suggestion.rationale
    )


def test_lt2_gap_does_not_replace_long_run():

    source = workout(
        2,
        title="LT2 Run",
        purpose="intensity",
        focus="threshold",
    )

    long_run = workout(
        6,
        title="Long Run",
        purpose="long",
    )

    race = workout(
        13,
        title="Race",
        purpose="race",
        phase="Race",
    )

    suggestions = (
        StimulusRebalancer()
        .suggest(
            workouts=(
                source,
                long_run,
                race,
            ),
            outcomes=(
                gap(
                    source,
                    planned=(
                        WorkoutStimulus.THRESHOLD
                    ),
                    completed=(
                        WorkoutStimulus.EASY
                    ),
                ),
            ),
            training_state=ready_state(),
            reference_day=date(
                2026,
                9,
                3,
            ),
        )
    )

    assert suggestions == ()


def test_does_not_suggest_intensity_during_fatigue():

    source = workout(
        2,
        title="Hill Run",
        purpose="intensity",
        focus="hills",
    )

    tempo = workout(
        7,
        title="Tempo Run",
        purpose="intensity",
        focus="tempo",
    )

    suggestions = (
        StimulusRebalancer()
        .suggest(
            workouts=(
                source,
                tempo,
            ),
            outcomes=(
                gap(
                    source,
                    planned=(
                        WorkoutStimulus.HILLS
                    ),
                    completed=(
                        WorkoutStimulus.TEMPO
                    ),
                ),
            ),
            training_state=(
                SimpleNamespace(
                    can_tolerate_intensity=False,
                )
            ),
            reference_day=date(
                2026,
                9,
                3,
            ),
        )
    )

    assert suggestions == ()


def test_does_not_use_slot_too_close_to_race():

    source = workout(
        2,
        title="Hill Run",
        purpose="intensity",
        focus="hills",
    )

    tempo = workout(
        11,
        title="Tempo Run",
        purpose="intensity",
        focus="tempo",
    )

    race = workout(
        13,
        title="Race",
        purpose="race",
        phase="Race",
    )

    suggestions = (
        StimulusRebalancer()
        .suggest(
            workouts=(
                source,
                tempo,
                race,
            ),
            outcomes=(
                gap(
                    source,
                    planned=(
                        WorkoutStimulus.HILLS
                    ),
                    completed=(
                        WorkoutStimulus.TEMPO
                    ),
                ),
            ),
            training_state=ready_state(),
            reference_day=date(
                2026,
                9,
                3,
            ),
        )
    )

    assert suggestions == ()