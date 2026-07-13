"""
PerformanceLab

AthleteFeedback

Subjective feedback reported by the athlete after a workout.
"""

from dataclasses import dataclass


@dataclass
class AthleteFeedback:

    # Perceived exertion (0-10 Borg CR10)
    rpe: float | None = None

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

    def __repr__(self):

        return (
            f"AthleteFeedback("
            f"rpe={self.rpe}, "
            f"feeling={self.feeling})"
        )