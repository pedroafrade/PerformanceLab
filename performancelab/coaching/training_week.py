"""
PerformanceLab

Training Week

Represents one concrete training week.

A TrainingWeek combines the abstract weekly structure produced by
WeekStructureGenerator with a calendar week. This is the bridge
between coaching decisions (weekday-based) and scheduled workouts
(date-based).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from .draft_slot import DraftTrainingSlot


@dataclass(frozen=True)
class TrainingWeek:
    """
    Represents one calendar training week.

    Parameters
    ----------
    start_date:
        Monday of the training week.

    slots:
        Seven DraftTrainingSlot objects ordered by weekday.
    """

    start_date: date

    slots: tuple[DraftTrainingSlot, ...]

    # ======================================================

    def __post_init__(self) -> None:

        if not isinstance(self.start_date, date):

            raise TypeError(
                "start_date must be a date."
            )

        if self.start_date.weekday() != 0:

            raise ValueError(
                "start_date must be a Monday."
            )

        slots = tuple(self.slots)

        for slot in slots:

            if not isinstance(
                slot,
                DraftTrainingSlot,
            ):

                raise TypeError(
                    "slots must contain DraftTrainingSlot objects."
                )

        object.__setattr__(
            self,
            "slots",
            tuple(
                sorted(
                    slots,
                    key=lambda slot: slot.weekday.value,
                )
            ),
        )

    # ======================================================

    @property
    def end_date(self) -> date:

        return (
            self.start_date
            + timedelta(days=6)
        )

    # ======================================================

    @property
    def weekdays(self):

        return tuple(
            slot.weekday
            for slot in self.slots
        )

    # ======================================================

    def scheduled_date(
        self,
        slot: DraftTrainingSlot,
    ) -> date:
        """
        Returns the calendar date for a slot.
        """

        return (
            self.start_date
            + timedelta(days=slot.weekday.value)
        )

    # ======================================================

    def __len__(self) -> int:

        return len(self.slots)

    # ======================================================

    def __iter__(self):

        return iter(self.slots)

    # ======================================================

    def __repr__(self) -> str:

        return (
            "TrainingWeek("
            f"start_date={self.start_date.isoformat()}, "
            f"slots={len(self.slots)})"
        )