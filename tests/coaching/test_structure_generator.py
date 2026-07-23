"""
Tests for WeekStructureGenerator.
"""

import pytest

from performancelab.training.config.availability import (
    AthleteAvailability,
    Weekday,
)
from performancelab.training.config.constraints import (
    TrainingConstraints,
)
from performancelab.training.config.preferences import (
    AthletePreferences,
)
from performancelab.coaching.session_purpose import (
    SessionPurpose,
)
from performancelab.coaching.strategy import StrategyPlan
from performancelab.coaching.structure_generator import (
    WeekStructureGenerator,
)


def slot_for_day(
    slots,
    weekday: Weekday,
):

    return next(
        slot
        for slot in slots
        if slot.weekday is weekday
    )


def test_generates_one_slot_for_each_weekday(
    strategy_plan: StrategyPlan,
    full_availability: AthleteAvailability,
    default_preferences: AthletePreferences,
    default_constraints: TrainingConstraints,
) -> None:

    slots = WeekStructureGenerator().generate(
        strategy_plan=strategy_plan,
        availability=full_availability,
        preferences=default_preferences,
        constraints=default_constraints,
    )

    assert isinstance(slots, tuple)
    assert len(slots) == 7

    assert {
        slot.weekday
        for slot in slots
    } == set(Weekday)


def test_unavailable_day_becomes_rest(
    strategy_plan: StrategyPlan,
    default_preferences: AthletePreferences,
    default_constraints: TrainingConstraints,
) -> None:

    availability = AthleteAvailability.from_minutes(
        monday=60,
        tuesday=0,
        wednesday=60,
        thursday=60,
        friday=60,
        saturday=60,
        sunday=60,
    )

    slots = WeekStructureGenerator().generate(
        strategy_plan=strategy_plan,
        availability=availability,
        preferences=default_preferences,
        constraints=default_constraints,
    )

    tuesday = slot_for_day(
        slots,
        Weekday.TUESDAY,
    )

    assert tuesday.is_rest is True
    assert tuesday.duration_minutes is None
    assert tuesday.notes == "The athlete is unavailable."


def test_blocked_day_becomes_rest(
    strategy_plan: StrategyPlan,
    full_availability: AthleteAvailability,
    default_preferences: AthletePreferences,
) -> None:

    constraints = TrainingConstraints(
        blocked_days={
            Weekday.WEDNESDAY,
        },
        max_weekly_minutes=420,
        max_session_minutes=120,
        max_weekday_minutes=90,
        max_weekend_minutes=120,
        max_consecutive_training_days=7,
        max_intensity_sessions=2,
        max_long_sessions=1,
        max_sessions_per_day=1,
        minimum_recovery_days=0,
        allow_double_sessions=False,
    )

    slots = WeekStructureGenerator().generate(
        strategy_plan=strategy_plan,
        availability=full_availability,
        preferences=default_preferences,
        constraints=constraints,
    )

    wednesday = slot_for_day(
        slots,
        Weekday.WEDNESDAY,
    )

    assert wednesday.is_rest is True
    assert (
        wednesday.notes
        == "Training is blocked by an athlete constraint."
    )


def test_preferred_rest_day_becomes_rest(
    strategy_plan: StrategyPlan,
    full_availability: AthleteAvailability,
    default_constraints: TrainingConstraints,
) -> None:

    preferences = AthletePreferences(
        preferred_rest_days={
            Weekday.FRIDAY,
        },
    )

    slots = WeekStructureGenerator().generate(
        strategy_plan=strategy_plan,
        availability=full_availability,
        preferences=preferences,
        constraints=default_constraints,
    )

    friday = slot_for_day(
        slots,
        Weekday.FRIDAY,
    )

    assert friday.is_rest is True
    assert friday.notes == "Preferred rest day."


def test_places_long_session_on_preferred_day(
    strategy_plan: StrategyPlan,
    full_availability: AthleteAvailability,
    default_constraints: TrainingConstraints,
) -> None:

    preferences = AthletePreferences(
        preferred_long_day=Weekday.SATURDAY,
    )

    slots = WeekStructureGenerator().generate(
        strategy_plan=strategy_plan,
        availability=full_availability,
        preferences=preferences,
        constraints=default_constraints,
    )

    saturday = slot_for_day(
        slots,
        Weekday.SATURDAY,
    )

    assert saturday.purpose is SessionPurpose.LONG

    assert sum(
        slot.is_long
        for slot in slots
    ) == 1


