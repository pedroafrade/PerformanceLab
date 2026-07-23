from datetime import date, timedelta

import pytest

from performancelab.coaching import (
    CoachContext,
    DraftTrainingSlot,
    SessionPurpose,
    StrategyPlan,
    TrainingWeek,
    Weekday,
    WorkoutGenerator,
)


@pytest.fixture
def strategy_plan() -> StrategyPlan:

    return StrategyPlan(
        strategy="balanced",
        phase="base",
        volume_factor=1.0,
        target_sessions=4,
        intensity_sessions=1,
        long_sessions=1,
        recovery_days=2,
        objectives=(
            "Build aerobic endurance.",
        ),
    )


@pytest.fixture
def coach_context() -> CoachContext:

    return object.__new__(
        CoachContext
    )


def configure_context(
    context: CoachContext,
    sports: tuple[str, ...],
) -> CoachContext:
    """
    Sets fields on a frozen dataclass fixture created without
    invoking its production constructor.
    """

    object.__setattr__(
        context,
        "sports",
        sports,
    )

    return context


def make_slot(
    weekday: Weekday,
    purpose: SessionPurpose,
    duration_minutes: int | None,
) -> DraftTrainingSlot:

    return DraftTrainingSlot(
        weekday=weekday,
        purpose=purpose,
        duration_minutes=duration_minutes,
    )


def make_training_week(
    *slots: DraftTrainingSlot,
) -> TrainingWeek:

    return TrainingWeek(
        start_date=date(
            2026,
            7,
            20,
        ),
        slots=slots,
    )


def test_generates_planned_workout(
    strategy_plan: StrategyPlan,
    coach_context: CoachContext,
) -> None:

    configure_context(
        coach_context,
        ("running",),
    )

    slot = make_slot(
        weekday=Weekday.MONDAY,
        purpose=SessionPurpose.EASY,
        duration_minutes=60,
    )

    training_week = make_training_week(
        slot
    )

    generator = WorkoutGenerator()

    workouts = generator.generate(
        strategy_plan=strategy_plan,
        training_week=training_week,
        coach_context=coach_context,
    )

    assert len(workouts) == 1

    workout = workouts[0]

    assert workout.day == date(
        2026,
        7,
        20,
    )

    assert workout.sport == "running"

    assert (
        workout.title
        == "Easy Aerobic Session"
    )

    assert workout.duration == timedelta(
        minutes=60
    )

    assert workout.intensity == "Easy"

    assert (
        "Develop aerobic endurance"
        in workout.objective
    )


def test_generates_workouts_in_date_order(
    strategy_plan: StrategyPlan,
    coach_context: CoachContext,
) -> None:

    configure_context(
        coach_context,
        ("running",),
    )

    training_week = make_training_week(
        make_slot(
            weekday=Weekday.WEDNESDAY,
            purpose=SessionPurpose.INTENSITY,
            duration_minutes=50,
        ),
        make_slot(
            weekday=Weekday.MONDAY,
            purpose=SessionPurpose.EASY,
            duration_minutes=45,
        ),
        make_slot(
            weekday=Weekday.TUESDAY,
            purpose=SessionPurpose.RECOVERY,
            duration_minutes=30,
        ),
    )

    workouts = WorkoutGenerator().generate(
        strategy_plan=strategy_plan,
        training_week=training_week,
        coach_context=coach_context,
    )

    assert tuple(
        workout.day
        for workout in workouts
    ) == (
        date(2026, 7, 20),
        date(2026, 7, 21),
        date(2026, 7, 22),
    )


def test_maps_weekdays_to_calendar_dates(
    strategy_plan: StrategyPlan,
    coach_context: CoachContext,
) -> None:

    configure_context(
        coach_context,
        ("running",),
    )

    training_week = make_training_week(
        make_slot(
            weekday=Weekday.MONDAY,
            purpose=SessionPurpose.EASY,
            duration_minutes=30,
        ),
        make_slot(
            weekday=Weekday.SUNDAY,
            purpose=SessionPurpose.LONG,
            duration_minutes=90,
        ),
    )

    workouts = WorkoutGenerator().generate(
        strategy_plan=strategy_plan,
        training_week=training_week,
        coach_context=coach_context,
    )

    assert workouts[0].day == date(
        2026,
        7,
        20,
    )

    assert workouts[1].day == date(
        2026,
        7,
        26,
    )


def test_rest_slots_are_skipped_by_default(
    strategy_plan: StrategyPlan,
    coach_context: CoachContext,
) -> None:

    configure_context(
        coach_context,
        ("running",),
    )

    slot = DraftTrainingSlot.rest(
        Weekday.MONDAY
    )

    training_week = make_training_week(
        slot
    )

    workouts = WorkoutGenerator().generate(
        strategy_plan=strategy_plan,
        training_week=training_week,
        coach_context=coach_context,
    )

    assert workouts == ()


