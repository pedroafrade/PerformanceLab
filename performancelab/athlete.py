"""
PerformanceLab

Athlete

Represents an athlete and all associated training data.
"""

from dataclasses import dataclass, field
from datetime import date
from uuid import uuid4


from .analysis import (
    AthleteAnalytics,
    HeartRateZone,
)
from .goals.goalbook import GoalBook
from .history import History
from .race.eventbook import EventBook
from .training.config import (
    AthleteAvailability,
    AthletePreferences,
    TrainingConstraints,
)
from .training.planning import TrainingPlan


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

    manual_heart_rate_zones: tuple[
        HeartRateZone,
        ...,
    ] = ()
    train_any_day: bool = True

    history: History = field(default_factory=History)
    training_plan: TrainingPlan = field(default_factory=TrainingPlan)

    availability: AthleteAvailability = field(
        default_factory=AthleteAvailability,
    )
    preferences: AthletePreferences = field(
        default_factory=AthletePreferences,
    )
    training_constraints: TrainingConstraints = field(
        default_factory=TrainingConstraints,
    )

    goals: GoalBook = field(default_factory=GoalBook)
    events: EventBook = field(default_factory=EventBook)

    analytics: AthleteAnalytics = field(init=False, repr=False)

    def __post_init__(self) -> None:

        self.analytics = AthleteAnalytics(
            self
        )

        self.history.on_change = (
            self.analytics
            .invalidate_training_state
        )

    def __repr__(self) -> str:
        return (
            "Athlete("
            f"name={self.name!r}, "
            f"workouts={len(self.history)}, "
            f"goals={len(self.goals)}, "
            f"plan={len(self.training_plan)}, "
            f"events={len(self.events)})"
        )