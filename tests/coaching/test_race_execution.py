from datetime import timedelta
from types import SimpleNamespace

from performancelab.coaching import (
    RaceExecutionPlan,
    build_race_execution_plan,
)

from performancelab.analysis.heart_rate_profile import (
    HeartRateProfile,
    HeartRateZone,
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

def test_road_10k_uses_athlete_heart_rate_zones():

    event = SimpleNamespace(
        sport="Road Running",
        distance=10,
    )

    profile = HeartRateProfile(
        max_hr=205,
        resting_hr=65,
        threshold_hr=177,
        zones=(
            HeartRateZone(
                "Z4",
                177,
                186,
            ),
            HeartRateZone(
                "Z5",
                187,
                205,
            ),
        ),
        source="manual",
    )

    plan = build_race_execution_plan(
        event=event,
        expected_duration=timedelta(
            minutes=50,
        ),
        heart_rate_profile=profile,
    )

    assert plan is not None

    assert "177–186 bpm" in plan.pacing[0]
    assert "181–186 bpm" in plan.pacing[1]
    assert "187–192 bpm" in plan.pacing[2]
    assert "from 187 bpm" in plan.pacing[3]


def test_road_10k_without_zones_keeps_pace_guidance():

    event = SimpleNamespace(
        sport="Road Running",
        distance=10,
    )

    plan = build_race_execution_plan(
        event=event,
        expected_duration=timedelta(
            minutes=50,
        ),
        heart_rate_profile=None,
    )

    assert plan is not None
    assert "5:00/km" in plan.pacing[0]
    assert not any(
        "Heart-rate guide"
        in step
        for step in plan.pacing
    )