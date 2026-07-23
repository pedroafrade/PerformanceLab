"""
PerformanceLab

Week Structure Generator

Creates a provisional weekly training structure from the
athlete's availability, preferences, constraints and
coaching strategy.

This generator does not create detailed workouts.
"""

from collections.abc import Iterable

from ..training.config.availability import (
    AthleteAvailability,
    Weekday,
)
from ..training.config.constraints import TrainingConstraints
from .draft_slot import DraftTrainingSlot
from ..training.config.preferences import AthletePreferences
from .session_purpose import SessionPurpose
from .strategy import StrategyPlan


class WeekStructureGenerator:
    """
    Generates a provisional seven-day training structure.

    The first version follows deterministic rules:

    1. Block unavailable and prohibited weekdays.
    2. Respect preferred rest days.
    3. Fill usable days with easy sessions.
    4. Place one long session when possible.
    5. Place intensity on preferred intensity days.
    6. Respect weekly duration and recovery limits.

    StrategyPlan is accepted now so that the public API
    remains stable as strategy-specific generation rules are
    added later.
    """

    # ======================================================

    def generate(
        self,
        *,
        strategy_plan: StrategyPlan,
        availability: AthleteAvailability,
        preferences: AthletePreferences,
        constraints: TrainingConstraints,
    ) -> tuple[DraftTrainingSlot, ...]:
        """
        Creates one draft slot for every weekday.
        """

        self._validate_inputs(
            strategy_plan=strategy_plan,
            availability=availability,
            preferences=preferences,
            constraints=constraints,
        )

        slots = self._create_initial_slots(
            availability=availability,
            preferences=preferences,
            constraints=constraints,
        )

        slots = self._place_long_session(
            slots=slots,
            preferences=preferences,
            constraints=constraints,
        )

        slots = self._place_intensity_sessions(
            slots=slots,
            preferences=preferences,
            constraints=constraints,
        )

        slots = self._enforce_consecutive_day_limit(
            slots=slots,
            constraints=constraints,
        )

        slots = self._enforce_recovery_day_requirement(
            slots=slots,
            constraints=constraints,
        )

        return tuple(
            sorted(
                slots,
                key=lambda slot: slot.weekday.value,
            )
        )

    # ======================================================

    def _create_initial_slots(
        self,
        *,
        availability: AthleteAvailability,
        preferences: AthletePreferences,
        constraints: TrainingConstraints,
    ) -> list[DraftTrainingSlot]:

        slots: list[DraftTrainingSlot] = []

        remaining_weekly_minutes = (
            constraints.max_weekly_minutes
        )

        for weekday in Weekday:

            if constraints.is_blocked(weekday):

                slots.append(
                    DraftTrainingSlot.rest(
                        weekday,
                        notes=(
                            "Training is blocked by an "
                            "athlete constraint."
                        ),
                    )
                )

                continue

            available_minutes = (
                availability.minutes_for(
                    weekday,
                )
            )

            if available_minutes <= 0:

                slots.append(
                    DraftTrainingSlot.rest(
                        weekday,
                        notes=(
                            "The athlete is unavailable."
                        ),
                    )
                )

                continue

            if preferences.prefers_rest(weekday):

                slots.append(
                    DraftTrainingSlot.rest(
                        weekday,
                        notes=(
                            "Preferred rest day."
                        ),
                    )
                )

                continue

            duration = self._duration_for_day(
                weekday=weekday,
                available_minutes=available_minutes,
                constraints=constraints,
                remaining_weekly_minutes=(
                    remaining_weekly_minutes
                ),
            )

            if duration <= 0:

                slots.append(
                    DraftTrainingSlot.rest(
                        weekday,
                        notes=(
                            "No weekly training time remains."
                        ),
                    )
                )

                continue

            slots.append(
                DraftTrainingSlot(
                    weekday=weekday,
                    purpose=SessionPurpose.EASY,
                    duration_minutes=duration,
                    notes=(
                        "Initial easy training slot."
                    ),
                )
            )

            if remaining_weekly_minutes is not None:

                remaining_weekly_minutes -= duration

        return slots

    # ======================================================

    def _place_long_session(
        self,
        *,
        slots: list[DraftTrainingSlot],
        preferences: AthletePreferences,
        constraints: TrainingConstraints,
    ) -> list[DraftTrainingSlot]:

        if constraints.max_long_sessions <= 0:

            return slots

        candidates = [
            slot
            for slot in slots
            if slot.is_training
        ]

        if not candidates:

            return slots

        selected: DraftTrainingSlot | None = None

        preferred_day = preferences.preferred_long_day

        if preferred_day is not None:

            selected = next(
                (
                    slot
                    for slot in candidates
                    if slot.weekday == preferred_day
                ),
                None,
            )

        if selected is None:

            selected = max(
                candidates,
                key=lambda slot: (
                    slot.duration_minutes or 0,
                    slot.weekday.value,
                ),
            )

        return [
            (
                slot.with_purpose(
                    SessionPurpose.LONG,
                    notes="Provisional long session.",
                )
                if slot.weekday == selected.weekday
                else slot
            )
            for slot in slots
        ]

    # ======================================================

    def _place_intensity_sessions(
        self,
        *,
        slots: list[DraftTrainingSlot],
        preferences: AthletePreferences,
        constraints: TrainingConstraints,
    ) -> list[DraftTrainingSlot]:

        maximum = constraints.max_intensity_sessions

        if maximum <= 0:

            return slots

        preferred_days = (
            preferences.preferred_intensity_days
        )

        if not preferred_days:

            return slots

        selected_days: list[Weekday] = []

        for weekday in preferred_days:

            if len(selected_days) >= maximum:

                break

            slot = self._slot_for_day(
                slots,
                weekday,
            )

            if slot is None:

                continue

            if not slot.is_training:

                continue

            if slot.is_long:

                continue

            if not constraints.allows_intensity(weekday):

                continue

            selected_days.append(
                weekday,
            )

        return [
            (
                slot.with_purpose(
                    SessionPurpose.INTENSITY,
                    notes=(
                        "Preferred provisional intensity "
                        "session."
                    ),
                )
                if slot.weekday in selected_days
                else slot
            )
            for slot in slots
        ]

    # ======================================================

    def _enforce_consecutive_day_limit(
        self,
        *,
        slots: list[DraftTrainingSlot],
        constraints: TrainingConstraints,
    ) -> list[DraftTrainingSlot]:

        maximum = (
            constraints.max_consecutive_training_days
        )

        if maximum >= 7:

            return slots

        consecutive_days = 0
        result: list[DraftTrainingSlot] = []

        for slot in sorted(
            slots,
            key=lambda item: item.weekday.value,
        ):

            if slot.is_rest:

                consecutive_days = 0
                result.append(slot)

                continue

            consecutive_days += 1

            if consecutive_days <= maximum:

                result.append(slot)

                continue

            result.append(
                DraftTrainingSlot.rest(
                    slot.weekday,
                    notes=(
                        "Rest inserted to respect the "
                        "consecutive training-day limit."
                    ),
                )
            )

            consecutive_days = 0

        return result

    # ======================================================

    def _enforce_recovery_day_requirement(
        self,
        *,
        slots: list[DraftTrainingSlot],
        constraints: TrainingConstraints,
    ) -> list[DraftTrainingSlot]:

        required = constraints.minimum_recovery_days

        current = sum(
            slot.is_rest
            for slot in slots
        )

        missing = required - current

        if missing <= 0:

            return slots

        candidates = sorted(
            (
                slot
                for slot in slots
                if slot.is_training
            ),
            key=lambda slot: (
                self._replacement_priority(slot),
                slot.duration_minutes or 0,
                slot.weekday.value,
            ),
        )

        selected_days = {
            slot.weekday
            for slot in candidates[:missing]
        }

        return [
            (
                DraftTrainingSlot.rest(
                    slot.weekday,
                    notes=(
                        "Rest inserted to satisfy the "
                        "minimum recovery-day requirement."
                    ),
                )
                if slot.weekday in selected_days
                else slot
            )
            for slot in slots
        ]

    # ======================================================

    @staticmethod
    def _duration_for_day(
        *,
        weekday: Weekday,
        available_minutes: int,
        constraints: TrainingConstraints,
        remaining_weekly_minutes: int | None,
    ) -> int:

        limits = [
            available_minutes,
        ]

        day_limit = constraints.duration_limit_for(
            weekday,
        )

        if day_limit is not None:

            limits.append(
                day_limit,
            )

        if remaining_weekly_minutes is not None:

            limits.append(
                remaining_weekly_minutes,
            )

        return max(
            0,
            min(limits),
        )

    # ======================================================

    @staticmethod
    def _slot_for_day(
        slots: Iterable[DraftTrainingSlot],
        weekday: Weekday,
    ) -> DraftTrainingSlot | None:

        return next(
            (
                slot
                for slot in slots
                if slot.weekday == weekday
            ),
            None,
        )

    # ======================================================

    @staticmethod
    def _replacement_priority(
        slot: DraftTrainingSlot,
    ) -> int:
        """
        Lower values are converted to rest first.
        """

        priorities = {
            SessionPurpose.RECOVERY: 0,
            SessionPurpose.EASY: 1,
            SessionPurpose.CROSS_TRAINING: 2,
            SessionPurpose.INTENSITY: 3,
            SessionPurpose.LONG: 4,
            SessionPurpose.RACE: 5,
        }

        return priorities.get(
            slot.purpose,
            6,
        )

    # ======================================================

    @staticmethod
    def _validate_inputs(
        *,
        strategy_plan: StrategyPlan,
        availability: AthleteAvailability,
        preferences: AthletePreferences,
        constraints: TrainingConstraints,
    ) -> None:

        if not isinstance(
            strategy_plan,
            StrategyPlan,
        ):

            raise TypeError(
                "strategy_plan must be a StrategyPlan."
            )

        if not isinstance(
            availability,
            AthleteAvailability,
        ):

            raise TypeError(
                "availability must be an "
                "AthleteAvailability."
            )

        if not isinstance(
            preferences,
            AthletePreferences,
        ):

            raise TypeError(
                "preferences must be an "
                "AthletePreferences."
            )

        if not isinstance(
            constraints,
            TrainingConstraints,
        ):

            raise TypeError(
                "constraints must be TrainingConstraints."
            )