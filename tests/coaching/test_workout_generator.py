from datetime import date

import pytest

from types import SimpleNamespace

from performancelab.analysis import (
    HeartRateProfile,
    HeartRateZone,
)

from performancelab.coaching import (
    DEFAULT_WORKOUT_TEMPLATES,
    PRE_RACE_TEMPLATE,
    LONG_TEMPLATE,
    RACE_TEMPLATE,
    RECOVERY_TEMPLATE,
    REST_TEMPLATE,
    WorkoutTemplate,
    CROSS_TRAINING_TEMPLATE,
)

from performancelab.coaching.session_purpose import (
    SessionPurpose,
)
from performancelab.coaching.workout_templates import (
    EASY_TEMPLATE,
    TECHNIQUE_TEMPLATE,
    INTENSITY_TEMPLATE,
    THRESHOLD_TEMPLATE,
    VO2MAX_TEMPLATE,
    TEMPO_TEMPLATE,
    HILLS_TEMPLATE,
    SPEED_TEMPLATE,
    SHAKEOUT_TEMPLATE,
    template_for,
)

from performancelab.coaching.strategy import StrategyPlan
from performancelab.coaching.training_focus import TrainingFocus

from performancelab.coaching.workout_generator import (
    WorkoutGenerator,
)


def test_creates_workout_template() -> None:

    template = WorkoutTemplate(
        purpose=SessionPurpose.EASY,
        title="Easy Run",
        objective="Aerobic endurance",
        intensity="Easy",
        description="Run comfortably.",
        structure=(
            "Warm-up",
            "Continuous running",
            "Cool-down",
        ),
        equipment=(
            "Running shoes",
        ),
        sport="running",
    )

    assert template.purpose is SessionPurpose.EASY
    assert template.title == "Easy Run"
    assert template.objective == "Aerobic endurance"
    assert template.intensity == "Easy"
    assert template.description == "Run comfortably."
    assert template.sport == "running"

    assert template.structure == (
        "Warm-up",
        "Continuous running",
        "Cool-down",
    )

    assert template.equipment == (
        "Running shoes",
    )


def test_template_is_immutable() -> None:

    template = WorkoutTemplate(
        purpose=SessionPurpose.EASY,
        title="Easy Session",
        objective="Aerobic endurance",
        intensity="Easy",
    )

    with pytest.raises(
        AttributeError,
    ):

        template.title = "Changed"


@pytest.mark.parametrize(
    "field_name",
    (
        "title",
        "objective",
        "intensity",
    ),
)
def test_required_text_cannot_be_empty(
    field_name: str,
) -> None:

    values = {
        "purpose": SessionPurpose.EASY,
        "title": "Easy Session",
        "objective": "Aerobic endurance",
        "intensity": "Easy",
    }

    values[field_name] = "   "

    with pytest.raises(
        ValueError,
        match=(
            f"{field_name} cannot be empty"
        ),
    ):

        WorkoutTemplate(**values)


def test_purpose_must_be_session_purpose() -> None:

    with pytest.raises(
        TypeError,
        match=(
            "purpose must be a SessionPurpose"
        ),
    ):

        WorkoutTemplate(
            purpose="easy",
            title="Easy Session",
            objective="Aerobic endurance",
            intensity="Easy",
        )


def test_structure_must_be_tuple() -> None:

    with pytest.raises(
        TypeError,
        match="structure must be a tuple",
    ):

        WorkoutTemplate(
            purpose=SessionPurpose.EASY,
            title="Easy Session",
            objective="Aerobic endurance",
            intensity="Easy",
            structure=[
                "Warm-up",
            ],
        )


def test_structure_must_contain_strings() -> None:

    with pytest.raises(
        TypeError,
        match=(
            "structure must contain strings"
        ),
    ):

        WorkoutTemplate(
            purpose=SessionPurpose.EASY,
            title="Easy Session",
            objective="Aerobic endurance",
            intensity="Easy",
            structure=(
                "Warm-up",
                10,
            ),
        )


def test_structure_cannot_contain_empty_values() -> None:

    with pytest.raises(
        ValueError,
        match=(
            "structure cannot contain empty values"
        ),
    ):

        WorkoutTemplate(
            purpose=SessionPurpose.EASY,
            title="Easy Session",
            objective="Aerobic endurance",
            intensity="Easy",
            structure=(
                "Warm-up",
                "",
            ),
        )


