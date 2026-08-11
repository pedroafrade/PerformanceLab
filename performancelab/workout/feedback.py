"""
PerformanceLab

AthleteFeedback

Subjective feedback reported by the athlete after a workout.
"""

from dataclasses import dataclass


@dataclass
class AthleteFeedback:

    # Athlete-confirmed perceived exertion (0-10 Borg CR10)
    rpe: float | None = None

    # Automatically estimated exertion (0-10)
    estimated_rpe: float | None = None

    # General feeling (0-10)
    feeling: float | None = None

    # Sleep quality (0-10)
    sleep_quality: float | None = None

    # Motivation before the workout (0-10)
    motivation: float | None = None

    # Perceived stress (0-10)
    stress: float | None = None

    # Muscle soreness (0-10)
    muscle_soreness: float | None = None

    # Free text
    notes: str = ""

    # ======================================================
    def record_notes(
        self,
        notes: str | None,
    ) -> bool:
        """
        Records normalized subjective notes from the athlete.

        Returns True only when the persisted value changes.
        """

        normalized_notes = (
            str(
                notes or ""
            ).strip()
        )

        if normalized_notes == self.notes:
            return False

        self.notes = normalized_notes

        return True

    # ======================================================

    @property
    def effective_rpe(self) -> float | None:
        """
        Returns manual RPE when available, otherwise the estimate.
        """

        if self.rpe is not None:
            return self.rpe

        return self.estimated_rpe

    # ======================================================

    def __repr__(self):

        return (
            f"AthleteFeedback("
            f"rpe={self.rpe}, "
            f"feeling={self.feeling})"
        )