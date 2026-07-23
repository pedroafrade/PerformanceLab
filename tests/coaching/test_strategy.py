"""
Tests for coaching strategy abstractions.

Place this file at:
    tests/coaching/test_strategy.py
"""

from types import SimpleNamespace

import pytest

from performancelab.coaching.strategy import (
    CoachStrategy,
    StrategyPlan,
)


def make_strategy_plan(
    **overrides,
) -> StrategyPlan:
    values = {
        "strategy": "BuildStrategy",
        "phase": "Build",
        "volume_factor": 1.05,
        "target_sessions": 5,
        "intensity_sessions": 2,
        "long_sessions": 1,
        "recovery_days": 2,
    }
    values.update(overrides)

    return StrategyPlan(**values)


# ======================================================
# Construction and concrete weekly targets
# ======================================================


def test_creates_strategy_plan_with_required_fields():
    plan = make_strategy_plan()

    assert plan.strategy == "BuildStrategy"
    assert plan.phase == "Build"
    assert plan.volume_factor == 1.05
    assert plan.target_sessions == 5
    assert plan.intensity_sessions == 2
    assert plan.long_sessions == 1
    assert plan.recovery_days == 2


def test_uses_empty_tuple_defaults():
    plan = make_strategy_plan()

    assert plan.objectives == ()
    assert plan.guidelines == ()
    assert plan.warnings == ()


def test_supports_concrete_weekly_targets():
    plan = make_strategy_plan(
        focus="threshold",
        target_weekly_minutes=420,
        target_weekly_load=480.0,
        long_session_minutes=120,
    )

    assert plan.focus == "threshold"
    assert plan.target_weekly_minutes == 420
    assert plan.target_weekly_load == 480.0
    assert plan.long_session_minutes == 120


def test_supports_objectives_guidelines_and_warnings():
    plan = make_strategy_plan(
        objectives=(
            "Develop threshold capacity.",
            "Maintain aerobic endurance.",
        ),
        guidelines=(
            "Separate intensity sessions.",
        ),
        warnings=(
            "Monitor accumulated fatigue.",
        ),
    )

    assert len(plan.objectives) == 2
    assert plan.guidelines == (
        "Separate intensity sessions.",
    )
    assert plan.warnings == (
        "Monitor accumulated fatigue.",
    )


def test_strategy_plan_is_immutable():
    plan = make_strategy_plan()

    with pytest.raises(
        AttributeError,
    ):
        plan.phase = "Taper"


# ======================================================
# Derived properties
# ======================================================


def test_calculates_session_distribution():
    plan = make_strategy_plan()

    assert plan.training_days == 5
    assert plan.rest_days == 2
    assert plan.easy_sessions == 2


def test_reports_intensity_and_long_session_presence():
    plan = make_strategy_plan()

    assert plan.has_intensity is True
    assert plan.has_long_session is True


def test_reports_absence_of_intensity_and_long_sessions():
    plan = make_strategy_plan(
        intensity_sessions=0,
        long_sessions=0,
    )

    assert plan.has_intensity is False
    assert plan.has_long_session is False
    assert plan.easy_sessions == 5


def test_easy_sessions_never_becomes_negative():
    plan = make_strategy_plan(
        target_sessions=1,
        intensity_sessions=1,
        long_sessions=1,
    )

    assert plan.easy_sessions == 0


# ======================================================
# Text validation
# ======================================================


@pytest.mark.parametrize(
    "field",
    [
        "strategy",
        "phase",
    ],
)
def test_rejects_non_string_required_text(
    field,
):
    with pytest.raises(
        TypeError,
        match=field,
    ):
        make_strategy_plan(
            **{field: 123},
        )


@pytest.mark.parametrize(
    "field",
    [
        "strategy",
        "phase",
    ],
)
def test_rejects_empty_required_text(
    field,
):
    with pytest.raises(
        ValueError,
        match=field,
    ):
        make_strategy_plan(
            **{field: "   "},
        )


def test_rejects_non_string_focus():
    with pytest.raises(
        TypeError,
        match="focus",
    ):
        make_strategy_plan(
            focus=123,
        )