def test_equipment_must_be_tuple() -> None:

    with pytest.raises(
        TypeError,
        match="equipment must be a tuple",
    ):

        WorkoutTemplate(
            purpose=SessionPurpose.EASY,
            title="Easy Session",
            objective="Aerobic endurance",
            intensity="Easy",
            equipment=[
                "Shoes",
            ],
        )


def test_for_sport_returns_new_template() -> None:

    original = WorkoutTemplate(
        purpose=SessionPurpose.EASY,
        title="Easy Session",
        objective="Aerobic endurance",
        intensity="Easy",
    )

    running = original.for_sport(
        "running"
    )

    assert running is not original
    assert original.sport is None
    assert running.sport == "running"

    assert running.purpose is original.purpose
    assert running.title == original.title
    assert running.objective == original.objective
    assert running.intensity == original.intensity
    assert running.structure == original.structure


def test_for_sport_rejects_empty_sport() -> None:

    template = WorkoutTemplate(
        purpose=SessionPurpose.EASY,
        title="Easy Session",
        objective="Aerobic endurance",
        intensity="Easy",
    )

    with pytest.raises(
        ValueError,
        match="sport cannot be empty",
    ):

        template.for_sport("   ")

def test_shakeout_structure_has_explicit_duration() -> None:

    assert SHAKEOUT_TEMPLATE.structure == (
        "Easy running 10 min",
        (
            "4×20 sec relaxed strides with full "
            "easy recovery (5 min block)"
        ),
        "Easy running 5 min",
    )

@pytest.mark.parametrize(
    (
        "purpose",
        "expected",
    ),
    (
        (
            SessionPurpose.REST,
            REST_TEMPLATE,
        ),
        (
            SessionPurpose.RECOVERY,
            RECOVERY_TEMPLATE,
        ),
        (
            SessionPurpose.EASY,
            EASY_TEMPLATE,
        ),
        (
            SessionPurpose.PRE_RACE,
            PRE_RACE_TEMPLATE,
        ),
        (
            SessionPurpose.INTENSITY,
            INTENSITY_TEMPLATE,
        ),
        (
            SessionPurpose.LONG,
            LONG_TEMPLATE,
        ),
        (
            SessionPurpose.RACE,
            RACE_TEMPLATE,
        ),
        (
            SessionPurpose.CROSS_TRAINING,
            CROSS_TRAINING_TEMPLATE,
        ),
    ),
)

def test_returns_default_template(
    purpose: SessionPurpose,
    expected: WorkoutTemplate,
) -> None:

    assert template_for(
        purpose
    ) is expected


def test_catalog_contains_every_purpose() -> None:

    assert set(
        DEFAULT_WORKOUT_TEMPLATES
    ) == set(
        SessionPurpose
    )


def test_catalog_is_immutable() -> None:

    with pytest.raises(
        TypeError,
    ):

        DEFAULT_WORKOUT_TEMPLATES[
            SessionPurpose.EASY
        ] = REST_TEMPLATE


def test_template_for_rejects_invalid_purpose() -> None:

    with pytest.raises(
        TypeError,
        match=(
            "purpose must be a SessionPurpose"
        ),
    ):

        template_for("easy")


def test_repr_contains_useful_information() -> None:

    template = WorkoutTemplate(
        purpose=SessionPurpose.LONG,
        title="Long Run",
        objective="Endurance",
        intensity="Easy",
        sport="running",
    )

    representation = repr(template)

    assert "WorkoutTemplate" in representation
    assert "'long'" in representation
    assert "'Long Run'" in representation
    assert "'running'" in representation


def make_strategy_plan(
    **overrides,
) -> StrategyPlan:

    values = {
        "strategy": "BuildStrategy",
        "phase": "Build",
        "volume_factor": 1.0,
        "target_sessions": 5,
        "intensity_sessions": 1,
        "long_sessions": 1,
        "recovery_days": 2,
    }

    values.update(overrides)

    return StrategyPlan(**values)


