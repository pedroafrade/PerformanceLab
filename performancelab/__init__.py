"""
PerformanceLab

Public package interface.
"""

from .athlete import Athlete
from .activity_coach_records import (
    ActivityCoachInterpretation,
    ActivityCoachInterpretationBook,
    activity_coach_context_hash,
)
from .vo2max_observations import (
    VO2MaxObservation,
    VO2MaxObservationBook,
    parse_vo2max_observation,
    synchronize_vo2max_observation_from_notes,
)
from .workout import Workout

from .history import History

from .goals import (
    Goal,
    GoalBook,
)

from .race import (
    Event,
    EventBook,
    EventEntry,
)

from .builders import (
    create_workout,
)

__all__ = [
    "Athlete",
    "ActivityCoachInterpretation",
    "ActivityCoachInterpretationBook",
    "activity_coach_context_hash",
    "VO2MaxObservation",
    "VO2MaxObservationBook",
    "parse_vo2max_observation",
    "synchronize_vo2max_observation_from_notes",
    "Workout",
    "History",
    "Goal",
    "GoalBook",
    "Event",
    "EventEntry",
    "EventBook",
    "create_workout",
]