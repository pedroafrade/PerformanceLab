from datetime import timedelta
from types import SimpleNamespace

from performancelab.coaching import (
    RaceExecutionPlan,
    build_race_execution_plan,
)


def test_builds_road_10k_execution_plan():

    event = SimpleNamespace(
        sport="Road Running",
        distance=10,
    )

    plan = build_race_execution_plan(
        event=event,
        expected_duration=timedelta(
            minutes=50,
        ),
    )

    assert isinstance(
        plan,
        RaceExecutionPlan,
    )

    assert plan.expected_duration == timedelta(
        minutes=50,
    )

    assert len(plan.pacing) == 4
    assert len(plan.hydration) == 2
    assert len(plan.nutrition) == 2

    assert "5:00/km" in plan.pacing[0]


def test_execution_plan_guidance_preserves_order():

    event = SimpleNamespace(
        sport="Road Running",
        distance=10,
    )

    plan = build_race_execution_plan(
        event=event,
        expected_duration=timedelta(
            minutes=50,
        ),
    )

    assert plan is not None

    assert plan.guidance == (
        *plan.pacing,
        *plan.hydration,
        *plan.nutrition,
    )


def test_unsupported_event_has_no_execution_plan():

    event = SimpleNamespace(
        sport="Trail Running",
        distance=23,
    )

    plan = build_race_execution_plan(
        event=event,
        expected_duration=timedelta(
            hours=3,
        ),
    )

    assert plan is None


def test_missing_duration_has_no_execution_plan():

    event = SimpleNamespace(
        sport="Road Running",
        distance=10,
    )

    plan = build_race_execution_plan(
        event=event,
        expected_duration=None,
    )

    assert plan is None