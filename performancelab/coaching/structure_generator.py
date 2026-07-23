"""
PerformanceLab

Week Structure Generator

Transforms a StrategyPlan into a provisional seven-day
training structure.

The generator decides when training occurs. It does not
create detailed workouts.
"""

from collections.abc import Iterable
from itertools import combinations

from performancelab.training.config import (
    AthleteAvailability,
    AthletePreferences,
    TrainingConstraints,
    Weekday,
)

from .draft_slot import DraftTrainingSlot
from .session_purpose import SessionPurpose
from .strategy import StrategyPlan


class WeekStructureGenerator:
    """
    Generates a provisional seven-day training structure.

    Responsibilities
    ----------------
    - select training days;
    - distribute the strategy's weekly minutes;
    - place long sessions;
    - place intensity sessions;
    - represent recovery guidance;
    - respect athlete availability and constraints.
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

        training_days = self._select_training_days(
            strategy_plan=strategy_plan,
            availability=availability,
            preferences=preferences,
            constraints=constraints,
        )

        purposes = self._assign_purposes(
            training_days=training_days,
            strategy_plan=strategy_plan,
            availability=availability,
            preferences=preferences,
            constraints=constraints,
        )

        durations = self._allocate_durations(
            training_days=training_days,
            purposes=purposes,
            strategy_plan=strategy_plan,
            availability=availability,
            constraints=constraints,
        )

        slots = self._build_slots(
            training_days=training_days,
            purposes=purposes,
            durations=durations,
            availability=availability,
            preferences=preferences,
            constraints=constraints,
        )

        slots = self._apply_recovery_guidance(
            slots=slots,
            strategy_plan=strategy_plan,
            constraints=constraints,
        )

        return tuple(
            sorted(
                slots,
                key=lambda slot: slot.weekday.value,
            )
        )

    # ======================================================
    # Training-day selection
    # ======================================================

    def _select_training_days(
        self,
        *,
        strategy_plan: StrategyPlan,
        availability: AthleteAvailability,
        preferences: AthletePreferences,
        constraints: TrainingConstraints,
    ) -> tuple[Weekday, ...]:
        """
        Selects training days while respecting the maximum number
        of consecutive training days.

        Preferred long and intensity days receive priority, followed
        by days with the greatest usable availability.
        """

        usable_days = [
            weekday
            for weekday in Weekday
            if self._is_usable_day(
                weekday=weekday,
                availability=availability,
                preferences=preferences,
                constraints=constraints,
            )
        ]

        target = min(
            strategy_plan.target_sessions,
            len(usable_days),
        )

        if target <= 0:
            return ()

        ranked_days = sorted(
            usable_days,
            key=lambda weekday: self._training_day_priority(
                weekday=weekday,
                strategy_plan=strategy_plan,
                availability=availability,
                preferences=preferences,
                constraints=constraints,
            ),
        )

        maximum_consecutive = (
            constraints.max_consecutive_training_days
        )

        for session_count in range(target, 0, -1):
            valid_combinations = [
                candidate
                for candidate in combinations(
                    ranked_days,
                    session_count,
                )
                if self._respects_consecutive_day_limit(
                    training_days=set(candidate),
                    maximum=maximum_consecutive,
                )
            ]

            if not valid_combinations:
                continue

            selected = min(
                valid_combinations,
                key=lambda candidate: (
                    self._training_day_combination_priority(
                        training_days=candidate,
                        strategy_plan=strategy_plan,
                        availability=availability,
                        preferences=preferences,
                        constraints=constraints,
                    )
                ),
            )

            return tuple(
                sorted(
                    selected,
                    key=lambda weekday: weekday.value,
                )
            )

        return ()

    # ======================================================

    @staticmethod
    def _respects_consecutive_day_limit(
        *,
        training_days: set[Weekday],
        maximum: int,
    ) -> bool:
        if maximum >= 7:
            return True

        if maximum <= 0:
            return not training_days

        consecutive_days = 0

        for weekday in Weekday:
            if weekday in training_days:
                consecutive_days += 1

                if consecutive_days > maximum:
                    return False
            else:
                consecutive_days = 0

        return True

    # ======================================================

    def _training_day_combination_priority(
        self,
        *,
        training_days: tuple[Weekday, ...],
        strategy_plan: StrategyPlan,
        availability: AthleteAvailability,
        preferences: AthletePreferences,
        constraints: TrainingConstraints,
    ) -> tuple[tuple[int, int, int, int], ...]:
        """
        Compares valid day combinations using the existing
        individual day-priority rules.
        """

        return tuple(
            sorted(
                (
                    self._training_day_priority(
                        weekday=weekday,
                        strategy_plan=strategy_plan,
                        availability=availability,
                        preferences=preferences,
                        constraints=constraints,
                    )
                    for weekday in training_days
                )
            )
        )

    # ======================================================

    @staticmethod
    def _is_usable_day(
        *,
        weekday: Weekday,
        availability: AthleteAvailability,
        preferences: AthletePreferences,
        constraints: TrainingConstraints,
    ) -> bool:
        if constraints.is_blocked(weekday):
            return False

        if availability.minutes_for(weekday) <= 0:
            return False

        if preferences.prefers_rest(weekday):
            return False

        return True

    # ======================================================

    def _training_day_priority(
        self,
        *,
        weekday: Weekday,
        strategy_plan: StrategyPlan,
        availability: AthleteAvailability,
        preferences: AthletePreferences,
        constraints: TrainingConstraints,
    ) -> tuple[int, int, int, int]:
        """
        Lower tuples are selected first.
        """

        preferred_long = (
            strategy_plan.long_sessions > 0
            and preferences.preferred_long_day == weekday
        )

        preferred_intensity = (
            strategy_plan.intensity_sessions > 0
            and weekday
            in preferences.preferred_intensity_days
            and constraints.allows_intensity(weekday)
        )

        usable_minutes = self._usable_minutes(
            weekday=weekday,
            availability=availability,
            constraints=constraints,
        )

        return (
            0 if preferred_long else 1,
            0 if preferred_intensity else 1,
            -usable_minutes,
            weekday.value,
        )

    # ======================================================
    # Purpose assignment
    # ======================================================

    def _assign_purposes(
        self,
        *,
        training_days: tuple[Weekday, ...],
        strategy_plan: StrategyPlan,
        availability: AthleteAvailability,
        preferences: AthletePreferences,
        constraints: TrainingConstraints,
    ) -> dict[Weekday, SessionPurpose]:
        purposes = {
            weekday: SessionPurpose.EASY
            for weekday in training_days
        }

        long_days = self._select_long_days(
            training_days=training_days,
            strategy_plan=strategy_plan,
            availability=availability,
            preferences=preferences,
            constraints=constraints,
        )

        for weekday in long_days:
            purposes[weekday] = SessionPurpose.LONG

        intensity_days = self._select_intensity_days(
            training_days=training_days,
            excluded_days=set(long_days),
            strategy_plan=strategy_plan,
            availability=availability,
            preferences=preferences,
            constraints=constraints,
        )

        for weekday in intensity_days:
            purposes[weekday] = SessionPurpose.INTENSITY

        return purposes

    # ======================================================

    def _select_long_days(
        self,
        *,
        training_days: tuple[Weekday, ...],
        strategy_plan: StrategyPlan,
        availability: AthleteAvailability,
        preferences: AthletePreferences,
        constraints: TrainingConstraints,
    ) -> tuple[Weekday, ...]:
        maximum = min(
            strategy_plan.long_sessions,
            constraints.max_long_sessions,
            len(training_days),
        )

        if maximum <= 0:
            return ()

        candidates = sorted(
            training_days,
            key=lambda weekday: (
                (
                    0
                    if weekday
                    == preferences.preferred_long_day
                    else 1
                ),
                -self._usable_minutes(
                    weekday=weekday,
                    availability=availability,
                    constraints=constraints,
                ),
                -weekday.value,
            ),
        )

        return tuple(candidates[:maximum])

    # ======================================================

    def _select_intensity_days(
        self,
        *,
        training_days: tuple[Weekday, ...],
        excluded_days: set[Weekday],
        strategy_plan: StrategyPlan,
        availability: AthleteAvailability,
        preferences: AthletePreferences,
        constraints: TrainingConstraints,
    ) -> tuple[Weekday, ...]:
        candidates = [
            weekday
            for weekday in training_days
            if weekday not in excluded_days
            and constraints.allows_intensity(weekday)
        ]

        maximum = min(
            strategy_plan.intensity_sessions,
            constraints.max_intensity_sessions,
            len(candidates),
        )

        if maximum <= 0:
            return ()

        preferred_days = set(
            preferences.preferred_intensity_days
        )

        candidates.sort(
            key=lambda weekday: (
                0 if weekday in preferred_days else 1,
                -self._usable_minutes(
                    weekday=weekday,
                    availability=availability,
                    constraints=constraints,
                ),
                weekday.value,
            )
        )

        return tuple(candidates[:maximum])

    # ======================================================
    # Duration allocation
    # ======================================================

    def _allocate_durations(
        self,
        *,
        training_days: tuple[Weekday, ...],
        purposes: dict[Weekday, SessionPurpose],
        strategy_plan: StrategyPlan,
        availability: AthleteAvailability,
        constraints: TrainingConstraints,
    ) -> dict[Weekday, int]:
        if not training_days:
            return {}

        weekly_target = self._weekly_minutes_target(
            strategy_plan=strategy_plan,
            constraints=constraints,
        )

        capacities = {
            weekday: self._usable_minutes(
                weekday=weekday,
                availability=availability,
                constraints=constraints,
            )
            for weekday in training_days
        }

        durations = {
            weekday: 0
            for weekday in training_days
        }

        remaining = weekly_target

        remaining = self._allocate_long_session_minutes(
            durations=durations,
            capacities=capacities,
            purposes=purposes,
            strategy_plan=strategy_plan,
            remaining=remaining,
        )

        self._distribute_remaining_minutes(
            durations=durations,
            capacities=capacities,
            purposes=purposes,
            remaining=remaining,
        )

        return durations

    # ======================================================

    @staticmethod
    def _weekly_minutes_target(
        *,
        strategy_plan: StrategyPlan,
        constraints: TrainingConstraints,
    ) -> int:
        candidates: list[int] = []

        if strategy_plan.target_weekly_minutes is not None:
            candidates.append(
                strategy_plan.target_weekly_minutes
            )

        if constraints.max_weekly_minutes is not None:
            candidates.append(
                constraints.max_weekly_minutes
            )

        if not candidates:
            return 0

        return max(
            0,
            min(candidates),
        )

    # ======================================================

    @staticmethod
    def _allocate_long_session_minutes(
        *,
        durations: dict[Weekday, int],
        capacities: dict[Weekday, int],
        purposes: dict[Weekday, SessionPurpose],
        strategy_plan: StrategyPlan,
        remaining: int,
    ) -> int:
        long_days = [
            weekday
            for weekday, purpose in purposes.items()
            if purpose is SessionPurpose.LONG
        ]

        if not long_days:
            return remaining

        requested = strategy_plan.long_session_minutes

        for weekday in long_days:
            if remaining <= 0:
                break

            target = (
                requested
                if requested is not None
                else capacities[weekday]
            )

            duration = min(
                target,
                capacities[weekday],
                remaining,
            )

            durations[weekday] = duration
            remaining -= duration

        return remaining

    # ======================================================

    @staticmethod
    def _distribute_remaining_minutes(
        *,
        durations: dict[Weekday, int],
        capacities: dict[Weekday, int],
        purposes: dict[Weekday, SessionPurpose],
        remaining: int,
    ) -> None:
        """
        Distributes minutes using small rounds.

        Intensity sessions receive priority over easy sessions once
        the long-session allocation is complete.
        """

        ordered_days = sorted(
            durations,
            key=lambda weekday: (
                WeekStructureGenerator._duration_priority(
                    purposes[weekday]
                ),
                weekday.value,
            ),
        )

        while remaining > 0:
            changed = False

            for weekday in ordered_days:
                capacity_left = (
                    capacities[weekday]
                    - durations[weekday]
                )

                if capacity_left <= 0:
                    continue

                allocation = min(
                    5,
                    capacity_left,
                    remaining,
                )

                durations[weekday] += allocation
                remaining -= allocation
                changed = True

                if remaining <= 0:
                    break

            if not changed:
                break

    # ======================================================

    @staticmethod
    def _duration_priority(
        purpose: SessionPurpose,
    ) -> int:
        priorities = {
            SessionPurpose.INTENSITY: 0,
            SessionPurpose.EASY: 1,
            SessionPurpose.CROSS_TRAINING: 2,
            SessionPurpose.RECOVERY: 3,
            SessionPurpose.LONG: 4,
            SessionPurpose.RACE: 5,
        }

        return priorities.get(
            purpose,
            6,
        )

    # ======================================================
    # Slot creation
    # ======================================================

    def _build_slots(
        self,
        *,
        training_days: tuple[Weekday, ...],
        purposes: dict[Weekday, SessionPurpose],
        durations: dict[Weekday, int],
        availability: AthleteAvailability,
        preferences: AthletePreferences,
        constraints: TrainingConstraints,
    ) -> list[DraftTrainingSlot]:
        training_day_set = set(training_days)
        slots: list[DraftTrainingSlot] = []

        for weekday in Weekday:
            if weekday in training_day_set:
                duration = durations.get(
                    weekday,
                    0,
                )

                if duration > 0:
                    purpose = purposes[weekday]

                    slots.append(
                        DraftTrainingSlot(
                            weekday=weekday,
                            purpose=purpose,
                            duration_minutes=duration,
                            notes=self._notes_for_purpose(
                                purpose
                            ),
                        )
                    )

                    continue

            slots.append(
                DraftTrainingSlot.rest(
                    weekday,
                    notes=self._rest_note(
                        weekday=weekday,
                        availability=availability,
                        preferences=preferences,
                        constraints=constraints,
                    ),
                )
            )

        return slots

    # ======================================================

    @staticmethod
    def _notes_for_purpose(
        purpose: SessionPurpose,
    ) -> str:
        notes = {
            SessionPurpose.EASY: (
                "Easy session assigned from the strategy plan."
            ),
            SessionPurpose.INTENSITY: (
                "Intensity session assigned from the strategy plan."
            ),
            SessionPurpose.LONG: (
                "Long session assigned from the strategy plan."
            ),
            SessionPurpose.RECOVERY: (
                "Recovery session assigned from the strategy plan."
            ),
            SessionPurpose.CROSS_TRAINING: (
                "Cross-training session assigned from the strategy plan."
            ),
            SessionPurpose.RACE: (
                "Race session assigned from the strategy plan."
            ),
        }

        return notes.get(
            purpose,
            "Training session assigned from the strategy plan.",
        )

    # ======================================================

    @staticmethod
    def _rest_note(
        *,
        weekday: Weekday,
        availability: AthleteAvailability,
        preferences: AthletePreferences,
        constraints: TrainingConstraints,
    ) -> str:
        if constraints.is_blocked(weekday):
            return (
                "Training is blocked by an athlete constraint."
            )

        if availability.minutes_for(weekday) <= 0:
            return "The athlete is unavailable."

        if preferences.prefers_rest(weekday):
            return "Preferred rest day."

        return (
            "Rest day selected to respect the strategy's "
            "session target."
        )

    # ======================================================
    # Recovery and constraints
    # ======================================================

    def _apply_recovery_guidance(
        self,
        *,
        slots: list[DraftTrainingSlot],
        strategy_plan: StrategyPlan,
        constraints: TrainingConstraints,
    ) -> list[DraftTrainingSlot]:
        """
        Satisfies recovery guidance using rest days first.

        When the strategy requests more recovery days than the week
        currently contains, easy sessions are converted to active
        recovery before demanding sessions are removed.
        """

        required = max(
            strategy_plan.recovery_days,
            constraints.minimum_recovery_days,
        )

        current = sum(
            slot.is_rest
            or slot.purpose is SessionPurpose.RECOVERY
            for slot in slots
        )

        missing = required - current

        if missing <= 0:
            return slots

        candidates = sorted(
            (
                slot
                for slot in slots
                if slot.purpose is SessionPurpose.EASY
            ),
            key=lambda slot: (
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
                slot.with_purpose(
                    SessionPurpose.RECOVERY,
                    notes=(
                        "Active recovery assigned to satisfy "
                        "the strategy's recovery guidance."
                    ),
                )
                if slot.weekday in selected_days
                else slot
            )
            for slot in slots
        ]

    # ======================================================

    # ======================================================
    # Shared helpers
    # ======================================================

    @staticmethod
    def _usable_minutes(
        *,
        weekday: Weekday,
        availability: AthleteAvailability,
        constraints: TrainingConstraints,
    ) -> int:
        limits = [
            availability.minutes_for(weekday),
        ]

        day_limit = constraints.duration_limit_for(
            weekday
        )

        if day_limit is not None:
            limits.append(day_limit)

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
                "availability must be an AthleteAvailability."
            )

        if not isinstance(
            preferences,
            AthletePreferences,
        ):
            raise TypeError(
                "preferences must be an AthletePreferences."
            )

        if not isinstance(
            constraints,
            TrainingConstraints,
        ):
            raise TypeError(
                "constraints must be TrainingConstraints."
            )