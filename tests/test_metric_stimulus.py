from datetime import (
    datetime,
    timedelta,
)
from types import SimpleNamespace

from performancelab.training.planning.metric_stimulus import (
    metric_workout_stimulus,
)
from performancelab.training.planning import (
    WorkoutStimulus,
)
from performancelab.workout import Workout


def test_recognises_three_by_eight_minutes_at_lt2():

    workout = Workout()

    workout.info.duration = timedelta(
        minutes=60
    )

    start = datetime(
        2026,
        9,
        6,
        8,
        0,
    )

    samples = []

    elapsed = 0

    for block in range(3):

        for second in range(8 * 60):
            samples.append(
                {
                    "time": (
                        start
                        + timedelta(
                            seconds=elapsed
                        )
                    ).isoformat(),
                    "value": 178,
                }
            )
            elapsed += 1

        if block < 2:

            for second in range(3 * 60):
                samples.append(
                    {
                        "time": (
                            start
                            + timedelta(
                                seconds=elapsed
                            )
                        ).isoformat(),
                        "value": 140,
                    }
                )
                elapsed += 1

    workout.sensors.add(
        "heart_rate",
        samples,
    )

    profile = SimpleNamespace(
        threshold_hr=180,
        max_hr=195,
    )

    assert (
        metric_workout_stimulus(
            workout,
            heart_rate_profile=profile,
        )
        is WorkoutStimulus.THRESHOLD
    )