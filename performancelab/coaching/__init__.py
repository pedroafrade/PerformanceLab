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
from .availability import (
    AthleteAvailability,
    Weekday,
)
from .constraints import TrainingConstraints
from .preferences import AthletePreferences
from .review import (
    PlanReview,
    ReviewCategory,
    ReviewFinding,
    ReviewSeverity,
)

from .draft_slot import DraftTrainingSlot
from .reviewer import CoachReviewer
from .session_purpose import SessionPurpose
from .structure_generator import WeekStructureGenerator

__all__ = [
    # Existing coaching API
    "Coach",
    "CoachContext",
    "CoachAnalysis",
    "CoachAnalyzer",
    "CoachRecommendation",
    "CoachStrategy",
    "StrategyPlan",
    "StrategySelector",

    # Strategies
    "BaseStrategy",
    "BuildStrategy",
    "RegenerationStrategy",
    "TaperStrategy",

    # Athlete scheduling domain
    "Weekday",
    "AthleteAvailability",
    "AthletePreferences",
    "TrainingConstraints",

    # Plan review domain
    "PlanReview",
    "ReviewFinding",
    "ReviewSeverity",
    "ReviewCategory",

    # Generator
    "SessionPurpose",
    "DraftTrainingSlot",
    "WeekStructureGenerator",
    "CoachReviewer",
]