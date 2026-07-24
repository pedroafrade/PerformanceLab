"""
PerformanceLab

Workout Template

Reusable description of a planned training session.
"""

from dataclasses import dataclass

from .session_purpose import SessionPurpose
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

    def customized_for(
        self,
        strategy_plan: StrategyPlan,
    ) -> "WorkoutTemplate":
        """
        Returns a copy enriched with weekly strategy guidance.

        Strategy guidance is included as descriptive information.
        This method does not reinterpret session purpose, duration,
        intensity, or structure.
        """

        if not isinstance(
            strategy_plan,
            StrategyPlan,
        ):
            raise TypeError(
                "strategy_plan must be a StrategyPlan"
            )

        return WorkoutTemplate(
            purpose=self.purpose,
            title=self.title,
            objective=self._customized_objective(
                strategy_plan
            ),
            intensity=self.intensity,
            description=self._customized_description(
                strategy_plan
            ),
            structure=self.structure,
            equipment=self.equipment,
            sport=self.sport,
        )
        # ======================================================

    def _customized_objective(
        self,
        strategy_plan: StrategyPlan,
    ) -> str:

        if not strategy_plan.objectives:
            return self.objective

        weekly_objectives = "; ".join(
            strategy_plan.objectives
        )

        return (
            f"{self.objective} "
            f"Weekly objectives: {weekly_objectives}"
        )

    # ======================================================

    def _customized_description(
        self,
        strategy_plan: StrategyPlan,
    ) -> str:

        sections: list[str] = []

        if self.description:
            sections.append(
                self.description.strip()
            )

        if strategy_plan.focus is not None:
            sections.append(
                f"Weekly focus: {strategy_plan.focus}."
            )

        if strategy_plan.guidelines:
            sections.append(
                "Weekly guidelines: "
                + " ".join(strategy_plan.guidelines)
            )

        if strategy_plan.warnings:
            sections.append(
                "Weekly warnings: "
                + " ".join(strategy_plan.warnings)
            )

        return " ".join(sections)
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

    def __repr__(self) -> str:

        return (
            f"WorkoutTemplate("
            f"purpose={self.purpose.value!r}, "
            f"title={self.title!r}, "
            f"sport={self.sport!r})"
        )