"""
PerformanceLab

Development presentation models.
"""

from dataclasses import dataclass
from datetime import date, datetime

@dataclass(frozen=True)
class DevelopmentSportVolumeData:
    """
    Aggregated completed training volume for one sport.
    """

    sport: str
    duration_seconds: float
    distance: float
    sessions: int

@dataclass(frozen=True)
class DevelopmentData:
    """
    Presentation-ready view of the athlete's
    physiological and training development.
    """

    dates: tuple[
        date | datetime,
        ...,
    ]

    daily_load: tuple[float, ...]
    fitness: tuple[float, ...]
    fatigue: tuple[float, ...]
    form: tuple[float, ...]

    current_fitness: float
    current_fatigue: float
    current_form: float

    recovery_score: float
    recovery_status: str
    recovery_recommendation: str

    acute_load: float
    chronic_load: float
    ramp_rate: float

    load_status: str
    load_recommendation: str

    sport_volume: tuple[
        DevelopmentSportVolumeData,
        ...,
    ] = ()