def test_does_not_place_long_session_on_unavailable_preferred_day(
    strategy_plan: StrategyPlan,
    default_constraints: TrainingConstraints,
) -> None:

    availability = AthleteAvailability.from_minutes(
        monday=30,
        tuesday=40,
        wednesday=50,
        thursday=60,
        friday=45,
        saturday=0,
        sunday=90,
    )

    preferences = AthletePreferences(
        preferred_long_day=Weekday.SATURDAY,
    )

    slots = WeekStructureGenerator().generate(
        strategy_plan=strategy_plan,
        availability=availability,
        preferences=preferences,
        constraints=default_constraints,
    )

    saturday = slot_for_day(
        slots,
        Weekday.SATURDAY,
    )

    sunday = slot_for_day(
        slots,
        Weekday.SUNDAY,
    )

    assert saturday.is_rest is True
    assert sunday.is_long is True


def test_does_not_place_long_session_when_not_allowed(
    strategy_plan: StrategyPlan,
    full_availability: AthleteAvailability,
    default_preferences: AthletePreferences,
) -> None:

    constraints = TrainingConstraints(
        max_weekly_minutes=420,
        max_session_minutes=120,
        max_weekday_minutes=90,
        max_weekend_minutes=120,
        max_consecutive_training_days=7,
        max_intensity_sessions=2,
        max_long_sessions=0,
        max_sessions_per_day=1,
        minimum_recovery_days=0,
        allow_double_sessions=False,
    )

    slots = WeekStructureGenerator().generate(
        strategy_plan=strategy_plan,
        availability=full_availability,
        preferences=default_preferences,
        constraints=constraints,
    )

    assert not any(
        slot.is_long
        for slot in slots
    )


def test_places_intensity_on_preferred_days(
    strategy_plan: StrategyPlan,
    full_availability: AthleteAvailability,
) -> None:

    preferences = AthletePreferences(
        preferred_long_day=Weekday.SUNDAY,
        preferred_intensity_days={
            Weekday.TUESDAY,
            Weekday.THURSDAY,
        },
    )

    constraints = TrainingConstraints(
        max_weekly_minutes=540,
        max_session_minutes=120,
        max_weekday_minutes=90,
        max_weekend_minutes=120,
        max_consecutive_training_days=7,
        max_intensity_sessions=2,
        max_long_sessions=1,
        max_sessions_per_day=1,
        minimum_recovery_days=0,
        allow_double_sessions=False,
    )

    slots = WeekStructureGenerator().generate(
        strategy_plan=strategy_plan,
        availability=full_availability,
        preferences=preferences,
        constraints=constraints,
    )

    assert (
        slot_for_day(
            slots,
            Weekday.TUESDAY,
        ).purpose
        is SessionPurpose.INTENSITY
    )

    assert (
        slot_for_day(
            slots,
            Weekday.THURSDAY,
        ).purpose
        is SessionPurpose.INTENSITY
    )

    assert (
        slot_for_day(
            slots,
            Weekday.SUNDAY,
        ).purpose
        is SessionPurpose.LONG
    )


def test_respects_intensity_session_limit(
    strategy_plan: StrategyPlan,
    full_availability: AthleteAvailability,
) -> None:

    preferences = AthletePreferences(
        preferred_long_day=Weekday.SUNDAY,
        preferred_intensity_days={
            Weekday.MONDAY,
            Weekday.TUESDAY,
            Weekday.THURSDAY,
        },
    )

    constraints = TrainingConstraints(
        max_weekly_minutes=420,
        max_session_minutes=120,
        max_weekday_minutes=90,
        max_weekend_minutes=120,
        max_consecutive_training_days=7,
        max_intensity_sessions=1,
        max_long_sessions=1,
        max_sessions_per_day=1,
        minimum_recovery_days=0,
        allow_double_sessions=False,
    )

    slots = WeekStructureGenerator().generate(
        strategy_plan=strategy_plan,
        availability=full_availability,
        preferences=preferences,
        constraints=constraints,
    )

    assert sum(
        slot.is_intensity
        for slot in slots
    ) == 1


def test_does_not_place_intensity_on_long_day(
    strategy_plan: StrategyPlan,
    full_availability: AthleteAvailability,
    default_constraints: TrainingConstraints,
) -> None:

    preferences = AthletePreferences(
        preferred_long_day=Weekday.SATURDAY,
        preferred_intensity_days={
            Weekday.SATURDAY,
        },
    )

    slots = WeekStructureGenerator().generate(
        strategy_plan=strategy_plan,
        availability=full_availability,
        preferences=preferences,
        constraints=default_constraints,
    )

    saturday = slot_for_day(
        slots,
        Weekday.SATURDAY,
    )

    assert saturday.purpose is SessionPurpose.LONG


