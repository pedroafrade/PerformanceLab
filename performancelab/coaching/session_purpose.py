"""
PerformanceLab

Session Purpose

Defines the high-level role of a session within a training
week.

A session purpose describes coaching intent. It does not
contain the detailed workout prescription.
"""

from enum import Enum


class SessionPurpose(str, Enum):
    """
    High-level purpose of a weekly training slot.
    """

    REST = "rest"

    RECOVERY = "recovery"

    EASY = "easy"

    INTENSITY = "intensity"

    LONG = "long"

    RACE = "race"

    CROSS_TRAINING = "cross_training"

    # ======================================================

    @property
    def is_training(self) -> bool:
        """
        Returns whether this purpose represents training.
        """

        return self is not SessionPurpose.REST

    # ======================================================

    @property
    def is_quality(self) -> bool:
        """
        Returns whether this purpose normally requires
        additional recovery.
        """

        return self in {
            SessionPurpose.INTENSITY,
            SessionPurpose.LONG,
            SessionPurpose.RACE,
        }

    # ======================================================

    @property
    def is_low_intensity(self) -> bool:
        """
        Returns whether this purpose represents a low
        intensity session.
        """

        return self in {
            SessionPurpose.RECOVERY,
            SessionPurpose.EASY,
        }