"""
PerformanceLab

Physiology
"""

from .heartrate import *
from .power import *
from .thresholds import *
from .zones import *
from .pace import *
from .recovery import *
from .cadence import *
from .vo2max import *
from .efficiency import *
from .fatigue import *

__all__ = [

    # Heart rate
    "heart_rate_reserve",
    "percent_max_hr",
    "percent_hrr",
    "karvonen",

    # Power
    "relative_power",
    "percent_ftp",
    "ftp_from_relative",
    "peak",
    "minimum",

    # Common
    "average",

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

    # Recovery
    "recovery_score",
    "recovery_days",
    "heart_rate_recovery",
    "is_recovered",
    "training_strain",

    # Cadence
    "maximum",
    "minimum",
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