def test_respects_weekly_duration_limit(
    strategy_plan: StrategyPlan,
    full_availability: AthleteAvailability,
    default_preferences: AthletePreferences,
) -> None:

    constraints = TrainingConstraints(
        max_weekly_minutes=150,
        max_session_minutes=120,
        max_weekday_minutes=90,
        max_weekend_minutes=120,
        max_consecutive_training_days=7,
        max_intensity_sessions=0,
        max_long_sessions=0,
        max_sessions_per_day=1,
        minimum_recovery_days=0,
        allow_double_sessions=False,
    )

    slots = WeekStructureGenerator().generate(
        strategy_plan=strategy_plan,
        availability=full_availability,
        preferences=default_preferences,
        constraints=constraints,
    )

    total_minutes = sum(
        slot.duration_minutes or 0
        for slot in slots
    )

    assert total_minutes == 150


def test_respects_weekday_duration_limit(
    strategy_plan: StrategyPlan,
    full_availability: AthleteAvailability,
    default_preferences: AthletePreferences,
) -> None:

    constraints = TrainingConstraints(
        max_weekly_minutes=420,
        max_session_minutes=120,
        max_weekday_minutes=30,
        max_weekend_minutes=90,
        max_consecutive_training_days=7,
        max_intensity_sessions=0,
        max_long_sessions=0,
        max_sessions_per_day=1,
        minimum_recovery_days=0,
        allow_double_sessions=False,
    )

    slots = WeekStructureGenerator().generate(
        strategy_plan=strategy_plan,
        availability=full_availability,
        preferences=default_preferences,
        constraints=constraints,
    )

    monday = slot_for_day(
        slots,
        Weekday.MONDAY,
    )

    saturday = slot_for_day(
        slots,
        Weekday.SATURDAY,
    )

    assert monday.duration_minutes == 30
    assert saturday.duration_minutes == 90


def test_inserts_rest_to_respect_consecutive_day_limit(
    strategy_plan: StrategyPlan,
    full_availability: AthleteAvailability,
    default_preferences: AthletePreferences,
) -> None:

    constraints = TrainingConstraints(
        max_weekly_minutes=420,
        max_session_minutes=120,
        max_weekday_minutes=90,
        max_weekend_minutes=120,
        max_consecutive_training_days=2,
        max_intensity_sessions=0,
        max_long_sessions=0,
        max_sessions_per_day=1,
        minimum_recovery_days=0,
        allow_double_sessions=False,
    )

    slots = WeekStructureGenerator().generate(
        strategy_plan=strategy_plan,
        availability=full_availability,
        preferences=default_preferences,
        constraints=constraints,
    )

    ordered = list(slots)

    # O número de sessões deve respeitar o StrategyPlan.
    assert sum(slot.is_training for slot in ordered) == strategy_plan.target_sessions

    # Nunca podem existir mais de 2 dias consecutivos de treino.
    consecutive = 0

    for slot in ordered:
        if slot.is_training:
            consecutive += 1
            assert consecutive <= constraints.max_consecutive_training_days
        else:
            consecutive = 0


def test_inserts_minimum_number_of_recovery_days(
    strategy_plan: StrategyPlan,
    full_availability: AthleteAvailability,
    default_preferences: AthletePreferences,
) -> None:

    constraints = TrainingConstraints(
        max_weekly_minutes=420,
        max_session_minutes=120,
        max_weekday_minutes=90,
        max_weekend_minutes=120,
        max_consecutive_training_days=7,
        max_intensity_sessions=0,
        max_long_sessions=1,
        max_sessions_per_day=1,
        minimum_recovery_days=2,
        allow_double_sessions=False,
    )

    slots = WeekStructureGenerator().generate(
        strategy_plan=strategy_plan,
        availability=full_availability,
        preferences=default_preferences,
        constraints=constraints,
    )

    assert sum(
        slot.is_rest
        for slot in slots
    ) >= 2


def test_rejects_invalid_strategy_plan(
    full_availability: AthleteAvailability,
    default_preferences: AthletePreferences,
    default_constraints: TrainingConstraints,
) -> None:

    with pytest.raises(
        TypeError,
        match="strategy_plan must be a StrategyPlan",
    ):

        WeekStructureGenerator().generate(
            strategy_plan=object(),
            availability=full_availability,
            preferences=default_preferences,
            constraints=default_constraints,
        )


def test_rejects_invalid_availability(
    strategy_plan: StrategyPlan,
    default_preferences: AthletePreferences,
    default_constraints: TrainingConstraints,
) -> None:

    with pytest.raises(
        TypeError,
        match="availability must be an",
    ):

        WeekStructureGenerator().generate(
            strategy_plan=strategy_plan,
            availability=object(),
            preferences=default_preferences,
            constraints=default_constraints,
        )