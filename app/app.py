"""
PerformanceLab

Streamlit demonstration application.
"""

from datetime import date, timedelta

import pandas as pd
import streamlit as st

from performancelab import Athlete, Workout
from performancelab.presentation import DashboardData


# ======================================================
# Page configuration
# ======================================================

st.set_page_config(
    page_title="PerformanceLab",
    page_icon="📈",
    layout="wide",
)


# ======================================================
# Demo data
# ======================================================

def create_workout(
    sport,
    workout_date,
    distance,
    duration,
    elevation,
    rpe,
):

    workout = Workout()

    workout.info.sport = sport
    workout.info.date = workout_date
    workout.info.distance = distance
    workout.info.duration = duration
    workout.info.elevation_gain = elevation

    workout.feedback.rpe = rpe

    return workout


# ======================================================

def create_demo_athlete():

    athlete = Athlete(

        name="Pedro",

        weight=70,

        ftp=280,

        max_hr=190,

        resting_hr=50,

    )

    workouts = [

        create_workout(
            "Running",
            date.today() - timedelta(days=13),
            8,
            timedelta(minutes=45),
            120,
            5,
        ),

        create_workout(
            "Cycling",
            date.today() - timedelta(days=11),
            42,
            timedelta(hours=1, minutes=30),
            450,
            6,
        ),

        create_workout(
            "Running",
            date.today() - timedelta(days=9),
            12,
            timedelta(hours=1, minutes=5),
            210,
            7,
        ),

        create_workout(
            "Swimming",
            date.today() - timedelta(days=7),
            2.5,
            timedelta(minutes=50),
            0,
            5,
        ),

        create_workout(
            "Cycling",
            date.today() - timedelta(days=5),
            55,
            timedelta(hours=2),
            700,
            7,
        ),

        create_workout(
            "Running",
            date.today() - timedelta(days=3),
            10,
            timedelta(minutes=52),
            160,
            6,
        ),

        create_workout(
            "Running",
            date.today(),
            16,
            timedelta(hours=1, minutes=25),
            320,
            8,
        ),

    ]

    for workout in workouts:

        athlete.history.add(workout)

    return athlete


# ======================================================
# Formatting helpers
# ======================================================

def format_duration(value):

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
# Application data
# ======================================================

athlete = create_demo_athlete()

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

st.subheader(
    dashboard["athlete"]["name"]
)

sports = dashboard["athlete"]["sports"]

if sports:

    st.write(
        "Sports:",
        ", ".join(sports),
    )

else:

    st.write("Sports: —")


# ======================================================
# Summary metrics
# ======================================================

st.divider()

st.subheader("Training summary")

column_1, column_2, column_3, column_4 = st.columns(4)

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
        summary["total_duration"],
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
# Performance metrics
# ======================================================

st.divider()

st.subheader("Performance management")

column_1, column_2, column_3 = st.columns(3)

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
            performance["dates"],
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
        "There is not enough training data "
        "to display the performance chart."
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
            next_goal.name or "Unnamed goal"
        )

        st.write(
            f"{planning['days_until_next_goal']} days remaining"
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
            f"{planning['days_until_next_event']} days remaining"
        )


# ======================================================
# Workout history
# ======================================================

st.divider()

st.subheader("Workout history")

workout_rows = []

for workout in athlete.history:

    workout_rows.append(

        {
            "Date": workout.date,
            "Sport": workout.sport or "Unknown",
            "Distance": workout.distance,
            "Duration": format_duration(
                workout.duration
            ),
            "Elevation": workout.elevation_gain,
            "RPE": workout.feedback.rpe,
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