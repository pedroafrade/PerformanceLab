"""
PerformanceLab

Streamlit UI components.
"""
from .activities_page import (
    show_activities_page,
)
from .alpha_participation_consent import (
    show_alpha_participation_consent_dialog,
)
from .calendar_page import (
    show_calendar_page,
)
from .plan_page import (
    show_plan_page,
)
from .activity_input import (
    show_activity_input,
)
from .athlete_panel import (
    show_athlete_panel,
)
from .dashboard import (
    show_dashboard,
    show_selected_workout_route,
)
from .development_page import (
    show_development_page,
)
from .elevation_profile import (
    show_elevation_profile,
)
from .import_panel import (
    show_import_panel,
)
from .route_map import (
    show_route_map,
)
from .sensor_card import (
    show_sensor_card,
)
from .sidebar import (
    show_sidebar,
)
from .settings_page import (
    show_settings_page,
)
from .storage_panel import (
    show_storage_panel,
)
from .today_page import (
    show_today_page,
)
from .training_coach_consent import (
    show_training_coach_consent_dialog,
    show_training_coach_consent_settings,
)
from .training_page import (
    show_training_page,
)
from .workout_details import (
    show_workout_details,
    show_workout_summary,
)
from .workout_editor import (
    show_workout_editor,
)
from .workout_table import (
    show_workout_table,
)


__all__ = [
    "show_activities_page",
    "show_alpha_participation_consent_dialog",
    "show_calendar_page",
    "show_activity_input",
    "show_athlete_panel",
    "show_dashboard",
    "show_development_page",
    "show_elevation_profile",
    "show_import_panel",
    "show_plan_page",
    "show_route_map",
    "show_selected_workout_route",
    "show_sensor_card",
    "show_settings_page",
    "show_sidebar",
    "show_storage_panel",
    "show_training_coach_consent_dialog",
    "show_training_coach_consent_settings",
    "show_today_page",
    "show_training_page",
    "show_workout_details",
    "show_workout_editor",
    "show_workout_summary",
    "show_workout_table",
]