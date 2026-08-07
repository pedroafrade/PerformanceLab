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
class DevelopmentHeartRateZoneData:
    """
    Aggregated time in one heart-rate zone.
    """

    name: str
    lower_bpm: int
    upper_bpm: int
    duration_seconds: float
    percentage: float


@dataclass(frozen=True)
class DevelopmentIntensityData:
    """
    Objective heart-rate intensity and subjective RPE.
    """

    zones: tuple[
        DevelopmentHeartRateZoneData,
        ...,
    ]

    zone_source: str | None
    heart_rate_seconds: float

    average_rpe: float | None
    sessions_with_rpe: int
    high_rpe_sessions: int

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

    intensity: (
        DevelopmentIntensityData
        | None
    ) = None