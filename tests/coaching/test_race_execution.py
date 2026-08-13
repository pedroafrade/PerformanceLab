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
from performancelab.analysis import (
    NutritionProfile,
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
        "No athlete-tested carbohydrate intake"
        in step
        for step in plan.nutrition
    )

    assert any(
        "30–60 g of carbohydrate per hour"
        in step
        for step in plan.nutrition
    )

    assert any(
        "approximately 100–200 g in total"
        in step
        for step in plan.nutrition
    )

    assert any(
        "Do not assume that 80–90 g/h is tolerated"
        in step
        for step in plan.nutrition
    )

def test_long_trail_uses_athlete_nutrition_profile():

    event = SimpleNamespace(
        sport="Trail Running",
        distance=23,
    )

    nutrition_profile = NutritionProfile(
        carbohydrate_per_hour=70,
        fluid_lower_ml_per_hour=500,
        fluid_upper_ml_per_hour=700,
        sodium_lower_mg_per_hour=600,
        sodium_upper_mg_per_hour=800,
        gel_carbohydrate_grams=20,
        pre_race_carbohydrate_lower=70,
        pre_race_carbohydrate_upper=90,
        source="athlete-tested",
    )

    plan = build_race_execution_plan(
        event=event,
        expected_duration=timedelta(
            hours=2,
        ),
        nutrition_profile=nutrition_profile,
    )

    assert plan is not None

    assert any(
        "1.0–1.4 L"
        in step
        for step in plan.hydration
    )

    assert any(
        "500–700 ml/h"
        in step
        for step in plan.hydration
    )

    assert any(
        "1200–1600 mg"
        in step
        for step in plan.hydration
    )

    assert any(
        "600–800 mg/h"
        in step
        for step in plan.hydration
    )

    assert any(
        "70–90 g"
        in step
        for step in plan.nutrition
    )

    assert any(
        "athlete-tested target of 70 g"
        in step
        for step in plan.nutrition
    )

    assert any(
        "about 140 g"
        in step
        for step in plan.nutrition
    )

    assert any(
        "4 gels of 20 g"
        in step
        for step in plan.nutrition
    )