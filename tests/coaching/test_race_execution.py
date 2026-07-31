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
        sport="Cycling",
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
                "Z3",
                157,
                176,
            ),
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

    assert "First 10 min" in plan.pacing[0]
    assert "157–176 bpm" in plan.pacing[0]
    assert "164 bpm" in plan.pacing[0]

    assert "Minutes 10–35" in plan.pacing[1]
    assert "LT2 (177 bpm)" in plan.pacing[1]

    assert "Minutes 35–45" in plan.pacing[2]
    assert "184 bpm" in plan.pacing[2]
    assert "from 187 bpm" in plan.pacing[2]

    assert "Final 5 min" in plan.pacing[3]
    assert "observed, not chased" in plan.pacing[3]


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

def test_road_10k_segments_follow_expected_duration():

    event = SimpleNamespace(
        sport="Road Running",
        distance=10,
    )

    plan = build_race_execution_plan(
        event=event,
        expected_duration=timedelta(
            minutes=45,
        ),
    )

    assert plan is not None

    assert "First 9 min" in plan.pacing[0]
    assert "Minutes 9–32" in plan.pacing[1]
    assert "Minutes 32–41" in plan.pacing[2]
    assert "Final 4 min" in plan.pacing[3]

def test_builds_long_trail_execution_plan():

    event = SimpleNamespace(
        sport="Trail Running",
        distance=23,
    )

    profile = HeartRateProfile(
        max_hr=205,
        resting_hr=65,
        threshold_hr=177,
        zones=(
            HeartRateZone(
                "Z3",
                157,
                176,
            ),
        ),
        source="manual",
    )

    plan = build_race_execution_plan(
        event=event,
        expected_duration=timedelta(
            minutes=201,
        ),
        heart_rate_profile=profile,
    )

    assert plan is not None

    assert "First 40 min" in plan.pacing[0]
    assert "164 bpm" in plan.pacing[0]

    assert "Minutes 40–141" in plan.pacing[1]
    assert "157–176 bpm" in plan.pacing[1]
    assert "LT2 (177 bpm)" in plan.pacing[1]

    assert "Minutes 141–181" in plan.pacing[2]
    assert "Final 20 min" in plan.pacing[3]

    assert any(
        "1.5–2.0 L"
        in step
        for step in plan.hydration
    )

    assert any(
        "1350–2000 mg"
        in step
        for step in plan.hydration
    )

    assert any(
        "80 g of carbohydrate per hour"
        in step
        for step in plan.nutrition
    )

    assert any(
        "about 270 g"
        in step
        for step in plan.nutrition
    )

    assert any(
        "6 gels"
        in step
        for step in plan.nutrition
    )