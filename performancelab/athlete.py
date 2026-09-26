"""
PerformanceLab

Athlete

Represents an athlete and all associated training data.
"""

from dataclasses import dataclass, field
from datetime import date
from uuid import uuid4

from .activity_coach_records import (
    ActivityCoachInterpretationBook,
)
from .analysis import (
    AthleteAnalytics,
    HeartRateZone,
    NutritionProfile,
)
from .goals.goalbook import GoalBook
from .history import History
from .race.eventbook import EventBook
from .recovery_log import RecoveryLogEntry
from .training.config import (
    AthleteAvailability,
    AthletePreferences,
    TrainingConstraints,
)
from .training.planning import TrainingPlan
from .vo2max_observations import (
    VO2MaxObservationBook,
)


@dataclass
class Athlete:
    athlete_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    name: str = ""
    birth_date: date | None = None
    gender: str = ""
    height: float | None = None
    weight: float | None = None
    ftp: float | None = None
    max_hr: int | None = None
    resting_hr: int | None = None
    threshold_hr: int | None = None

    onboarding_completed: bool | None = None
    onboarding_step: int = 1

    manual_heart_rate_zones: tuple[
        HeartRateZone,
        ...,
    ] = ()

    nutrition_profile: NutritionProfile = field(
        default_factory=NutritionProfile,
    )

    train_any_day: bool = True

    history: History = field(
        default_factory=History
    )
    training_plan: TrainingPlan = field(
        default_factory=TrainingPlan
    )
    activity_coach_interpretations: (
        ActivityCoachInterpretationBook
    ) = field(
        default_factory=(
            ActivityCoachInterpretationBook
        )
    )
    vo2max_observations: (
        VO2MaxObservationBook
    ) = field(
        default_factory=VO2MaxObservationBook
    )

    availability: AthleteAvailability = field(
        default_factory=AthleteAvailability,
    )
    preferences: AthletePreferences = field(
        default_factory=AthletePreferences,
    )
    training_constraints: TrainingConstraints = field(
        default_factory=TrainingConstraints,
    )

    goals: GoalBook = field(
        default_factory=GoalBook
    )
    events: EventBook = field(
        default_factory=EventBook
    )
    recovery_log: list[RecoveryLogEntry] = field(default_factory=list)

    analytics: AthleteAnalytics = field(
        init=False,
        repr=False,
    )

    def __post_init__(
        self,
    ) -> None:

        if self.onboarding_completed not in (None, False, True):
            raise TypeError(
                "onboarding_completed must be a boolean or None."
            )

        if (
            not isinstance(self.onboarding_step, int)
            or isinstance(self.onboarding_step, bool)
            or self.onboarding_step not in range(1, 6)
        ):
            raise ValueError(
                "onboarding_step must be between 1 and 5."
            )

        self.analytics = AthleteAnalytics(
            self
        )

        self.history.on_change = (
            self.analytics
            .invalidate_training_state
        )

    def __repr__(
        self,
    ) -> str:

        return (
            "Athlete("
            f"name={self.name!r}, "
            f"workouts={len(self.history)}, "
            f"goals={len(self.goals)}, "
            f"plan={len(self.training_plan)}, "
            f"events={len(self.events)})"
        )
