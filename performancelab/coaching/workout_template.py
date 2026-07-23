"""
PerformanceLab

Workout Template

Reusable description of a planned training session.
"""

from dataclasses import dataclass

from .session_purpose import SessionPurpose


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

    def __repr__(self) -> str:

        return (
            f"WorkoutTemplate("
            f"purpose={self.purpose.value!r}, "
            f"title={self.title!r}, "
            f"sport={self.sport!r})"
        )