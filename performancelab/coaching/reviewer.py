"""
PerformanceLab

Coach Reviewer

Reviews a provisional weekly structure after generation or
manual adjustment by the athlete.

The reviewer explains problems and trade-offs. It does not
prevent the athlete from changing the plan.
"""

from collections.abc import Sequence

from .availability import (
    AthleteAvailability,
    Weekday,
)
from .constraints import TrainingConstraints
from .draft_slot import DraftTrainingSlot
from .preferences import AthletePreferences
from .review import (
    PlanReview,
    ReviewCategory,
    ReviewFinding,
    ReviewSeverity,
)
from .session_purpose import SessionPurpose
from .strategy import StrategyPlan


class CoachReviewer:
    """
    Reviews a provisional weekly training structure.
    """

    # ======================================================

    def review(
        self,
        *,
        slots: Sequence[DraftTrainingSlot],
        strategy_plan: StrategyPlan,
        availability: AthleteAvailability,
        preferences: AthletePreferences,
        constraints: TrainingConstraints,
    ) -> PlanReview:
        """
        Reviews a sequence of provisional training slots.
        """

        self._validate_inputs(
            slots=slots,
            strategy_plan=strategy_plan,
            availability=availability,
            preferences=preferences,
            constraints=constraints,
        )

        normalized_slots = tuple(
            sorted(
                slots,
                key=lambda slot: slot.weekday.value,
            )
        )

        findings: list[ReviewFinding] = []

        findings.extend(
            self._review_weekday_structure(
                normalized_slots,
            )
        )

        findings.extend(
            self._review_availability(
                normalized_slots,
                availability,
            )
        )

        findings.extend(
            self._review_constraints(
                normalized_slots,
                constraints,
            )
        )

        findings.extend(
            self._review_preferences(
                normalized_slots,
                preferences,
            )
        )

        availability_score = self._category_score(
            findings,
            ReviewCategory.AVAILABILITY,
        )

        constraint_score = self._category_score(
            findings,
            ReviewCategory.CONSTRAINT,
        )

        recovery_score = self._recovery_score(
            findings,
        )

        consistency_score = self._consistency_score(
            normalized_slots,
            findings,
        )

        score = self._score_findings(
            findings,
        )

        return PlanReview(
            score=score,
            consistency_score=consistency_score,
            recovery_score=recovery_score,
            availability_score=availability_score,
            constraint_score=constraint_score,
            findings=tuple(findings),
            summary=self._summary(
                findings,
            ),
        )

    # ======================================================

    def _review_weekday_structure(
        self,
        slots: tuple[DraftTrainingSlot, ...],
    ) -> list[ReviewFinding]:

        findings: list[ReviewFinding] = []

        counts = {
            weekday: 0
            for weekday in Weekday
        }

        for slot in slots:

            counts[slot.weekday] += 1

        for weekday, count in counts.items():

            if count == 0:

                findings.append(
                    ReviewFinding(
                        code="missing_weekday",
                        message=(
                            f"{weekday.label} has no draft "
                            "training slot."
                        ),
                        severity=ReviewSeverity.ERROR,
                        category=(
                            ReviewCategory.SCHEDULING
                        ),
                        day=weekday,
                        suggestion=(
                            "Add a rest or training slot "
                            "for this weekday."
                        ),
                    )
                )

            elif count > 1:

                findings.append(
                    ReviewFinding(
                        code="duplicate_weekday",
                        message=(
                            f"{weekday.label} has more than "
                            "one draft training slot."
                        ),
                        severity=ReviewSeverity.ERROR,
                        category=(
                            ReviewCategory.SCHEDULING
                        ),
                        day=weekday,
                        suggestion=(
                            "Keep only one provisional slot "
                            "for each weekday."
                        ),
                    )
                )

        return findings

    # ======================================================

    def _review_availability(
        self,
        slots: tuple[DraftTrainingSlot, ...],
        availability: AthleteAvailability,
    ) -> list[ReviewFinding]:

        findings: list[ReviewFinding] = []

        for slot in slots:

            if slot.is_rest:

                continue

            available_minutes = (
                availability.minutes_for(
                    slot.weekday,
                )
            )

            if available_minutes <= 0:

                findings.append(
                    ReviewFinding(
                        code="training_when_unavailable",
                        message=(
                            "Training is scheduled when the "
                            "athlete is unavailable."
                        ),
                        severity=ReviewSeverity.ERROR,
                        category=(
                            ReviewCategory.AVAILABILITY
                        ),
                        day=slot.weekday,
                        suggestion=(
                            "Move the session to an "
                            "available weekday."
                        ),
                    )
                )

                continue

            if (
                slot.duration_minutes is not None
                and slot.duration_minutes
                > available_minutes
            ):

                findings.append(
                    ReviewFinding(
                        code="duration_exceeds_availability",
                        message=(
                            "The proposed session duration "
                            "exceeds the athlete's available "
                            "time."
                        ),
                        severity=ReviewSeverity.ERROR,
                        category=(
                            ReviewCategory.AVAILABILITY
                        ),
                        day=slot.weekday,
                        suggestion=(
                            f"Reduce the session to "
                            f"{available_minutes} minutes or "
                            "move it to another day."
                        ),
                    )
                )

        return findings

    # ======================================================

    def _review_constraints(
        self,
        slots: tuple[DraftTrainingSlot, ...],
        constraints: TrainingConstraints,
    ) -> list[ReviewFinding]:

        findings: list[ReviewFinding] = []

        findings.extend(
            self._review_daily_constraints(
                slots,
                constraints,
            )
        )

        findings.extend(
            self._review_weekly_duration(
                slots,
                constraints,
            )
        )

        findings.extend(
            self._review_session_counts(
                slots,
                constraints,
            )
        )

        findings.extend(
            self._review_consecutive_days(
                slots,
                constraints,
            )
        )

        findings.extend(
            self._review_recovery_days(
                slots,
                constraints,
            )
        )

        return findings

    # ======================================================

    def _review_daily_constraints(
        self,
        slots: tuple[DraftTrainingSlot, ...],
        constraints: TrainingConstraints,
    ) -> list[ReviewFinding]:

        findings: list[ReviewFinding] = []

        for slot in slots:

            if slot.is_rest:

                continue

            if constraints.is_blocked(slot.weekday):

                findings.append(
                    ReviewFinding(
                        code="training_on_blocked_day",
                        message=(
                            "Training is scheduled on a "
                            "blocked weekday."
                        ),
                        severity=ReviewSeverity.ERROR,
                        category=ReviewCategory.CONSTRAINT,
                        day=slot.weekday,
                        suggestion=(
                            "Move the session to a weekday "
                            "that is not blocked."
                        ),
                    )
                )

            if (
                slot.is_intensity
                and not constraints.allows_intensity(
                    slot.weekday,
                )
            ):

                findings.append(
                    ReviewFinding(
                        code="intensity_not_allowed",
                        message=(
                            "An intensity session is "
                            "scheduled on a weekday where "
                            "intensity is not allowed."
                        ),
                        severity=ReviewSeverity.ERROR,
                        category=ReviewCategory.INTENSITY,
                        day=slot.weekday,
                        suggestion=(
                            "Move the intensity session or "
                            "change its purpose."
                        ),
                    )
                )

            if (
                slot.duration_minutes is not None
                and not constraints.allows_duration(
                    slot.weekday,
                    slot.duration_minutes,
                )
            ):

                findings.append(
                    ReviewFinding(
                        code="duration_exceeds_constraint",
                        message=(
                            "The session duration exceeds "
                            "the configured duration limit."
                        ),
                        severity=ReviewSeverity.ERROR,
                        category=ReviewCategory.CONSTRAINT,
                        day=slot.weekday,
                        suggestion=(
                            "Reduce the session duration."
                        ),
                    )
                )

        return findings

    # ======================================================

    def _review_weekly_duration(
        self,
        slots: tuple[DraftTrainingSlot, ...],
        constraints: TrainingConstraints,
    ) -> list[ReviewFinding]:

        maximum = constraints.max_weekly_minutes

        if maximum is None:

            return []

        total = sum(
            slot.duration_minutes or 0
            for slot in slots
        )

        if total <= maximum:

            return []

        return [
            ReviewFinding(
                code="weekly_duration_exceeded",
                message=(
                    f"The weekly structure contains "
                    f"{total} minutes, exceeding the "
                    f"{maximum}-minute limit."
                ),
                severity=ReviewSeverity.ERROR,
                category=ReviewCategory.VOLUME,
                suggestion=(
                    "Reduce the duration or remove one or "
                    "more sessions."
                ),
            )
        ]

    # ======================================================

    def _review_session_counts(
        self,
        slots: tuple[DraftTrainingSlot, ...],
        constraints: TrainingConstraints,
    ) -> list[ReviewFinding]:

        findings: list[ReviewFinding] = []

        intensity_count = sum(
            slot.purpose is SessionPurpose.INTENSITY
            for slot in slots
        )

        if (
            intensity_count
            > constraints.max_intensity_sessions
        ):

            findings.append(
                ReviewFinding(
                    code="too_many_intensity_sessions",
                    message=(
                        f"The structure contains "
                        f"{intensity_count} intensity "
                        "sessions."
                    ),
                    severity=ReviewSeverity.ERROR,
                    category=ReviewCategory.INTENSITY,
                    suggestion=(
                        "Convert or remove one or more "
                        "intensity sessions."
                    ),
                )
            )

        long_count = sum(
            slot.purpose is SessionPurpose.LONG
            for slot in slots
        )

        if long_count > constraints.max_long_sessions:

            findings.append(
                ReviewFinding(
                    code="too_many_long_sessions",
                    message=(
                        f"The structure contains "
                        f"{long_count} long sessions."
                    ),
                    severity=ReviewSeverity.ERROR,
                    category=ReviewCategory.VOLUME,
                    suggestion=(
                        "Keep only the permitted number of "
                        "long sessions."
                    ),
                )
            )

        return findings

    # ======================================================

    def _review_consecutive_days(
        self,
        slots: tuple[DraftTrainingSlot, ...],
        constraints: TrainingConstraints,
    ) -> list[ReviewFinding]:

        maximum = (
            constraints.max_consecutive_training_days
        )

        consecutive = 0
        findings: list[ReviewFinding] = []

        for slot in slots:

            if slot.is_rest:

                consecutive = 0

                continue

            consecutive += 1

            if consecutive > maximum:

                findings.append(
                    ReviewFinding(
                        code="consecutive_days_exceeded",
                        message=(
                            "The maximum number of "
                            "consecutive training days has "
                            "been exceeded."
                        ),
                        severity=ReviewSeverity.WARNING,
                        category=ReviewCategory.RECOVERY,
                        day=slot.weekday,
                        suggestion=(
                            "Insert a rest day before this "
                            "session."
                        ),
                    )
                )

                break

        return findings

    # ======================================================

    def _review_recovery_days(
        self,
        slots: tuple[DraftTrainingSlot, ...],
        constraints: TrainingConstraints,
    ) -> list[ReviewFinding]:

        rest_days = sum(
            slot.is_rest
            for slot in slots
        )

        required = constraints.minimum_recovery_days

        if rest_days >= required:

            return []

        return [
            ReviewFinding(
                code="insufficient_recovery_days",
                message=(
                    f"The structure contains {rest_days} "
                    f"rest days, but at least {required} "
                    "are required."
                ),
                severity=ReviewSeverity.WARNING,
                category=ReviewCategory.RECOVERY,
                suggestion=(
                    "Convert an easy session into a rest "
                    "day."
                ),
            )
        ]

    # ======================================================

    def _review_preferences(
        self,
        slots: tuple[DraftTrainingSlot, ...],
        preferences: AthletePreferences,
    ) -> list[ReviewFinding]:

        findings: list[ReviewFinding] = []

        preferred_long_day = (
            preferences.preferred_long_day
        )

        if preferred_long_day is not None:

            long_slot = next(
                (
                    slot
                    for slot in slots
                    if slot.is_long
                ),
                None,
            )

            if (
                long_slot is not None
                and long_slot.weekday
                != preferred_long_day
            ):

                findings.append(
                    ReviewFinding(
                        code="long_day_preference_not_met",
                        message=(
                            "The long session is not placed "
                            "on the athlete's preferred "
                            "weekday."
                        ),
                        severity=ReviewSeverity.INFO,
                        category=ReviewCategory.PREFERENCE,
                        day=long_slot.weekday,
                        suggestion=(
                            f"Consider moving it to "
                            f"{preferred_long_day.label}."
                        ),
                    )
                )

        for weekday in preferences.preferred_rest_days:

            slot = self._slot_for_day(
                slots,
                weekday,
            )

            if slot is not None and slot.is_training:

                findings.append(
                    ReviewFinding(
                        code="rest_preference_not_met",
                        message=(
                            "Training is scheduled on a "
                            "preferred rest day."
                        ),
                        severity=ReviewSeverity.INFO,
                        category=ReviewCategory.PREFERENCE,
                        day=weekday,
                        suggestion=(
                            "Move the session when practical."
                        ),
                    )
                )

        return findings

    # ======================================================

    @staticmethod
    def _category_score(
        findings: list[ReviewFinding],
        category: ReviewCategory,
    ) -> int:

        relevant = [
            finding
            for finding in findings
            if finding.category is category
        ]

        return CoachReviewer._score_findings(
            relevant,
        )

    # ======================================================

    @staticmethod
    def _recovery_score(
        findings: list[ReviewFinding],
    ) -> int:

        relevant_categories = {
            ReviewCategory.RECOVERY,
            ReviewCategory.INTENSITY,
        }

        relevant = [
            finding
            for finding in findings
            if finding.category
            in relevant_categories
        ]

        return CoachReviewer._score_findings(
            relevant,
        )

    # ======================================================

    @staticmethod
    def _consistency_score(
        slots: tuple[DraftTrainingSlot, ...],
        findings: list[ReviewFinding],
    ) -> int:

        scheduling_findings = [
            finding
            for finding in findings
            if finding.category
            is ReviewCategory.SCHEDULING
        ]

        score = CoachReviewer._score_findings(
            scheduling_findings,
        )

        represented_days = {
            slot.weekday
            for slot in slots
        }

        completeness = round(
            len(represented_days)
            / len(Weekday)
            * 100
        )

        return min(
            score,
            completeness,
        )

    # ======================================================

    @staticmethod
    def _score_findings(
        findings: list[ReviewFinding],
    ) -> int:

        deductions = {
            ReviewSeverity.INFO: 2,
            ReviewSeverity.WARNING: 10,
            ReviewSeverity.ERROR: 25,
        }

        score = 100

        for finding in findings:

            score -= deductions[
                finding.severity
            ]

        return max(
            0,
            score,
        )

    # ======================================================

    @staticmethod
    def _summary(
        findings: list[ReviewFinding],
    ) -> str:

        errors = sum(
            finding.severity
            is ReviewSeverity.ERROR
            for finding in findings
        )

        warnings = sum(
            finding.severity
            is ReviewSeverity.WARNING
            for finding in findings
        )

        information = sum(
            finding.severity
            is ReviewSeverity.INFO
            for finding in findings
        )

        if not findings:

            return (
                "The weekly structure respects the current "
                "availability, preferences and constraints."
            )

        return (
            f"The review found {errors} errors, "
            f"{warnings} warnings and "
            f"{information} informational observations."
        )

    # ======================================================

    @staticmethod
    def _slot_for_day(
        slots: tuple[DraftTrainingSlot, ...],
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
        slots: Sequence[DraftTrainingSlot],
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

        if not all(
            isinstance(slot, DraftTrainingSlot)
            for slot in slots
        ):

            raise TypeError(
                "All slots must be DraftTrainingSlot "
                "instances."
            )