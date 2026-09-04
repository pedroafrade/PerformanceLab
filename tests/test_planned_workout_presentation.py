from datetime import datetime, timedelta

from performancelab.training.planning import PlannedWorkout


def test_collapses_legacy_long_run_for_presentation():

    workout = PlannedWorkout(
        scheduled_at=datetime(2026, 9, 6),
        sport="Trail Running",
        title="Long Run",
        duration=timedelta(minutes=100),
        structure=(
            "Warm up 10 min",
            "Long aerobic run on hilly terrain 85 min",
            "Target elevation gain: 450 m D+",
            "Cool down 5 min",
            "Heart rate target: Z2 · 121–156 bpm",
        ),
    )

    assert workout.presentation_structure == (
        "Long aerobic run on hilly terrain 1h40",
        "Target elevation gain: 450 m D+",
        "Heart rate target: Z2 · 121–156 bpm",
    )


def test_keeps_non_continuous_session_structure():

    workout = PlannedWorkout(
        scheduled_at=datetime(2026, 9, 8),
        sport="Trail Running",
        title="LT2 Run",
        duration=timedelta(minutes=43),
        structure=(
            "Warm up 10 min",
            "3×8 min at LT2",
            "Recover 2 min easy between repetitions",
            "Cool down 5 min",
        ),
    )

    assert (
        workout.presentation_structure
        == workout.structure
    )
