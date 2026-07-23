"""
PerformanceLab

Coaching

Public interface for the athlete coaching engine.
"""

from .analyzer import CoachAnalysis, CoachAnalyzer
from .context import CoachContext
from .recommendation import CoachRecommendation
from .strategy import CoachStrategy, StrategyPlan

from .strategies import (
    BaseStrategy,
    BuildStrategy,
    RegenerationStrategy,
    TaperStrategy,
)
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
from .workout_template import WorkoutTemplate
from .workout_templates import (
    CROSS_TRAINING_TEMPLATE,
    DEFAULT_WORKOUT_TEMPLATES,
    EASY_TEMPLATE,
    INTENSITY_TEMPLATE,
    LONG_TEMPLATE,
    RACE_TEMPLATE,
    RECOVERY_TEMPLATE,
    REST_TEMPLATE,
    template_for,
)
from .workout_generator import WorkoutGenerator
from .training_week import TrainingWeek

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

    # Workout templates
    "WorkoutTemplate",
    "DEFAULT_WORKOUT_TEMPLATES",
    "REST_TEMPLATE",
    "RECOVERY_TEMPLATE",
    "EASY_TEMPLATE",
    "INTENSITY_TEMPLATE",
    "LONG_TEMPLATE",
    "RACE_TEMPLATE",
    "template_for",
    "CROSS_TRAINING_TEMPLATE",

    "WorkoutGenerator",
    "TrainingWeek",
]
def __getattr__(name: str):

    if name == "Coach":
        from .coach import Coach

        return Coach

    raise AttributeError(
        f"module {__name__!r} has no attribute {name!r}"
    )