"""
Shared fixtures for coaching tests.
"""

import pytest

from performancelab.coaching.availability import (
    AthleteAvailability,
)
from performancelab.coaching.constraints import (
    TrainingConstraints,
)
from performancelab.coaching.preferences import (
    AthletePreferences,
)
from performancelab.coaching.strategy import StrategyPlan


@pytest.fixture
def strategy_plan() -> StrategyPlan:
    """
    Creates a StrategyPlan instance without depending on its
    current constructor fields.

    The structure generator and reviewer currently validate
    only that the value is a StrategyPlan instance.
    """

    return object.__new__(StrategyPlan)


@pytest.fixture
def full_availability() -> AthleteAvailability:
    """
    Athlete available for enough time to support all common
    test sessions, including a 90-minute weekend long
    session.
    """

    return AthleteAvailability.from_minutes(
        monday=60,
        tuesday=60,
        wednesday=60,
        thursday=60,
        friday=60,
        saturday=120,
        sunday=120,
    )


@pytest.fixture
def default_preferences() -> AthletePreferences:
    """
    Preferences with no special weekday requests.
    """

    return AthletePreferences()


@pytest.fixture
def default_constraints() -> TrainingConstraints:
    """
    Permissive constraints suitable for most tests.
    """

    return TrainingConstraints(
        max_weekly_minutes=420,
        max_session_minutes=120,
        max_weekday_minutes=90,
        max_weekend_minutes=120,
        max_consecutive_training_days=7,
        max_intensity_sessions=2,
        max_long_sessions=1,
        max_sessions_per_day=1,
        minimum_recovery_days=0,
        allow_double_sessions=False,
    )