def test_customizes_template_with_strategy_plan():

    template = WorkoutTemplate(
        purpose=SessionPurpose.INTENSITY,
        title="Quality Session",
        objective="Develop aerobic power.",
        intensity="Hard",
        description="Complete the intervals with control.",
        structure=(
            "Warm-up",
            "Main intervals",
            "Cool-down",
        ),
    )

    strategy_plan = make_strategy_plan(
        focus="threshold",
        objectives=(
            "Develop sustainable speed.",
        ),
        guidelines=(
            "Keep the opening repetitions controlled.",
        ),
        warnings=(
            "Monitor accumulated fatigue.",
        ),
    )

    customized = template.customized_for(
        strategy_plan
    )

    assert customized is not template

    assert customized.purpose is template.purpose
    assert customized.title == template.title
    assert customized.intensity == template.intensity
    assert customized.structure == template.structure

    assert (
        "Develop sustainable speed."
        in customized.objective
    )

    description = customized.description.lower()

    assert "threshold" in description
    assert "main work" in description
    assert "controlled pacing" in description
    assert "opening repetitions controlled" in description
    assert "accumulated fatigue" in description


def test_customization_enriches_empty_template_description():

    template = WorkoutTemplate(
        purpose=SessionPurpose.EASY,
        title="Easy Session",
        objective="Develop aerobic endurance.",
        intensity="Easy",
    )

    customized = template.customized_for(
        make_strategy_plan()
    )

    assert customized.objective == template.objective
    assert customized.description
    assert (
        "comfortably aerobic"
        in customized.description.lower()
    )
    assert customized.structure == template.structure


def test_rejects_invalid_strategy_plan():

    template = WorkoutTemplate(
        purpose=SessionPurpose.EASY,
        title="Easy Session",
        objective="Develop aerobic endurance.",
        intensity="Easy",
    )

    with pytest.raises(
        TypeError,
        match="strategy_plan",
    ):
        template.customized_for(
            object()
        )

def test_returns_threshold_template_for_threshold_focus():

    template = template_for(
        SessionPurpose.INTENSITY,
        focus="threshold",
    )

    assert template is THRESHOLD_TEMPLATE
    assert template.title == "LT2 Session"
    assert template.purpose is SessionPurpose.INTENSITY


def test_focus_matching_is_normalized():

    template = template_for(
        SessionPurpose.INTENSITY,
        focus=" Threshold ",
    )

    assert template is THRESHOLD_TEMPLATE


def test_returns_default_when_focus_has_no_template():

    template = template_for(
        SessionPurpose.INTENSITY,
        focus="aerobic endurance",
    )

    assert template is INTENSITY_TEMPLATE


def test_focus_does_not_override_another_purpose():

    template = template_for(
        SessionPurpose.EASY,
        focus="threshold",
    )

    assert template is EASY_TEMPLATE


def test_rejects_invalid_focus_type():

    with pytest.raises(
        TypeError,
        match="focus",
    ):
        template_for(
            SessionPurpose.INTENSITY,
            focus=123,
        )


def test_rejects_empty_focus():

    with pytest.raises(
        ValueError,
        match="focus",
    ):
        template_for(
            SessionPurpose.INTENSITY,
            focus="   ",
        )


def test_returns_vo2max_template_for_vo2max_focus() -> None:

    template = template_for(
        SessionPurpose.INTENSITY,
        focus="vo2max",
    )

    assert template is VO2MAX_TEMPLATE
    assert template.title == "VO₂max Session"
    assert template.intensity == "Very hard"

def test_returns_tempo_template_for_tempo_focus() -> None:

    template = template_for(
        SessionPurpose.INTENSITY,
        focus="tempo",
    )

    assert template is TEMPO_TEMPLATE
    assert template.title == "Tempo Session"
    assert template.intensity == "Hard"

def test_returns_hills_template_for_hills_focus() -> None:

    template = template_for(
        SessionPurpose.INTENSITY,
        focus="hills",
    )

    assert template is HILLS_TEMPLATE
    assert template.title == "Hill Session"
    assert template.intensity == "Hard"

def test_returns_speed_template_for_speed_focus() -> None:

    template = template_for(
        SessionPurpose.INTENSITY,
        focus="speed",
    )

    assert template is SPEED_TEMPLATE
    assert template.title == "Speed Session"
    assert template.intensity == "Very hard"

def test_selects_target_event_sport_before_history_sports() -> None:

    context = SimpleNamespace(
        next_event=SimpleNamespace(
            event=SimpleNamespace(
                sport="Road Running",
            ),
        ),
        sports=(
            "Cycling",
            "Running",
        ),
    )

    sport = WorkoutGenerator._select_sport(
        context
    )

    assert sport == "Road Running"

