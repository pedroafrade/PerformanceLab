"""
PerformanceLab

Presentation package.
"""
from .activity_models import (
    ActivityFilters,
    ActivityListItemData,
)
from .activities_presenter import (
    ActivitiesPresenter,
)
from .activity_coach_models import (
    ActivityCoachAssessmentData,
    ActivityCoachContextData,
    ActivityCoachEventData,
    ActivityCoachFeedbackData,
    ActivityCoachPhysiologyData,
    ActivityCoachPlanData,
    ActivityCoachRecentTrainingData,
    ActivityCoachSensorData,
)
from .activity_coach_presenter import (
    ActivityCoachPresenter,
)
from .activity_coach_prompt import (
    ACTIVITY_COACH_OUTPUT_SECTIONS,
    ACTIVITY_COACH_PROMPT_RULES,
    ACTIVITY_COACH_PROMPT_VERSION,
    build_activity_coach_prompt_payload,
)
from .development_models import (
    DevelopmentData,
    DevelopmentHeartRateZoneData,
    DevelopmentIntensityData,
    DevelopmentPaceZoneData,
    DevelopmentPerformanceReferencesData,
    DevelopmentSportVolumeData,
    DevelopmentSummaryCardData,
    DevelopmentTrendMetricData,
    DevelopmentTrendsData,
    DevelopmentVO2MaxObservationData,
)

from .development_presenter import (
    DevelopmentPresenter,
)
from .development_summary_presenter import (
    DevelopmentSummaryPresenter,
)
from .calendar_models import (
    CalendarDayData,
    CalendarItemData,
    CalendarMonthData,
    CalendarUpcomingEventData,
)
from .calendar_presenter import (
    CalendarPresenter,
)

from .plan_models import (
    CompletePlanData,
    PlanAdaptationData,
    PlanChartPointData,
    PlanCompletedLoadPointData,
    PlanCurrentPhaseData,
    PlanPhaseData,
    PlanProgressionPointData,
    PlanWeekData,
    PlanWorkoutData,
)
from .plan_presenter import (
    PlanPresenter,
)
from .today_models import (
    TodayAdaptationData,
    TodayData,
    TodayGuidanceData,
    TodayReadinessData,
    TodaySessionCardData,
)
from .today_presenter import (
    TodayPresenter,
)
from .card import (
    SensorCard,
    cadence_card,
    heart_rate_card,
    power_card,
    sensor_card,
)

from .chart import (
    cadence_series,
    cadence_summary,
    has_sensor_series,
    heart_rate_series,
    heart_rate_summary,
    power_series,
    power_summary,
    sensor_average,
    sensor_maximum,
    sensor_minimum,
    sensor_series,
    sensor_summary,
    sensor_values,
)

from .dashboard import DashboardData

from .elevation import (
    elevation_maximum,
    elevation_minimum,
    elevation_profile,
    elevation_profile_distance,
    elevation_range,
    elevation_values,
    has_elevation_profile,
)

from .route import (
    has_route,
    route_center,
    route_coordinates,
    route_points,
)


__all__ = [

    # Activities
    "ActivityFilters",
    "ActivityListItemData",
    "ActivitiesPresenter",
    "ActivityCoachAssessmentData",
    "ActivityCoachContextData",
    "ActivityCoachRecentTrainingData",
    "ActivityCoachSensorData",
    "ActivityCoachPresenter",
    "ActivityCoachEventData",
    "ActivityCoachPhysiologyData",
    "ActivityCoachPlanData",
    "ActivityCoachFeedbackData",
    "ACTIVITY_COACH_OUTPUT_SECTIONS",
    "ACTIVITY_COACH_PROMPT_RULES",
    "ACTIVITY_COACH_PROMPT_VERSION",
    "build_activity_coach_prompt_payload",

    # Calendar
    "CalendarDayData",
    "CalendarItemData",
    "CalendarMonthData",
    "CalendarPresenter",
    "CalendarUpcomingEventData",

    # Complete plan
    "CompletePlanData",
    "PlanAdaptationData",
    "PlanChartPointData",
    "PlanCompletedLoadPointData",
    "PlanCurrentPhaseData",
    "PlanProgressionPointData",
    "PlanPresenter",
    "PlanWeekData",
    "PlanWorkoutData",

    # Today
    "TodayAdaptationData",
    "TodayData",
    "TodayGuidanceData",
    "TodayPresenter",
    "TodayReadinessData",
    "TodaySessionCardData",


    # Development
    "DevelopmentData",
    "DevelopmentHeartRateZoneData",
    "DevelopmentIntensityData",
    "DevelopmentPaceZoneData",
    "DevelopmentPerformanceReferencesData",
    "DevelopmentPresenter",
    "DevelopmentSportVolumeData",
    "DevelopmentSummaryCardData",
    "DevelopmentSummaryPresenter",
    "DevelopmentTrendMetricData",
    "DevelopmentTrendsData",
    "DevelopmentVO2MaxObservationData",


    # Dashboard
    "DashboardData",

    # Route
    "has_route",
    "route_center",
    "route_coordinates",
    "route_points",

    # Elevation
    "elevation_profile",
    "elevation_values",
    "elevation_minimum",
    "elevation_maximum",
    "elevation_range",
    "elevation_profile_distance",
    "has_elevation_profile",

    # Generic chart data
    "sensor_series",
    "sensor_values",
    "sensor_average",
    "sensor_minimum",
    "sensor_maximum",
    "sensor_summary",
    "has_sensor_series",

    # Heart rate
    "heart_rate_series",
    "heart_rate_summary",

    # Power
    "power_series",
    "power_summary",

    # Cadence
    "cadence_series",
    "cadence_summary",

    # Sensor cards
    "SensorCard",
    "sensor_card",
    "heart_rate_card",
    "power_card",
    "cadence_card",

]