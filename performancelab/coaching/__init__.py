"""
PerformanceLab

Coaching

Public interface for the athlete coaching engine.
"""

from .analyzer import CoachAnalysis, CoachAnalyzer
from .context import CoachContext
from .heart_rate_target import (
    HeartRateTarget,
    heart_rate_target_for,
)
from .recommendation import CoachRecommendation
from .race_execution import (
    RaceExecutionPlan,
    build_race_execution_plan,
)
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
from .daily_guidance import (
    DailyTrainingGuidance,
    build_daily_training_guidance,
)
from .reviewer import CoachReviewer
from .session_purpose import SessionPurpose
from .stimulus_dose import StimulusDose
from .structure_generator import WeekStructureGenerator
from .workout_template import WorkoutTemplate
from .workout_templates import (
    CROSS_TRAINING_TEMPLATE,
    DEFAULT_WORKOUT_TEMPLATES,
    EASY_TEMPLATE,
    TECHNIQUE_TEMPLATE,
    PRE_RACE_TEMPLATE,
    SHAKEOUT_TEMPLATE,
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
    "HeartRateTarget",
    "heart_rate_target_for",
    "CoachAnalysis",
    "CoachAnalyzer",
    "CoachRecommendation",
    "RaceExecutionPlan",
    "build_race_execution_plan",
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
    "DailyTrainingGuidance",
    "build_daily_training_guidance",
    "WeekStructureGenerator",
    "CoachReviewer",

    # Workout templates
    "StimulusDose",
    "WorkoutTemplate",
    "DEFAULT_WORKOUT_TEMPLATES",
    "REST_TEMPLATE",
    "RECOVERY_TEMPLATE",
    "EASY_TEMPLATE",
    "TECHNIQUE_TEMPLATE",
    "PRE_RACE_TEMPLATE",
    "SHAKEOUT_TEMPLATE",
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