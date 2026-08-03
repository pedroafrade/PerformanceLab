"""
PerformanceLab

Streamlit UI components.
"""
from .activities_page import (
    show_activities_page,
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
from .storage_panel import (
    show_storage_panel,
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
    "show_calendar_page",
    "show_activity_input",
    "show_athlete_panel",
    "show_dashboard",
    "show_elevation_profile",
    "show_import_panel",
    "show_plan_page",
    "show_route_map",
    "show_selected_workout_route",
    "show_sensor_card",
    "show_sidebar",
    "show_storage_panel",
    "show_training_page",
    "show_workout_details",
    "show_workout_editor",
    "show_workout_summary",
    "show_workout_table",
]