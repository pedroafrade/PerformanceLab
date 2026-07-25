"""
PerformanceLab

Workout Template

Reusable description of a planned training session.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .session_purpose import SessionPurpose
if TYPE_CHECKING:
    from .strategy import StrategyPlan


@dataclass(frozen=True)
class WorkoutTemplate:
    """
    Describes the content of a planned workout.

    A WorkoutTemplate does not contain a date or duration.
    Those values come from a DraftTrainingSlot when the
    template is converted into a PlannedWorkout.
    """

    purpose: SessionPurpose
    title: str
    objective: str
    intensity: str
    description: str = ""
    structure: tuple[str, ...] = ()
    equipment: tuple[str, ...] = ()
    sport: str | None = None

    # ======================================================

    def __post_init__(self) -> None:
        if not isinstance(
            self.purpose,
            SessionPurpose,
        ):
            raise TypeError(
                "purpose must be a SessionPurpose"
            )

        self._validate_required_text(
            "title",
            self.title,
        )
        self._validate_required_text(
            "objective",
            self.objective,
        )
        self._validate_required_text(
            "intensity",
            self.intensity,
        )
        self._validate_optional_text(
            "description",
            self.description,
        )

        if self.sport is not None:
            self._validate_required_text(
                "sport",
                self.sport,
            )

        self._validate_text_tuple(
            "structure",
            self.structure,
        )
        self._validate_text_tuple(
            "equipment",
            self.equipment,
        )

    # ======================================================

    @staticmethod
    def _validate_required_text(
        field_name: str,
        value: str,
    ) -> None:
        if not isinstance(value, str):
            raise TypeError(
                f"{field_name} must be a string"
            )

        if not value.strip():
            raise ValueError(
                f"{field_name} cannot be empty"
            )

    # ======================================================

    @staticmethod
    def _validate_optional_text(
        field_name: str,
        value: str,
    ) -> None:
        if not isinstance(value, str):
            raise TypeError(
                f"{field_name} must be a string"
            )

    # ======================================================

    @staticmethod
    def _validate_text_tuple(
        field_name: str,
        values: tuple[str, ...],
    ) -> None:
        if not isinstance(values, tuple):
            raise TypeError(
                f"{field_name} must be a tuple"
            )

        for value in values:
            if not isinstance(value, str):
                raise TypeError(
                    f"{field_name} must contain strings"
                )

            if not value.strip():
                raise ValueError(
                    f"{field_name} cannot contain "
                    "empty values"
                )

    # ======================================================

    def for_sport(
        self,
        sport: str,
    ) -> "WorkoutTemplate":
        """
        Returns a copy of this template assigned to a sport.
        """

        return WorkoutTemplate(
            purpose=self.purpose,
            title=self.title,
            objective=self.objective,
            intensity=self.intensity,
            description=self.description,
            structure=self.structure,
            equipment=self.equipment,
            sport=sport,
        )

    # ======================================================

    def customized_for(
        self,
        strategy_plan: "StrategyPlan",
    ) -> "WorkoutTemplate":
        """
        Returns a copy enriched with the strategy plan context.
        """

        from .strategy import StrategyPlan

        if not isinstance(
            strategy_plan,
            StrategyPlan,
        ):
            raise TypeError(
                "strategy_plan must be a StrategyPlan"
            )

        objective = self.objective
        description_parts: list[str] = []

        if self.description:
            description_parts.append(
                self.description
            )

        if strategy_plan.objectives:
            objective = (
                f"{self.objective} "
                f"{' '.join(strategy_plan.objectives)}"
            )

        if strategy_plan.focus is not None:
            focus_value = getattr(
                strategy_plan.focus,
                "value",
                str(strategy_plan.focus),
            )
            description_parts.append(
                f"Weekly focus: {focus_value}."
            )

        description_parts.extend(
            strategy_plan.guidelines
        )
        description_parts.extend(
            strategy_plan.warnings
        )

        return WorkoutTemplate(
            purpose=self.purpose,
            title=self.title,
            objective=objective,
            intensity=self.intensity,
            description=" ".join(
                description_parts
            ),
            structure=self.structure,
            equipment=self.equipment,
            sport=self.sport,
        )

    # ======================================================

    def __repr__(self) -> str:
        return (
            f"WorkoutTemplate("
            f"purpose={self.purpose.value!r}, "
            f"title={self.title!r}, "
            f"sport={self.sport!r})"
        )
