"""
PerformanceLab

Streamlit application with manual workout entry
and session-based athlete state.
"""

from datetime import date, timedelta
from datetime import datetime

import pandas as pd
import streamlit as st
import pydeck as pdk

from performancelab import Athlete, Workout
from performancelab.presentation import (
    DashboardData,
    has_route,
    route_center,
    route_coordinates,
)
from performancelab.importers import GPXImporter


# ======================================================
# Page configuration
# ======================================================

st.set_page_config(
    page_title="PerformanceLab",
    page_icon="📈",
    layout="wide",
)


# ======================================================
# Formatting helpers
# ======================================================

def format_workout_date(value):

    if value is None:

        return "—"

    if isinstance(value, datetime):

        return value.strftime(
            "%Y-%m-%d %H:%M"
        )

    return value.strftime(
        "%Y-%m-%d"
    )

def format_duration(value: timedelta | None) -> str:

    if value is None:

        return "—"

    total_seconds = int(value.total_seconds())

    hours, remainder = divmod(
        total_seconds,
        3600,
    )

    minutes = remainder // 60

    return f"{hours}h {minutes:02d}m"


# ======================================================

def format_distance(value: float | None) -> str:

    if value is None:

        return "—"

    return f"{value:.2f} km"


# ======================================================

def format_elevation(value: float | None) -> str:

    if value is None:

        return "—"

    return f"{value:.0f} m"


# ======================================================
# Workout creation
# ======================================================

def create_workout(
    sport: str,
    workout_date: date,
    distance: float | None,
    duration: timedelta,
    elevation_gain: float | None,
    rpe: float | None,
    title: str = "",
    description: str = "",
) -> Workout:

    workout = Workout()

    workout.info.sport = sport
    workout.info.date = workout_date
    workout.info.distance = distance
    workout.info.duration = duration
    workout.info.elevation_gain = elevation_gain
    workout.info.title = title
    workout.info.description = description
    workout.info.source = "manual"

    workout.feedback.rpe = rpe

    return workout


# ======================================================
# Demonstration athlete
# ======================================================

def create_demo_athlete() -> Athlete:

    athlete = Athlete(
        name="Pedro",
        weight=70,
        ftp=280,
        max_hr=190,
        resting_hr=50,
    )

    demo_workouts = [

        create_workout(
            sport="Running",
            workout_date=date.today() - timedelta(days=13),
            distance=8,
            duration=timedelta(minutes=45),
            elevation_gain=120,
            rpe=5,
            title="Easy Run",
        ),

        create_workout(
            sport="Cycling",
            workout_date=date.today() - timedelta(days=11),
            distance=42,
            duration=timedelta(
                hours=1,
                minutes=30,
            ),
            elevation_gain=450,
            rpe=6,
            title="Endurance Ride",
        ),

        create_workout(
            sport="Running",
            workout_date=date.today() - timedelta(days=9),
            distance=12,
            duration=timedelta(
                hours=1,
                minutes=5,
            ),
            elevation_gain=210,
            rpe=7,
            title="Tempo Run",
        ),

        create_workout(
            sport="Swimming",
            workout_date=date.today() - timedelta(days=7),
            distance=2.5,
            duration=timedelta(minutes=50),
            elevation_gain=0,
            rpe=5,
            title="Pool Session",
        ),

        create_workout(
            sport="Cycling",
            workout_date=date.today() - timedelta(days=5),
            distance=55,
            duration=timedelta(hours=2),
            elevation_gain=700,
            rpe=7,
            title="Long Ride",
        ),

        create_workout(
            sport="Running",
            workout_date=date.today() - timedelta(days=3),
            distance=10,
            duration=timedelta(minutes=52),
            elevation_gain=160,
            rpe=6,
            title="Steady Run",
        ),

        create_workout(
            sport="Running",
            workout_date=date.today(),
            distance=16,
            duration=timedelta(
                hours=1,
                minutes=25,
            ),
            elevation_gain=320,
            rpe=8,
            title="Long Run",
        ),

    ]

    for workout in demo_workouts:

        athlete.history.add(workout)

    return athlete

# ======================================================
# Route map
# ======================================================

