"""
PerformanceLab

External service integrations.
"""

from .gemini_activity_coach import (
    GEMINI_ACTIVITY_COACH_MODEL,
    GeminiActivityCoachProvider,
)


__all__ = [
    "GEMINI_ACTIVITY_COACH_MODEL",
    "GeminiActivityCoachProvider",
]