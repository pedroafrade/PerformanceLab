"""
PerformanceLab

Coaching

Public interface for the athlete coaching engine.
"""

from .analyzer import CoachAnalysis, CoachAnalyzer
from .coach import Coach
from .context import CoachContext
from .recommendation import CoachRecommendation


__all__ = [
    "Coach",
    "CoachContext",
    "CoachAnalysis",
    "CoachAnalyzer",
    "CoachRecommendation",
]