def show_route_map(
    workout: Workout,
) -> None:

    if not has_route(workout):

        st.info(
            "This workout does not contain "
            "GPS route data."
        )

        return

    coordinates = route_coordinates(
        workout
    )

    center = route_center(workout)

    if center is None:

        return

    latitude, longitude = center

    route_data = [

        {
            "path": coordinates,
        }

    ]

    route_layer = pdk.Layer(

        "PathLayer",

        data=route_data,

        get_path="path",

        get_width=5,

        width_min_pixels=3,

        pickable=True,

    )

    start_finish_layer = pdk.Layer(

        "ScatterplotLayer",

        data=[
            {
                "position": coordinates[0],
                "label": "Start",
            },
            {
                "position": coordinates[-1],
                "label": "Finish",
            },
        ],

        get_position="position",

        get_radius=20,

        radius_min_pixels=6,

        pickable=True,

    )

    view_state = pdk.ViewState(

        latitude=latitude,

        longitude=longitude,

        zoom=13,

        pitch=0,

    )

    deck = pdk.Deck(

        layers=[
            route_layer,
            start_finish_layer,
        ],

        initial_view_state=view_state,

        tooltip={
            "text": "{label}",
        },

    )

    st.pydeck_chart(
        deck,
        width="stretch",
        height=500,
    )
# ======================================================
# Session state initialization
# ======================================================

def initialize_session_state() -> None:

    if "athlete" not in st.session_state:

        st.session_state.athlete = (
            create_demo_athlete()
        )

    if "notice" not in st.session_state:

        st.session_state.notice = None


# ======================================================
# Session actions
# ======================================================

def reset_demo_data() -> None:

    st.session_state.athlete = (
        create_demo_athlete()
    )

    st.session_state.notice = (
        "Demonstration data restored."
    )


# ======================================================

def clear_training_data() -> None:

    athlete = st.session_state.athlete

    athlete.history.clear()

    st.session_state.notice = (
        "Workout history cleared."
    )


# ======================================================
# Initialize state
# ======================================================

initialize_session_state()

athlete: Athlete = st.session_state.athlete


# ======================================================
# Sidebar — athlete
# ======================================================

with st.sidebar:

    st.header("Athlete")

    athlete.name = st.text_input(
        "Name",
        value=athlete.name,
    )

    athlete.weight = st.number_input(
        "Weight (kg)",
        min_value=0.0,
        value=float(
            athlete.weight or 0.0
        ),
        step=0.1,
    ) or None

    athlete.ftp = st.number_input(
        "FTP (W)",
        min_value=0.0,
        value=float(
            athlete.ftp or 0.0
        ),
        step=1.0,
    ) or None

    athlete.max_hr = int(
        st.number_input(
            "Maximum heart rate",
            min_value=0,
            value=int(
                athlete.max_hr or 0
            ),
            step=1,
        )
    ) or None

    athlete.resting_hr = int(
        st.number_input(
            "Resting heart rate",
            min_value=0,
            value=int(
                athlete.resting_hr or 0
            ),
            step=1,
        )
    ) or None

    st.divider()


# ======================================================
# Sidebar — add workout
# ======================================================

