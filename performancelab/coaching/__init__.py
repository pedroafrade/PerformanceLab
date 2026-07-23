"""
PerformanceLab

Coaching

Public interface for the athlete coaching engine.
"""

from .analyzer import CoachAnalysis, CoachAnalyzer
from .coach import Coach
from .context import CoachContext
from .recommendation import CoachRecommendation
from .strategy import CoachStrategy, StrategyPlan

from .strategies import (
    BaseStrategy,
    BuildStrategy,
    RegenerationStrategy,
    TaperStrategy,
)


__all__ = [
    "Coach",
    "CoachContext",
    "CoachAnalysis",
    "CoachAnalyzer",
    "CoachRecommendation",
    "CoachStrategy",
    "StrategyPlan",
    "BaseStrategy",
    "BuildStrategy",
    "RegenerationStrategy",
    "TaperStrategy",
]