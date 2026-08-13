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
class DevelopmentPaceZoneData:
    """
    One running pace training zone.
    """

    name: str
    faster_pace: float
    slower_pace: float


@dataclass(frozen=True)
class DevelopmentPerformanceReferencesData:
    """
    Stable physiological performance references.
    """

    pace_zones: tuple[
        DevelopmentPaceZoneData,
        ...,
    ]

    easy_pace: float | None
    tempo_pace: float | None
    lt2_pace: float | None

    threshold_hr: int | None
    ftp: float | None

@dataclass(frozen=True)
class DevelopmentTrendMetricData:
    """
    One historical development metric compared across
    two consecutive fixed-duration windows.
    """

    current_value: float | None
    previous_value: float | None

    absolute_change: float | None
    percentage_change: float | None

    current_samples: int
    previous_samples: int

    window_days: int = 28


@dataclass(frozen=True)
class DevelopmentTrendsData:
    """
    Historical volume trends prepared for presentation.
    """

    exercise_minutes_per_day: (
        DevelopmentTrendMetricData
    )

    exercise_distance_per_day: (
        DevelopmentTrendMetricData
    )

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
    recovery_balance: float
    recovery_status: str
    recovery_recommendation: str



    acute_load: float
    chronic_load: float
    ramp_rate: float

    load_status: str
    load_recommendation: str

    historical_trends: (
        DevelopmentTrendsData
        | None
    ) = None

    sport_volume: tuple[
        DevelopmentSportVolumeData,
        ...,
    ] = ()

    intensity: (
        DevelopmentIntensityData
        | None
    ) = None

    performance_references: (
        DevelopmentPerformanceReferencesData
        | None
    ) = None

    recovery_reference_time: (
        datetime | None
    ) = None
    hours_since_last_workout: (
        float | None
    ) = None
    recovery_is_time_aware: bool = False