with st.sidebar:

    st.header("Add workout")

    with st.form(
        "manual_workout_form",
        clear_on_submit=True,
    ):

        title = st.text_input(
            "Title",
            placeholder="Morning run",
        )

        sport = st.selectbox(
            "Sport",
            options=[
                "Running",
                "Cycling",
                "Swimming",
                "Walking",
                "Hiking",
                "Strength",
                "Other",
            ],
        )

        workout_date = st.date_input(
            "Date",
            value=date.today(),
        )

        distance_value = st.number_input(
            "Distance (km)",
            min_value=0.0,
            value=0.0,
            step=0.1,
        )

        duration_column_1, duration_column_2 = (
            st.columns(2)
        )

        with duration_column_1:

            duration_hours = st.number_input(
                "Hours",
                min_value=0,
                value=0,
                step=1,
            )

        with duration_column_2:

            duration_minutes = st.number_input(
                "Minutes",
                min_value=0,
                max_value=59,
                value=30,
                step=1,
            )

        elevation_value = st.number_input(
            "Elevation gain (m)",
            min_value=0.0,
            value=0.0,
            step=10.0,
        )

        rpe_value = st.slider(
            "RPE",
            min_value=0,
            max_value=10,
            value=5,
            step=1,
        )

        description = st.text_area(
            "Description",
            placeholder="Workout notes...",
        )

        submitted = st.form_submit_button(
            "Add workout",
            type="primary",
            use_container_width=True,
        )

        if submitted:

            elapsed = timedelta(
                hours=int(duration_hours),
                minutes=int(duration_minutes),
            )

            if elapsed.total_seconds() <= 0:

                st.error(
                    "Duration must be greater "
                    "than zero."
                )

            else:

                workout = create_workout(
                    sport=sport,
                    workout_date=workout_date,
                    distance=(
                        float(distance_value)
                        if distance_value > 0
                        else None
                    ),
                    duration=elapsed,
                    elevation_gain=(
                        float(elevation_value)
                        if elevation_value > 0
                        else 0.0
                    ),
                    rpe=float(rpe_value),
                    title=title.strip(),
                    description=description.strip(),
                )

                athlete.history.add(workout)

                st.session_state.notice = (
                    "Workout added successfully."
                )

# ======================================================
# Sidebar — GPX Import
# ======================================================

with st.sidebar:

    st.divider()

    st.header("Import GPX")

    uploaded_gpx = st.file_uploader(

        "GPX file",

        type=["gpx"],

        accept_multiple_files=False,

    )

    if st.button(

        "Import GPX",

        use_container_width=True,

    ):

        if uploaded_gpx is None:

            st.warning(

                "Please choose a GPX file."

            )

        else:

            try:

                importer = GPXImporter()

                workout = importer.read(

                    uploaded_gpx

                )

                st.write("Imported sensors:")
                st.write(workout.sensors.__dict__)

                athlete.history.add(

                    workout

                )

                st.success(

                    "Workout imported successfully."

                )

                st.rerun()

            except Exception as error:

                st.error(

                    str(error)

                )
# ======================================================
# Sidebar — data controls
# ======================================================

with st.sidebar:

    st.divider()

    st.subheader("Session data")

    control_column_1, control_column_2 = (
        st.columns(2)
    )

    control_column_1.button(
        "Reset demo",
        on_click=reset_demo_data,
        use_container_width=True,
    )

    control_column_2.button(
        "Clear",
        on_click=clear_training_data,
        use_container_width=True,
    )

    st.caption(
        "The current version stores data only "
        "during this browser session."
    )


# ======================================================
# Dashboard data
# ======================================================

dashboard = DashboardData(
    athlete,
).build()

summary = dashboard["summary"]
performance = dashboard["performance"]
planning = dashboard["planning"]


# ======================================================
# Header
# ======================================================

st.title("PerformanceLab")

st.caption(
    "Training, physiology and performance analytics."
)

if st.session_state.notice:

    st.success(
        st.session_state.notice
    )

    st.session_state.notice = None

st.subheader(
    dashboard["athlete"]["name"]
    or "Unnamed athlete"
)

sports = dashboard["athlete"]["sports"]

if sports:

    st.write(
        "**Sports:**",
        ", ".join(sports),
    )

else:

    st.write("**Sports:** —")


# ======================================================
# Training summary
# ======================================================

st.divider()

st.subheader("Training summary")

column_1, column_2, column_3, column_4 = (
    st.columns(4)
)

column_1.metric(
    "Workouts",
    summary["workouts"],
)

column_2.metric(
    "Training days",
    summary["training_days"],
)

column_3.metric(
    "Total duration",
    format_duration(
        summary["total_duration"]
    ),
)

average_rpe = summary["average_rpe"]

column_4.metric(
    "Average RPE",
    (
        f"{average_rpe:.1f}"
        if average_rpe is not None
        else "—"
    ),
)


# ======================================================
# Performance management
# ======================================================

st.divider()

st.subheader("Performance management")

column_1, column_2, column_3 = (
    st.columns(3)
)

column_1.metric(
    "CTL — Fitness",
    f"{summary['ctl']:.1f}",
)

