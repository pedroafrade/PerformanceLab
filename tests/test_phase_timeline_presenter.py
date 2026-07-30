from datetime import date, datetime

from performancelab.presentation.planning_presenter import (
    PlanningPresenter,
)
from performancelab.training.planning import (
    PlannedWorkout,
    TrainingPlan,
    WeeklyPlan,
)


def test_builds_complete_phase_timeline():

    training_plan = TrainingPlan(
        start_date=date(
            2026,
            9,
            7,
        ),
        end_date=date(
            2026,
            9,
            20,
        ),
    )

    taper_workout = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            9,
            10,
        ),
        title="Quality Run",
        phase="Taper",
    )

    race = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            9,
            13,
        ),
        title="Race",
        intensity="Race effort",
        phase="Taper",
    )

    recovery_workout = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            9,
            16,
        ),
        title="Recovery Run",
        phase="Recovery",
    )

    training_plan.add(
        taper_workout
    )
    training_plan.add(
        race
    )
    training_plan.add(
        recovery_workout
    )

    weekly_plan = WeeklyPlan(
        start_date=date(
            2026,
            9,
            7,
        ),
        end_date=date(
            2026,
            9,
            13,
        ),
        workouts=[
            taper_workout,
            race,
        ],
    )

    data = PlanningPresenter(
        plan=weekly_plan,
        training_plan=training_plan,
        reference=datetime(
            2026,
            9,
            10,
        ),
    ).build()

    timeline = data.phase_timeline

    assert timeline is not None

    assert timeline.start_date == date(
        2026,
        9,
        7,
    )

    assert timeline.end_date == date(
        2026,
        9,
        20,
    )

    assert len(
        timeline.days
    ) == 14

    phases = {
        item.day: item.phase
        for item in timeline.days
    }

    assert phases[
        date(
            2026,
            9,
            11,
        )
    ] == "Taper"

    assert phases[
        date(
            2026,
            9,
            13,
        )
    ] == "Race"

    assert phases[
        date(
            2026,
            9,
            15,
        )
    ] == "Recovery"