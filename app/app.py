"""
PerformanceLab

Streamlit application.
"""

from datetime import date, timedelta

import streamlit as st

from components import (
    show_dashboard,
    show_selected_workout_route,
    show_sidebar,
    show_workout_editor,
)

from performancelab import (
    Athlete,
    create_workout,
)


# ======================================================
# Page configuration
# ======================================================

st.set_page_config(
    page_title="PerformanceLab",
    page_icon="📈",
    layout="wide",
)


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
            duration=timedelta(hours=1, minutes=30),
            elevation_gain=450,
            rpe=6,
            title="Endurance Ride",
        ),
        create_workout(
            sport="Running",
            workout_date=date.today() - timedelta(days=9),
            distance=12,
            duration=timedelta(hours=1, minutes=5),
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
            duration=timedelta(hours=1, minutes=25),
            elevation_gain=320,
            rpe=8,
            title="Long Run",
        ),
    ]

    for workout in demo_workouts:
        athlete.history.add(workout)

    return athlete


# ======================================================
# Session state
# ======================================================

def initialize_session_state() -> None:

    if "athlete" not in st.session_state:
        st.session_state.athlete = create_demo_athlete()

    if "notice" not in st.session_state:
        st.session_state.notice = None

    if "confirm_delete" not in st.session_state:
        st.session_state.confirm_delete = False

    if "edit_workout" not in st.session_state:
        st.session_state.edit_workout = False

    if "page" not in st.session_state:
        st.session_state.page = "dashboard"


# ======================================================
# Application
# ======================================================

initialize_session_state()

athlete: Athlete = st.session_state.athlete

athlete = show_sidebar(
    athlete,
)

page = st.session_state.page

if page == "dashboard":

    selected_workout = show_dashboard(
        athlete,
    )

    show_workout_editor(
        athlete,
        selected_workout,
    )

    show_selected_workout_route(
        selected_workout,
    )

else:

    TITLES = {
        "training": "Treinos",
        "goals": "Objetivos",
        "events": "Eventos",
        "analytics": "Análises",
        "statistics": "Estatísticas",
        "equipment": "Equipamento",
        "settings": "Configurações",
    }

    st.title(
        TITLES.get(page, page.title())
    )

    st.info(
        "🚧 Página em desenvolvimento."
    )

st.session_state.athlete = athlete