column_2.metric(
    "ATL — Fatigue",
    f"{summary['atl']:.1f}",
)

column_3.metric(
    "TSB — Form",
    f"{summary['tsb']:.1f}",
)


# ======================================================
# Performance chart
# ======================================================

if performance["dates"]:

    chart_data = pd.DataFrame(

        {
            "Load": performance["load"],
            "CTL": performance["ctl"],
            "ATL": performance["atl"],
            "TSB": performance["tsb"],
        },

        index=pd.to_datetime(
            performance["dates"]
        ),

    )

    chart_data.index.name = "Date"

    st.line_chart(
        chart_data,
    )

    with st.expander(
        "Show performance data"
    ):

        st.dataframe(
            chart_data,
            width="stretch",
        )

else:

    st.info(
        "Add a workout to display "
        "performance data."
    )


# ======================================================
# Planning
# ======================================================

st.divider()

st.subheader("Planning")

column_1, column_2 = st.columns(2)

next_goal = planning["next_goal"]

with column_1:

    st.markdown("#### Next goal")

    if next_goal is None:

        st.write("No active goals.")

    else:

        st.write(
            next_goal.name
            or "Unnamed goal"
        )

        st.write(
            f"{planning['days_until_next_goal']} "
            "days remaining"
        )

next_event = planning["next_event"]

with column_2:

    st.markdown("#### Next event")

    if next_event is None:

        st.write("No upcoming events.")

    else:

        st.write(
            next_event.event.name
            or "Unnamed event"
        )

        st.write(
            f"{planning['days_until_next_event']} "
            "days remaining"
        )


# ======================================================
# Workout history
# ======================================================

st.divider()

st.subheader("Workout history")

workout_rows = []

for workout in reversed(
    athlete.history.workouts
):

    workout_rows.append(

        {
            "Date": format_workout_date(
                workout.date
            ),
            "Title": (
                workout.info.title
                or "—"
            ),
            "Sport": (
                workout.sport
                or "Unknown"
            ),
            "Distance": format_distance(
                workout.distance
            ),
            "Duration": format_duration(
                workout.duration
            ),
            "Elevation": format_elevation(
                workout.elevation_gain
            ),
            "RPE": workout.feedback.rpe,
            "Source": (
                workout.info.source
                or "—"
            ),
        }

    )

if workout_rows:

    workout_table = pd.DataFrame(
        workout_rows
    )

    st.dataframe(
        workout_table,
        width="stretch",
        hide_index=True,
    )

else:

    st.info(
        "No workouts available."
    )

# ======================================================
# Workout details
# ======================================================

st.divider()

st.subheader("Workout details")

workouts = list(

    reversed(
        athlete.history.workouts
    )

)

if workouts:

    selected_index = st.selectbox(

        "Select workout",

        options=range(len(workouts)),

        format_func=lambda index: (

            f"{workouts[index].date} — "
            f"{workouts[index].sport or 'Unknown'} — "
            f"{workouts[index].info.title or 'Untitled'} — "
            f"{workouts[index].info.source or 'unknown'}"
        ),

    )

    selected_workout = workouts[
        selected_index
    ]

    st.write("Sensors:")
    st.write(selected_workout.sensors)

    st.write("Sensors dict:")
    st.write(vars(selected_workout.sensors))

    detail_column_1, detail_column_2, \
        detail_column_3, detail_column_4 = (
            st.columns(4)
        )
    

    detail_column_1.metric(

        "Distance",

        format_distance(
            selected_workout.distance
        ),

    )

    detail_column_2.metric(

        "Duration",

        format_duration(
            selected_workout.duration
        ),

    )

    detail_column_3.metric(

        "Elevation",

        format_elevation(
            selected_workout.elevation_gain
        ),

    )

    detail_column_4.metric(

        "RPE",

        (
            f"{selected_workout.feedback.rpe:.1f}"
            if selected_workout.feedback.rpe
            is not None
            else "—"
        ),

    )

    st.markdown("#### Route")

    show_route_map(
        selected_workout
    )

else:

    st.info(
        "No workout is available "
        "for inspection."
    )