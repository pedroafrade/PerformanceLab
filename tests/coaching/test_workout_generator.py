from datetime import date

import pytest

from types import SimpleNamespace

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
    assert template.title == "Threshold Session"
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
            "Easy Aerobic Run",
        ),
        (
            "Cycling",
            "Easy Aerobic Ride",
        ),
        (
            "Swimming",
            "Easy Aerobic Swim",
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

def test_builds_mountainous_hill_structure():

    structure = WorkoutGenerator._hill_steps(
        35,
        elevation_demand="mountainous",
    )

    assert structure == (
        "5×5 min uphill",
        (
            "Recover 2 min easy downhill "
            "between repetitions"
        ),
    )


def test_builds_hilly_event_hill_structure():

    structure = WorkoutGenerator._hill_steps(
        35,
        elevation_demand="hilly",
    )

    assert structure == (
        "6×3 min uphill",
        (
            "Recover 2 min easy downhill "
            "between repetitions"
        ),
    )


def test_builds_rolling_event_hill_structure():

    structure = WorkoutGenerator._hill_steps(
        35,
        elevation_demand="rolling",
    )

    assert structure == (
        "10×1 min uphill",
        (
            "Recover 1 min easy downhill "
            "between repetitions"
        ),
    )


def test_mountainous_hill_structure_adapts_to_short_session():

    structure = WorkoutGenerator._hill_steps(
        15,
        elevation_demand="mountainous",
    )

    assert structure == (
        "3×3 min uphill",
        (
            "Recover 2 min easy downhill "
            "between repetitions"
        ),
    )

def test_builds_mountainous_long_run_structure():

    structure = WorkoutGenerator._long_structure(
        duration_minutes=120,
        sport="Trail Running",
        elevation_demand="mountainous",
    )

    assert structure == (
        "Warm up 10 min",
        (
            "Long aerobic run on mountainous "
            "terrain 105 min"
        ),
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