def test_selects_phase_event_sport_before_primary_event() -> None:

    context = SimpleNamespace(
        phase_event=SimpleNamespace(
            event=SimpleNamespace(
                sport="Road Running",
            ),
        ),
        primary_event=SimpleNamespace(
            event=SimpleNamespace(
                sport="Trail Running",
            ),
        ),
        next_event=SimpleNamespace(
            event=SimpleNamespace(
                sport="Road Running",
            ),
        ),
        sports=(
            "Cycling",
            "Running",
        ),
    )

    sport = WorkoutGenerator._select_sport(
        context
    )

    assert sport == "Road Running"

def test_selects_primary_event_sport_before_next_event() -> None:

    context = SimpleNamespace(
        primary_event=SimpleNamespace(
            event=SimpleNamespace(
                sport="Trail Running",
            ),
        ),
        next_event=SimpleNamespace(
            event=SimpleNamespace(
                sport="Road Running",
            ),
        ),
        sports=(
            "Cycling",
            "Running",
        ),
    )

    sport = WorkoutGenerator._select_sport(
        context
    )

    assert sport == "Trail Running"

def test_uses_history_sport_without_target_event() -> None:

    context = SimpleNamespace(
        next_event=None,
        sports=(
            "Cycling",
            "Running",
        ),
    )

    sport = WorkoutGenerator._select_sport(
        context
    )

    assert sport == "Cycling"

@pytest.mark.parametrize(
    (
        "sport",
        "expected_title",
    ),
    (
        (
            "Road Running",
            "Easy Run",
        ),
        (
            "Cycling",
            "Easy Ride",
        ),
        (
            "Swimming",
            "Easy Swim",
        ),
    ),
)

def test_builds_sport_specific_workout_title(
    sport,
    expected_title,
) -> None:

    template = EASY_TEMPLATE.for_sport(
        sport
    )

    title = (
        WorkoutGenerator._sport_specific_title(
            template
        )
    )

    assert title == expected_title

def test_builds_sport_specific_long_title():

    template = LONG_TEMPLATE.for_sport(
        "Trail Running"
    )

    title = (
        WorkoutGenerator._sport_specific_title(
            template
        )
    )

    assert title == "Long Run"


def test_threshold_workout_structure_matches_duration():

    structure = (
        WorkoutGenerator._intensity_structure(
            template=(
                THRESHOLD_TEMPLATE.for_sport(
                    "Trail Running"
                )
            ),
            duration_minutes=70,
            coach_context=SimpleNamespace(
                athlete=SimpleNamespace(
                    threshold_hr=177,
                ),
            ),
        )
    )

    assert structure == (
        "Warm up 16 min",
        "3×13 min at LT2 (177 bpm)",
        (
            "Recover 2 min easy "
            "between repetitions"
        ),
        "Cool down 11 min",
    )

def test_lt2_workout_has_prescription_summary():

    workout = WorkoutGenerator()._build_workout(
        slot=SimpleNamespace(
            purpose=SessionPurpose.INTENSITY,
            duration_minutes=70,
        ),
        scheduled_day=date(
            2026,
            8,
            4,
        ),
        template=THRESHOLD_TEMPLATE.for_sport(
            "Trail Running"
        ),
        coach_context=SimpleNamespace(
            athlete=SimpleNamespace(
                threshold_hr=177,
            ),
        ),
        strategy_plan=make_strategy_plan(
            key_session_focus="threshold",
        ),
    )

    assert workout.title == "LT2 Run"

    assert (
        workout.prescription_summary
        == "3×13 min at LT2 (177 bpm)"
    )

def test_vo2max_workout_distributes_complementary_time():

    structure = (
        WorkoutGenerator._intensity_structure(
            template=(
                VO2MAX_TEMPLATE.for_sport(
                    "Road Running"
                )
            ),
            duration_minutes=70,
            coach_context=SimpleNamespace(),
        )
    )

    assert structure == (
        "Warm up 25 min",
        "6×3 min at VO₂max effort",
        (
            "Recover 2 min easy "
            "between repetitions"
        ),
        "Cool down 17 min",
    )

