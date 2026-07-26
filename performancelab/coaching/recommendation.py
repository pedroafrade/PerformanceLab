"""
PerformanceLab

Coaching Recommendation

Presentation-oriented coaching language built from deterministic
coaching and workout data.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .analyzer import CoachAnalysis
from .context import CoachContext
from .session_purpose import SessionPurpose

if TYPE_CHECKING:
    from .strategy import StrategyPlan
    from .workout_template import WorkoutTemplate


@dataclass(frozen=True)
class CoachRecommendation:
    """
    Complete recommendation returned by the coaching engine.

    Besides storing the high-level coaching result, this class
    translates structured strategy data into concise, natural
    language for athlete-facing interfaces.
    """

    context: CoachContext
    analysis: CoachAnalysis
    strategy: str
    summary: str
    warnings: tuple[str, ...] = field(
        default_factory=tuple
    )

    @classmethod
    def workout_summary(
        cls,
        *,
        strategy_plan: "StrategyPlan",
        workout_template: "WorkoutTemplate",
    ) -> str:
        """
        Builds natural coaching notes for one workout.
        """

        paragraphs: list[str] = []

        for paragraph in (
            cls._context_paragraph(
                strategy_plan=strategy_plan,
                workout_template=workout_template,
            ),
            cls._execution_paragraph(
                strategy_plan=strategy_plan,
                workout_template=workout_template,
            ),
            cls._caution_paragraph(
                strategy_plan=strategy_plan,
            ),
        ):
            if paragraph:
                paragraphs.append(
                    paragraph
                )

        return "\n\n".join(
            paragraphs
        )

    @classmethod
    def _context_paragraph(
        cls,
        *,
        strategy_plan: "StrategyPlan",
        workout_template: "WorkoutTemplate",
    ) -> str:
        recovery_priority = str(
            strategy_plan.recovery_priority
            or "normal"
        ).strip().lower()

        weekly_focus = cls._focus_text(
            strategy_plan.focus
        )

        if recovery_priority == "high":
            return (
                "This session belongs to a recovery-focused week "
                "after a period of accumulated fatigue. The aim is "
                "to preserve movement and routine while allowing "
                "freshness to return."
            )

        if recovery_priority in {
            "elevated",
            "medium",
            "moderate",
        }:
            return (
                "Recovery remains an important priority this week, "
                "so this session should support adaptation without "
                "adding unnecessary fatigue."
            )

        if weekly_focus:
            return (
                f"This session supports the week's {weekly_focus} "
                "focus and contributes to the current training phase."
            )

        if workout_template.description:
            return cls._ensure_sentence(
                workout_template.description
            )

        return (
            "This session supports the current training phase and "
            "should be completed with controlled, purposeful effort."
        )

    @classmethod
    def _execution_paragraph(
        cls,
        *,
        strategy_plan: "StrategyPlan",
        workout_template: "WorkoutTemplate",
    ) -> str:
        purpose = workout_template.purpose
        primary_focus = cls._focus_text(
            strategy_plan.key_session_focus
        )
        secondary_focus = cls._focus_text(
            strategy_plan.secondary_focus
        )

        if purpose is SessionPurpose.RECOVERY:
            return (
                "Keep the effort very easy and relaxed throughout. "
                "You should finish feeling better than when you "
                "started, not as though you completed a training test."
            )

        if purpose is SessionPurpose.EASY:
            focus = secondary_focus or "aerobic endurance"

            return (
                f"Keep the session comfortably aerobic, using a "
                f"conversational effort to develop {focus}. Avoid "
                "turning the final part into an unplanned hard effort."
            )

        if purpose is SessionPurpose.LONG:
            focus = secondary_focus or "aerobic durability"

            return (
                f"Settle into a sustainable rhythm and use the session "
                f"to develop {focus}. The priority is steady execution "
                "and good energy management rather than finishing at "
                "maximal effort."
            )

        if purpose is SessionPurpose.INTENSITY:
            focus = primary_focus or "the planned quality stimulus"

            return (
                f"The main work should target {focus}. Complete the "
                "repetitions with consistent technique and controlled "
                "pacing, leaving enough reserve to maintain quality "
                "through the final effort."
            )

        if purpose is SessionPurpose.RACE:
            specificity = round(
                strategy_plan.race_specificity * 100
            )

            if specificity > 0:
                return (
                    f"Use this session to rehearse race execution, "
                    f"with approximately {specificity}% race-specific "
                    "emphasis. Prioritise pacing, fuelling and decisions "
                    "that can be repeated on event day."
                )

            return (
                "Treat this session as a rehearsal of race execution. "
                "Prioritise pacing, fuelling and calm decision-making."
            )

        if purpose is SessionPurpose.CROSS_TRAINING:
            return (
                "Keep the effort aerobic and technically controlled. "
                "The session should complement the main sport without "
                "creating fatigue that compromises the next key workout."
            )

        if workout_template.description:
            return cls._ensure_sentence(
                workout_template.description
            )

        return (
            "Complete the session with controlled effort and adjust "
            "the intensity if technique or movement quality begins "
            "to deteriorate."
        )

    @classmethod
    def _caution_paragraph(
        cls,
        *,
        strategy_plan: "StrategyPlan",
    ) -> str:
        recovery_priority = str(
            strategy_plan.recovery_priority
            or "normal"
        ).strip().lower()

        if recovery_priority == "high":
            return (
                "If fatigue still feels unusually high, shorten the "
                "session or replace it with complete rest. Postpone "
                "threshold, interval and maximal-strength work until "
                "recovery indicators improve."
            )

        return cls._selected_advice(
            strategy_plan
        )

    @classmethod
    def _selected_advice(
        cls,
        strategy_plan: "StrategyPlan",
    ) -> str:
        """
        Selects at most one guideline and one warning.
        """

        parts: list[str] = []

        if strategy_plan.guidelines:
            parts.append(
                cls._ensure_sentence(
                    strategy_plan.guidelines[0]
                )
            )

        if strategy_plan.warnings:
            warning = cls._ensure_sentence(
                strategy_plan.warnings[0]
            )

            if warning not in parts:
                parts.append(
                    warning
                )

        return " ".join(
            parts
        )

    @staticmethod
    def _focus_text(
        focus,
    ) -> str:
        if focus is None:
            return ""

        value = getattr(
            focus,
            "value",
            focus,
        )

        return str(
            value
        ).strip().lower()

    @staticmethod
    def _ensure_sentence(
        value: str,
    ) -> str:
        cleaned = " ".join(
            str(value).split()
        )

        if not cleaned:
            return ""

        if cleaned[-1] not in ".!?":
            return f"{cleaned}."

        return cleaned