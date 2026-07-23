import pytest

from performancelab.coaching import (
    DEFAULT_WORKOUT_TEMPLATES,
    EASY_TEMPLATE,
    INTENSITY_TEMPLATE,
    LONG_TEMPLATE,
    RACE_TEMPLATE,
    RECOVERY_TEMPLATE,
    REST_TEMPLATE,
    SessionPurpose,
    WorkoutTemplate,
    template_for,
    CROSS_TRAINING_TEMPLATE,
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