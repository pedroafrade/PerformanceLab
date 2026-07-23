"""
PerformanceLab

Draft Training Slot

Represents one provisional position in a weekly training
structure.

A draft slot contains coaching intent only. It does not
represent a complete workout prescription.
"""

from dataclasses import dataclass, replace

from ..training.config.availability import Weekday
from .session_purpose import SessionPurpose


@dataclass(frozen=True)
class DraftTrainingSlot:
    """
    Represents the planned purpose of one weekday.

    Parameters
    ----------
    weekday:
        Weekday represented by this slot.

    purpose:
        High-level coaching purpose of the slot.

    duration_minutes:
        Proposed duration in minutes.

        Rest slots must not have a duration. Training slots
        may temporarily have no duration while the structure
        is still being developed.

    notes:
        Optional explanation or coaching note.
    """

    weekday: Weekday

    purpose: SessionPurpose

    duration_minutes: int | None = None

    notes: str | None = None

    # ======================================================

    def __post_init__(self) -> None:

        try:

            weekday = Weekday(
                self.weekday,
            )

        except (TypeError, ValueError) as error:

            raise ValueError(
                f"Invalid weekday: {self.weekday!r}"
            ) from error

        try:

            purpose = SessionPurpose(
                self.purpose,
            )

        except (TypeError, ValueError) as error:

            raise ValueError(
                f"Invalid session purpose: "
                f"{self.purpose!r}"
            ) from error

        duration = self.duration_minutes

        if duration is not None:

            if isinstance(duration, bool):

                raise TypeError(
                    "duration_minutes must be an integer."
                )

            duration = int(
                duration,
            )

            if duration < 0:

                raise ValueError(
                    "duration_minutes cannot be negative."
                )

        if (
            purpose is SessionPurpose.REST
            and duration is not None
        ):

            raise ValueError(
                "A rest slot cannot have a duration."
            )

        notes = (
            self.notes.strip()
            if self.notes
            else None
        )

        object.__setattr__(
            self,
            "weekday",
            weekday,
        )

        object.__setattr__(
            self,
            "purpose",
            purpose,
        )

        object.__setattr__(
            self,
            "duration_minutes",
            duration,
        )

        object.__setattr__(
            self,
            "notes",
            notes,
        )

    # ======================================================

    @classmethod
    def rest(
        cls,
        weekday: Weekday,
        *,
        notes: str | None = None,
    ) -> "DraftTrainingSlot":
        """
        Creates a rest slot.
        """

        return cls(
            weekday=weekday,
            purpose=SessionPurpose.REST,
            duration_minutes=None,
            notes=notes,
        )

    # ======================================================

    @property
    def is_rest(self) -> bool:
        """
        Returns whether this is a rest slot.
        """

        return (
            self.purpose
            is SessionPurpose.REST
        )

    # ======================================================

    @property
    def is_training(self) -> bool:
        """
        Returns whether this slot represents training.
        """

        return not self.is_rest

    # ======================================================

    @property
    def is_intensity(self) -> bool:
        """
        Returns whether this is an intensity slot.
        """

        return (
            self.purpose
            is SessionPurpose.INTENSITY
        )

    # ======================================================

    @property
    def is_long(self) -> bool:
        """
        Returns whether this is a long-session slot.
        """

        return (
            self.purpose
            is SessionPurpose.LONG
        )

    # ======================================================

    @property
    def is_quality(self) -> bool:
        """
        Returns whether the slot normally requires additional
        recovery.
        """

        return self.purpose.is_quality

    # ======================================================

    @property
    def has_duration(self) -> bool:
        """
        Returns whether a duration has been assigned.
        """

        return (
            self.duration_minutes
            is not None
        )

    # ======================================================

    def with_purpose(
        self,
        purpose: SessionPurpose,
        *,
        notes: str | None = None,
    ) -> "DraftTrainingSlot":
        """
        Returns a copy with a different session purpose.

        Changing a slot to rest automatically removes its
        duration.
        """

        normalized_purpose = SessionPurpose(
            purpose,
        )

        duration = self.duration_minutes

        if normalized_purpose is SessionPurpose.REST:

            duration = None

        return replace(
            self,
            purpose=normalized_purpose,
            duration_minutes=duration,
            notes=(
                self.notes
                if notes is None
                else notes
            ),
        )

    # ======================================================

    def with_duration(
        self,
        duration_minutes: int | None,
    ) -> "DraftTrainingSlot":
        """
        Returns a copy with a different duration.
        """

        if self.is_rest and duration_minutes is not None:

            raise ValueError(
                "A rest slot cannot have a duration."
            )

        return replace(
            self,
            duration_minutes=duration_minutes,
        )

    # ======================================================

    def move_to(
        self,
        weekday: Weekday,
    ) -> "DraftTrainingSlot":
        """
        Returns a copy assigned to another weekday.
        """

        return replace(
            self,
            weekday=Weekday(weekday),
        )