def test_rejects_empty_focus():
    with pytest.raises(
        ValueError,
        match="focus",
    ):
        make_strategy_plan(
            focus=" ",
        )


# ======================================================
# Numeric validation
# ======================================================


@pytest.mark.parametrize(
    "value",
    [
        "1.0",
        object(),
        True,
    ],
)
def test_rejects_invalid_volume_factor_type(
    value,
):
    with pytest.raises(
        TypeError,
        match="volume_factor",
    ):
        make_strategy_plan(
            volume_factor=value,
        )


def test_rejects_negative_volume_factor():
    with pytest.raises(
        ValueError,
        match="volume_factor",
    ):
        make_strategy_plan(
            volume_factor=-0.1,
        )


@pytest.mark.parametrize(
    "field",
    [
        "target_sessions",
        "intensity_sessions",
        "long_sessions",
        "recovery_days",
    ],
)
def test_rejects_negative_session_counts(
    field,
):
    with pytest.raises(
        ValueError,
        match=field,
    ):
        make_strategy_plan(
            **{field: -1},
        )


@pytest.mark.parametrize(
    "field",
    [
        "target_sessions",
        "intensity_sessions",
        "long_sessions",
        "recovery_days",
    ],
)
@pytest.mark.parametrize(
    "value",
    [
        1.5,
        "1",
        True,
    ],
)
def test_rejects_invalid_session_count_types(
    field,
    value,
):
    with pytest.raises(
        TypeError,
        match=field,
    ):
        make_strategy_plan(
            **{field: value},
        )


def test_rejects_more_than_seven_sessions():
    with pytest.raises(
        ValueError,
        match="target_sessions cannot exceed 7",
    ):
        make_strategy_plan(
            target_sessions=8,
        )


def test_rejects_more_than_seven_recovery_days():
    with pytest.raises(
        ValueError,
        match="recovery_days cannot exceed 7",
    ):
        make_strategy_plan(
            recovery_days=8,
        )


def test_rejects_intensity_sessions_above_target_sessions():
    with pytest.raises(
        ValueError,
        match="intensity_sessions cannot exceed",
    ):
        make_strategy_plan(
            target_sessions=2,
            intensity_sessions=3,
            long_sessions=0,
        )


def test_rejects_long_sessions_above_target_sessions():
    with pytest.raises(
        ValueError,
        match="long_sessions cannot exceed",
    ):
        make_strategy_plan(
            target_sessions=1,
            intensity_sessions=0,
            long_sessions=2,
        )


# ======================================================
# Optional weekly targets
# ======================================================


@pytest.mark.parametrize(
    "field",
    [
        "target_weekly_minutes",
        "long_session_minutes",
    ],
)
def test_rejects_negative_optional_minutes(
    field,
):
    with pytest.raises(
        ValueError,
        match=field,
    ):
        make_strategy_plan(
            **{field: -1},
        )


@pytest.mark.parametrize(
    "field",
    [
        "target_weekly_minutes",
        "long_session_minutes",
    ],
)
@pytest.mark.parametrize(
    "value",
    [
        1.5,
        "60",
        True,
    ],
)
def test_rejects_invalid_optional_minutes_type(
    field,
    value,
):
    with pytest.raises(
        TypeError,
        match=field,
    ):
        make_strategy_plan(
            **{field: value},
        )


@pytest.mark.parametrize(
    "value",
    [
        "480",
        object(),
        True,
    ],
)
def test_rejects_invalid_weekly_load_type(
    value,
):
    with pytest.raises(
        TypeError,
        match="target_weekly_load",
    ):
        make_strategy_plan(
            target_weekly_load=value,
        )


def test_rejects_negative_weekly_load():
    with pytest.raises(
        ValueError,
        match="target_weekly_load",
    ):
        make_strategy_plan(
            target_weekly_load=-1.0,
        )


def test_rejects_long_session_minutes_without_long_session():
    with pytest.raises(
        ValueError,
        match="requires at least one long session",
    ):
        make_strategy_plan(
            long_sessions=0,
            long_session_minutes=90,
        )


def test_rejects_zero_long_session_duration():
    with pytest.raises(
        ValueError,
        match="must be greater than zero",
    ):
        make_strategy_plan(
            long_sessions=1,
            long_session_minutes=0,
        )