def test_speed_workout_distributes_complementary_time():

    structure = (
        WorkoutGenerator._intensity_structure(
            template=(
                SPEED_TEMPLATE.for_sport(
                    "Road Running"
                )
            ),
            duration_minutes=50,
            coach_context=SimpleNamespace(),
        )
    )

    assert structure == (
        "Warm up 18 min",
        "10×30 sec fast",
        (
            "Recover 90 sec easy "
            "after each repetition"
        ),
        "Cool down 12 min",
    )

def test_builds_mountainous_hill_structure():

    structure, complementary_minutes = (
        WorkoutGenerator._hill_steps(
            35,
            elevation_demand="mountainous",
        )
    )

    assert structure == (
        "5×5 min uphill",
        (
            "Recover 2 min easy downhill "
            "between repetitions"
        ),
    )

    assert complementary_minutes == 2


def test_builds_hilly_event_hill_structure():

    structure, complementary_minutes = (
        WorkoutGenerator._hill_steps(
            35,
            elevation_demand="hilly",
        )
    )

    assert structure == (
        "6×3 min uphill",
        (
            "Recover 2 min easy downhill "
            "between repetitions"
        ),
    )

    assert complementary_minutes == 7


def test_builds_rolling_event_hill_structure():

    structure, complementary_minutes = (
        WorkoutGenerator._hill_steps(
            35,
            elevation_demand="rolling",
        )
    )

    assert structure == (
        "10×1 min uphill",
        (
            "Recover 1 min easy downhill "
            "between repetitions"
        ),
    )

    assert complementary_minutes == 16


def test_mountainous_hill_structure_adapts_to_short_session():

    structure, complementary_minutes = (
        WorkoutGenerator._hill_steps(
            15,
            elevation_demand="mountainous",
        )
    )

    assert structure == (
        "3×3 min uphill",
        (
            "Recover 2 min easy downhill "
            "between repetitions"
        ),
    )

    assert complementary_minutes == 2

def test_hill_workout_structure_matches_duration():

    structure = (
        WorkoutGenerator._intensity_structure(
            template=HILLS_TEMPLATE.for_sport(
                "Trail Running"
            ),
            duration_minutes=70,
            coach_context=SimpleNamespace(),
            elevation_demand="mountainous",
        )
    )

    assert structure == (
        "Warm up 22 min",
        "5×5 min uphill",
        (
            "Recover 2 min easy downhill "
            "between repetitions"
        ),
        "Cool down 15 min",
    )

def test_hill_workout_has_prescription_summary():

    workout = WorkoutGenerator()._build_workout(
        slot=SimpleNamespace(
            purpose=SessionPurpose.INTENSITY,
            duration_minutes=70,
        ),
        scheduled_day=date(
            2026,
            8,
            11,
        ),
        template=HILLS_TEMPLATE.for_sport(
            "Trail Running"
        ),
        coach_context=SimpleNamespace(),
        strategy_plan=make_strategy_plan(
            elevation_demand="rolling",
        ),
    )

    assert (
        workout.prescription_summary
        == "10×60 sec uphill"
    )

def test_builds_mountainous_long_run_structure():

    structure = WorkoutGenerator._long_structure(
        duration_minutes=120,
        sport="Trail Running",
        elevation_demand="mountainous",
        target_elevation_gain=450,
    )

    assert structure == (
        "Warm up 10 min",
        (
            "Long aerobic run on mountainous "
            "terrain 105 min"
        ),
        "Target elevation gain: 450 m D+",
        (
            "Keep climbs aerobic and use purposeful "
            "hiking on steep gradients"
        ),
        (
            "Practise controlled downhill technique "
            "without racing descents"
        ),
        "Cool down 5 min",
    )


def test_builds_hilly_long_run_structure():

    structure = WorkoutGenerator._long_structure(
        duration_minutes=120,
        sport="Trail Running",
        elevation_demand="hilly",
    )

    assert structure == (
        "Warm up 10 min",
        (
            "Long aerobic run on hilly "
            "terrain 105 min"
        ),
        (
            "Keep sustained climbs aerobic and "
            "descend with controlled technique"
        ),
        "Cool down 5 min",
    )


