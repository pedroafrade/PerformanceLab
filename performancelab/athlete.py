"""
PerformanceLab

Athlete

Represents an athlete and all associated training data.
"""

from dataclasses import dataclass, field

from .history import History
from .goals.goalbook import GoalBook
from .race.eventbook import EventBook
from .analysis import AthleteAnalytics


@dataclass
class Athlete:

    name: str = ""

    birth_date: object | None = None

    sex: str = ""

    height: float | None = None

    weight: float | None = None

    ftp: float | None = None

    max_hr: int | None = None

    resting_hr: int | None = None

    history: History = field(default_factory=History)

    goals: GoalBook = field(default_factory=GoalBook)

    calendar: EventBook = field(default_factory=EventBook)

    analytics: AthleteAnalytics = field(init=False)

    # ======================================================

    def __post_init__(self):

        self.analytics = AthleteAnalytics(self)

    # ======================================================

    def __repr__(self):

        return (

            f"Athlete("

            f"name='{self.name}', "

            f"workouts={len(self.history)}, "

            f"goals={len(self.goals)}, "

            f"calendar={len(self.calendar)})"

        )