def test_rejects_long_session_above_weekly_duration():
    with pytest.raises(
        ValueError,
        match="long_session_minutes cannot exceed",
    ):
        make_strategy_plan(
            target_weekly_minutes=90,
            long_session_minutes=120,
        )


def test_allows_recovery_days_alongside_training_days():
    """
    Recovery days are guidance targets and may include active
    recovery, so they do not need to sum with training days to 7.
    """

    plan = make_strategy_plan(
        target_sessions=6,
        recovery_days=2,
    )

    assert plan.target_sessions == 6
    assert plan.recovery_days == 2


# ======================================================
# Tuple validation
# ======================================================


@pytest.mark.parametrize(
    "field",
    [
        "objectives",
        "guidelines",
        "warnings",
    ],
)
def test_rejects_non_tuple_text_collections(
    field,
):
    with pytest.raises(
        TypeError,
        match=field,
    ):
        make_strategy_plan(
            **{field: ["Item"]},
        )


@pytest.mark.parametrize(
    "field",
    [
        "objectives",
        "guidelines",
        "warnings",
    ],
)
@pytest.mark.parametrize(
    "value",
    [
        ("",),
        ("   ",),
        (123,),
    ],
)
def test_rejects_invalid_tuple_items(
    field,
    value,
):
    with pytest.raises(
        ValueError,
        match=field,
    ):
        make_strategy_plan(
            **{field: value},
        )


# ======================================================
# CoachStrategy helpers
# ======================================================


class ExampleStrategy(CoachStrategy):
    name = "ExampleStrategy"
    phase = "Example"

    def build(
        self,
        context,
    ) -> StrategyPlan:
        return make_strategy_plan(
            strategy=self.name,
            phase=self.phase,
        )


def test_coach_strategy_is_abstract():
    with pytest.raises(
        TypeError,
    ):
        CoachStrategy()


def test_concrete_strategy_can_be_created():
    strategy = ExampleStrategy()

    assert strategy.name == "ExampleStrategy"
    assert strategy.phase == "Example"


def test_has_training_history_uses_context_sports():
    strategy = ExampleStrategy()

    assert strategy._has_training_history(
        SimpleNamespace(
            sports=("running",),
        )
    ) is True

    assert strategy._has_training_history(
        SimpleNamespace(
            sports=(),
        )
    ) is False


def test_event_name_returns_nested_event_name():
    strategy = ExampleStrategy()
    context = SimpleNamespace(
        next_event=SimpleNamespace(
            event=SimpleNamespace(
                name="City Marathon",
            ),
        ),
    )

    assert strategy._event_name(
        context,
    ) == "City Marathon"


@pytest.mark.parametrize(
    "next_event",
    [
        None,
        SimpleNamespace(
            event=None,
        ),
        SimpleNamespace(
            event=SimpleNamespace(),
        ),
    ],
)
def test_event_name_returns_none_when_unavailable(
    next_event,
):
    strategy = ExampleStrategy()

    assert strategy._event_name(
        SimpleNamespace(
            next_event=next_event,
        )
    ) is None


def test_event_priority_is_uppercase():
    strategy = ExampleStrategy()
    context = SimpleNamespace(
        next_event=SimpleNamespace(
            priority="a",
        ),
    )

    assert strategy._event_priority(
        context,
    ) == "A"


@pytest.mark.parametrize(
    "next_event",
    [
        None,
        SimpleNamespace(
            priority=None,
        ),
    ],
)
def test_event_priority_returns_none_when_unavailable(
    next_event,
):
    strategy = ExampleStrategy()

    assert strategy._event_priority(
        SimpleNamespace(
            next_event=next_event,
        )
    ) is None


def test_build_returns_strategy_plan():
    strategy = ExampleStrategy()

    plan = strategy.build(
        SimpleNamespace(),
    )

    assert isinstance(
        plan,
        StrategyPlan,
    )
    assert plan.strategy == "ExampleStrategy"
    assert plan.phase == "Example"


def test_repr_contains_class_and_phase():
    strategy = ExampleStrategy()

    representation = repr(
        strategy,
    )

    assert "ExampleStrategy" in representation
    assert "Example" in representation