def test_flat_long_run_keeps_standard_structure():

    structure = WorkoutGenerator._long_structure(
        duration_minutes=120,
        sport="Road Running",
        elevation_demand="flat",
    )

    assert structure == (
        "Warm up 10 min",
        "Long aerobic run 105 min",
        "Cool down 5 min",
    )

def test_builds_pre_race_running_title() -> None:

    template = PRE_RACE_TEMPLATE.for_sport(
        "Trail Running"
    )

    title = (
        WorkoutGenerator._sport_specific_title(
            template
        )
    )

    assert title == "Pre-Race Easy Run"

def test_builds_duration_aware_pre_race_structure():

    template = (
        PRE_RACE_TEMPLATE.for_sport(
            "Trail Running"
        )
    )

    structure = (
        WorkoutGenerator._prescribed_structure(
            template=template,
            duration_minutes=40,
            coach_context=SimpleNamespace(),
            strategy_plan=SimpleNamespace(),
        )
    )

    assert structure == (
        "Warm up 10 min",
        "Easy aerobic run 20 min",
        (
            "4×20 sec relaxed strides with "
            "full easy recovery (5 min block)"
        ),
        "Cool down 5 min",
    )

def test_copies_long_elevation_target_to_planned_workout():

    strategy_plan = make_strategy_plan(
        long_session_elevation_gain=450,
    )

    workout = WorkoutGenerator()._build_workout(
        slot=SimpleNamespace(
            purpose=SessionPurpose.LONG,
            duration_minutes=120,
        ),
        scheduled_day=date(
            2026,
            8,
            2,
        ),
        template=LONG_TEMPLATE.for_sport(
            "Trail Running"
        ),
        coach_context=SimpleNamespace(
            training_state=SimpleNamespace(
                typical_running_long_session_effort_pace=(
                    7.5
                ),
            ),
        ),
        strategy_plan=strategy_plan,
    )

    assert workout.elevation_gain == 450

    assert workout.distance == 12

    assert (
        "Target elevation gain: 450 m D+"
        in workout.structure
    )

def test_copies_strategy_phase_to_planned_workout():

    strategy_plan = make_strategy_plan(
        phase="Peak",
    )

    workout = WorkoutGenerator()._build_workout(
        slot=SimpleNamespace(
            purpose=SessionPurpose.EASY,
            duration_minutes=45,
        ),
        scheduled_day=date(
            2026,
            8,
            20,
        ),
        template=EASY_TEMPLATE.for_sport(
            "Trail Running"
        ),
        coach_context=SimpleNamespace(),
        strategy_plan=strategy_plan,
    )

    assert workout.phase == "Peak"

def test_race_week_easy_session_is_taper():

    phase = WorkoutGenerator._phase_for_slot(
        phase="Race",
        purpose=SessionPurpose.EASY,
    )

    assert phase == "Taper"


def test_competition_session_keeps_race_phase():

    phase = WorkoutGenerator._phase_for_slot(
        phase="Race",
        purpose=SessionPurpose.RACE,
    )

    assert phase == "Race"

def test_builds_duration_aware_technique_structure():

    template = (
        TECHNIQUE_TEMPLATE.for_sport(
            "Trail Running"
        )
    )

    structure = (
        WorkoutGenerator._prescribed_structure(
            template=template,
            duration_minutes=40,
            coach_context=SimpleNamespace(),
            strategy_plan=SimpleNamespace(
                elevation_demand="mountainous",
            ),
        )
    )

    assert structure == (
        "Warm up 10 min",
        (
            "Easy aerobic run on varied "
            "terrain 15 min"
        ),
        (
            "Controlled climbing and relaxed "
            "descending technique 10 min"
        ),
        "Cool down 5 min",
    )

def test_race_structure_keeps_full_event_duration():

    structure = (
        WorkoutGenerator._race_structure(
            duration_minutes=50,
        )
    )

    assert structure == (
        "Warm up 8 min",
        "Race effort 50 min",
        "Cool down 5 min",
    )

