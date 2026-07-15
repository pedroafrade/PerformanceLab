"""
PerformanceLab

Public physiology package interface.
"""

from .cadence import (
    average as average_cadence,
    cadence_reserve,
    maximum as maximum_cadence,
    minimum as minimum_cadence,
    percent_maximum,
    recommended_cycling,
    recommended_running,
)

from .efficiency import (
    efficiency_factor,
    normalized_efficiency,
    power_per_heart_rate,
    speed_per_heart_rate,
    speed_per_watt,
    vertical_speed,
)

from .fatigue import (
    acute_chronic_ratio,
    fatigue_index,
    freshness_score,
    monotony,
    risk_score,
    strain,
)

from .heartrate import (
    average as average_heart_rate,
    heart_rate_reserve,
    karvonen,
    percent_hrr,
    percent_max_hr,
)

from .pace import (
    average as average_pace,
    duration,
    fastest,
    pace,
    pace_from_speed,
    slowest,
    speed,
    speed_from_pace,
)

from .power import (
    average as average_power,
    ftp_from_relative,
    minimum as minimum_power,
    peak,
    percent_ftp,
    relative_power,
)

from .recovery import (
    heart_rate_recovery,
    is_recovered,
    recovery_days,
    recovery_score,
    training_strain,
)

from .thresholds import (
    aerobic_threshold,
    anaerobic_threshold,
    lthr,
    threshold_pace,
    threshold_power,
    threshold_speed,
)

from .vo2max import (
    oxygen_cost,
    relative_intensity,
    running_economy,
    vdot,
    vo2_reserve,
    vo2max_from_cooper,
    vo2max_from_speed,
)

from .zones import (
    heart_rate_zones,
    pace_zones,
    power_zones,
    zone,
)


__all__ = [

    # Heart rate
    "heart_rate_reserve",
    "percent_max_hr",
    "percent_hrr",
    "karvonen",
    "average_heart_rate",

    # Power
    "relative_power",
    "percent_ftp",
    "ftp_from_relative",
    "average_power",
    "peak",
    "minimum_power",

    # Thresholds
    "lthr",
    "aerobic_threshold",
    "anaerobic_threshold",
    "threshold_speed",
    "threshold_pace",
    "threshold_power",

    # Zones
    "heart_rate_zones",
    "power_zones",
    "pace_zones",
    "zone",

    # Pace
    "speed",
    "pace",
    "duration",
    "pace_from_speed",
    "speed_from_pace",
    "fastest",
    "slowest",
    "average_pace",

    # Recovery
    "recovery_score",
    "recovery_days",
    "heart_rate_recovery",
    "is_recovered",
    "training_strain",

    # Cadence
    "average_cadence",
    "maximum_cadence",
    "minimum_cadence",
    "cadence_reserve",
    "percent_maximum",
    "recommended_running",
    "recommended_cycling",

    # VO2max
    "vo2max_from_cooper",
    "vo2max_from_speed",
    "oxygen_cost",
    "running_economy",
    "vdot",
    "relative_intensity",
    "vo2_reserve",

    # Efficiency
    "speed_per_heart_rate",
    "power_per_heart_rate",
    "speed_per_watt",
    "vertical_speed",
    "efficiency_factor",
    "normalized_efficiency",

    # Fatigue
    "acute_chronic_ratio",
    "monotony",
    "strain",
    "fatigue_index",
    "freshness_score",
    "risk_score",
]