def test_can_generate_rest_placeholders(
    strategy_plan: StrategyPlan,
    coach_context: CoachContext,
) -> None:

    configure_context(
        coach_context,
        ("running",),
    )

    slot = DraftTrainingSlot.rest(
        Weekday.MONDAY
    )

    training_week = make_training_week(
        slot
    )

    generator = WorkoutGenerator(
        include_rest_days=True
    )

    workouts = generator.generate(
        strategy_plan=strategy_plan,
        training_week=training_week,
        coach_context=coach_context,
    )

    assert len(workouts) == 1

    assert workouts[0].is_rest

    assert workouts[0].day == date(
        2026,
        7,
        20,
    )


def test_uses_first_context_sport(
    strategy_plan: StrategyPlan,
    coach_context: CoachContext,
) -> None:

    configure_context(
        coach_context,
        (
            "cycling",
            "running",
        ),
    )

    training_week = make_training_week(
        make_slot(
            weekday=Weekday.MONDAY,
            purpose=SessionPurpose.EASY,
            duration_minutes=60,
        )
    )

    workouts = WorkoutGenerator().generate(
        strategy_plan=strategy_plan,
        training_week=training_week,
        coach_context=coach_context,
    )

    assert workouts[0].sport == "cycling"


def test_allows_context_without_sports(
    strategy_plan: StrategyPlan,
    coach_context: CoachContext,
) -> None:

    configure_context(
        coach_context,
        (),
    )

    training_week = make_training_week(
        make_slot(
            weekday=Weekday.MONDAY,
            purpose=SessionPurpose.EASY,
            duration_minutes=60,
        )
    )

    workouts = WorkoutGenerator().generate(
        strategy_plan=strategy_plan,
        training_week=training_week,
        coach_context=coach_context,
    )

    assert workouts[0].sport is None


def test_uses_template_structure(
    strategy_plan: StrategyPlan,
    coach_context: CoachContext,
) -> None:

    configure_context(
        coach_context,
        ("running",),
    )

    training_week = make_training_week(
        make_slot(
            weekday=Weekday.MONDAY,
            purpose=SessionPurpose.INTENSITY,
            duration_minutes=60,
        )
    )

    workouts = WorkoutGenerator().generate(
        strategy_plan=strategy_plan,
        training_week=training_week,
        coach_context=coach_context,
    )

    workout = workouts[0]

    assert workout.structure

    assert (
        "Main work intervals"
        in workout.structure
    )


def test_rejects_training_slot_without_duration(
    strategy_plan: StrategyPlan,
    coach_context: CoachContext,
) -> None:

    configure_context(
        coach_context,
        ("running",),
    )

    training_week = make_training_week(
        make_slot(
            weekday=Weekday.MONDAY,
            purpose=SessionPurpose.EASY,
            duration_minutes=None,
        )
    )

    with pytest.raises(
        ValueError,
        match=(
            "training slots must have a duration"
        ),
    ):

        WorkoutGenerator().generate(
            strategy_plan=strategy_plan,
            training_week=training_week,
            coach_context=coach_context,
        )


def test_rejects_zero_duration_training_slot(
    strategy_plan: StrategyPlan,
    coach_context: CoachContext,
) -> None:

    configure_context(
        coach_context,
        ("running",),
    )

    training_week = make_training_week(
        make_slot(
            weekday=Weekday.MONDAY,
            purpose=SessionPurpose.EASY,
            duration_minutes=0,
        )
    )

    with pytest.raises(
        ValueError,
        match=(
            "training slots must have a positive duration"
        ),
    ):

        WorkoutGenerator().generate(
            strategy_plan=strategy_plan,
            training_week=training_week,
            coach_context=coach_context,
        )


def test_rejects_invalid_strategy_plan(
    coach_context: CoachContext,
) -> None:

    configure_context(
        coach_context,
        ("running",),
    )

    training_week = make_training_week()

    with pytest.raises(
        TypeError,
        match=(
            "strategy_plan must be a StrategyPlan"
        ),
    ):

        WorkoutGenerator().generate(
            strategy_plan=object(),
            training_week=training_week,
            coach_context=coach_context,
        )


def test_rejects_invalid_training_week(
    strategy_plan: StrategyPlan,
    coach_context: CoachContext,
) -> None:

    configure_context(
        coach_context,
        ("running",),
    )

    with pytest.raises(
        TypeError,
        match=(
            "training_week must be a TrainingWeek"
        ),
    ):

        WorkoutGenerator().generate(
            strategy_plan=strategy_plan,
            training_week=object(),
            coach_context=coach_context,
        )


def test_rejects_invalid_context(
    strategy_plan: StrategyPlan,
) -> None:

    training_week = make_training_week()

    with pytest.raises(
        TypeError,
        match=(
            "coach_context must be a CoachContext"
        ),
    ):

        WorkoutGenerator().generate(
            strategy_plan=strategy_plan,
            training_week=training_week,
            coach_context=object(),
        )


def test_rejects_invalid_rest_configuration() -> None:

    with pytest.raises(
        TypeError,
        match=(
            "include_rest_days must be a bool"
        ),
    ):

        WorkoutGenerator(
            include_rest_days="yes"
        )


def test_repr_contains_configuration() -> None:

    generator = WorkoutGenerator(
        include_rest_days=True
    )

    representation = repr(
        generator
    )

    assert (
        "WorkoutGenerator"
        in representation
    )

    assert (
        "include_rest_days=True"
        in representation
    )