def test_easy_workout_uses_athlete_z2():

    heart_rate_profile = HeartRateProfile(
        max_hr=205,
        resting_hr=65,
        threshold_hr=177,
        zones=(

            HeartRateZone(
                name="Z1",
                lower_bpm=1,
                upper_bpm=120,
            ),

            HeartRateZone(
                name="Z2",
                lower_bpm=121,
                upper_bpm=156,
            ),

            HeartRateZone(
                name="Z3",
                lower_bpm=157,
                upper_bpm=176,
            ),

            HeartRateZone(
                name="Z4",
                lower_bpm=177,
                upper_bpm=186,
            ),

            HeartRateZone(
                name="Z5",
                lower_bpm=187,
                upper_bpm=205,
            ),

        ),
        source="manual",
    )

    workout = WorkoutGenerator()._build_workout(
        slot=SimpleNamespace(
            purpose=SessionPurpose.EASY,
            duration_minutes=50,
        ),
        scheduled_day=date(
            2026,
            8,
            5,
        ),
        template=EASY_TEMPLATE.for_sport(
            "Road Running"
        ),
        coach_context=SimpleNamespace(
            heart_rate_profile=(
                heart_rate_profile
            ),
        ),
        strategy_plan=make_strategy_plan(),
    )

    assert (
        workout.structure[-1]
        == (
            "Heart rate target: "
            "Z2 · 121–156 bpm"
        )
    )

def test_easy_workout_uses_easy_pace_for_summary():

    workout = WorkoutGenerator()._build_workout(
        slot=SimpleNamespace(
            purpose=SessionPurpose.EASY,
            duration_minutes=60,
        ),
        scheduled_day=date(
            2026,
            8,
            6,
        ),
        template=EASY_TEMPLATE.for_sport(
            "Road Running"
        ),
        coach_context=SimpleNamespace(
            training_state=SimpleNamespace(
                typical_easy_running_pace=6.0,
            ),
        ),
        strategy_plan=make_strategy_plan(),
    )

    assert workout.distance == 10

    assert (
        workout.prescription_summary
        == "10 km · Z2"
    )

def test_easy_running_pace_is_not_used_for_cycling():

    workout = WorkoutGenerator()._build_workout(
        slot=SimpleNamespace(
            purpose=SessionPurpose.EASY,
            duration_minutes=60,
        ),
        scheduled_day=date(
            2026,
            8,
            6,
        ),
        template=EASY_TEMPLATE.for_sport(
            "Cycling"
        ),
        coach_context=SimpleNamespace(
            training_state=SimpleNamespace(
                typical_easy_running_pace=6.0,
            ),
        ),
        strategy_plan=make_strategy_plan(),
    )

    assert workout.distance is None

    assert (
        workout.prescription_summary
        is None
    )

def test_workout_keeps_semantic_zone_without_profile():

    workout = WorkoutGenerator()._build_workout(
        slot=SimpleNamespace(
            purpose=SessionPurpose.RECOVERY,
            duration_minutes=20,
        ),
        scheduled_day=date(
            2026,
            8,
            5,
        ),
        template=RECOVERY_TEMPLATE.for_sport(
            "Road Running"
        ),
        coach_context=SimpleNamespace(),
        strategy_plan=make_strategy_plan(),
    )

    assert (
        workout.structure[-1]
        == "Heart rate target: Z1"
    )


def test_race_has_no_generic_heart_rate_target():

    guidance = (
        WorkoutGenerator
        ._heart_rate_guidance(
            purpose=SessionPurpose.RACE,
            strategy_plan=make_strategy_plan(),
            coach_context=SimpleNamespace(),
        )
    )

    assert guidance is None

def test_tempo_uses_threshold_heart_rate_range():

    guidance = (
        WorkoutGenerator
        ._heart_rate_guidance(
            purpose=SessionPurpose.INTENSITY,
            strategy_plan=make_strategy_plan(
                focus="tempo",
            ),
            coach_context=SimpleNamespace(
                heart_rate_profile=(
                    SimpleNamespace(
                        threshold_hr=177,
                    )
                ),
            ),
        )
    )

    assert guidance == (
        "Heart rate target: "
        "Z3–Z4 · 168–175 bpm"
    )


def test_threshold_uses_threshold_heart_rate_range():

    guidance = (
        WorkoutGenerator
        ._heart_rate_guidance(
            purpose=SessionPurpose.INTENSITY,
            strategy_plan=make_strategy_plan(
                focus="threshold",
            ),
            coach_context=SimpleNamespace(
                heart_rate_profile=(
                    SimpleNamespace(
                        threshold_hr=177,
                    )
                ),
            ),
        )
    )

    assert guidance == (
        "Heart rate target: "
        "Z4 · 177–181 bpm"
    )