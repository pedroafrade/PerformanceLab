"""
PerformanceLab

Sidebar Component.
"""

from html import escape

import streamlit as st

from .activity_input import (
    show_activity_input,
)
from .storage_panel import (
    show_storage_panel,
)


# ======================================================
# Styling
# ======================================================

def _sidebar_styles() -> None:
    """
    Applies the sidebar visual styling.
    """

    st.markdown(
        """
        <style>
        @import url(
            'https://fonts.googleapis.com/css2'
            '?family=Material+Symbols+Rounded:'
            'opsz,wght,FILL,GRAD@20..48,400,0,0'
        );

        [data-testid="stSidebar"] {
            min-width: 240px;
            max-width: 240px;
            background: transparent;
            border-right: 1px solid rgba(128, 128, 128, 0.22);
        }

        [data-testid="stSidebarContent"] {
            overflow-y: hidden;
            background: transparent;
        }

        [data-testid="stSidebarHeader"] {
            min-height: 1.5rem;
            height: 1.5rem;
            padding: 0.1rem 0.5rem 0;
        }

        [data-testid="stSidebar"] > div:first-child {
            padding: 0 0.8rem 0.35rem;
            background: transparent;
        }

        .performancelab-brand {
            margin: -0.45rem 0 0;
            padding: 0 0.5rem;
            font-size: 1.35rem;
            font-weight: 700;
            letter-spacing: -0.04em;
        }

        .sidebar-account {
            display: flex;
            align-items: center;
            gap: 0.7rem;
            margin: 0.35rem 0 0.45rem;
            padding: 0.4rem 0.5rem;
            border-radius: 0.55rem;
        }

        .sidebar-account-avatar {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 2rem;
            height: 2rem;
            flex: 0 0 2rem;
            border: 1px solid rgba(128, 128, 128, 0.35);
            border-radius: 50%;
            font-size: 1rem;
        }

        .sidebar-account-name {
            min-width: 0;
            flex: 1;
            overflow: hidden;
            font-size: 0.86rem;
            font-weight: 600;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .sidebar-account-arrow {
            color: rgba(128, 128, 128, 0.9);
            font-size: 1rem;
        }

        .sidebar-menu-item {
            display: flex;
            align-items: center;
            gap: 0.7rem;
            width: 100%;
            min-height: 1.95rem;
            margin: 0.02rem 0;
            padding: 0.34rem 0.7rem;
            overflow: hidden;
            border-radius: 0.55rem;
            color: inherit;
            font-size: 0.9rem;
            font-weight: 500;
            line-height: 1.2;
            white-space: nowrap;
        }

        .sidebar-menu-item-active {
            background: rgba(100,149,237,0.14);
            border-left: 3px solid rgb(100,149,237);
            font-weight: 700;
            padding-left: calc(0.7rem - 3px);
        }

        .sidebar-menu-icon {
            width: 1.3rem;
            flex: 0 0 1.3rem;
            text-align: center;
            font-family: "Material Symbols Rounded";
            font-size: 1.15rem;
            font-style: normal;
            font-weight: normal;
            line-height: 1;
            letter-spacing: normal;
            text-transform: none;
            white-space: nowrap;
            word-wrap: normal;
            direction: ltr;
            -webkit-font-feature-settings: "liga";
            -webkit-font-smoothing: antialiased;
            font-feature-settings: "liga";
        }

        .sidebar-menu-label {
            min-width: 0;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .sidebar-bottom {
            margin-top: 1rem;
        }

        .sidebar-section-label {
            margin: 0.35rem 0 0.2rem;
            padding: 0 0.5rem;
            color: rgba(128, 128, 128, 0.9);
            font-size: 0.68rem;
            font-weight: 600;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }

        [data-testid="stSidebar"] hr {
            margin: 0.4rem 0;
            border-color: rgba(128, 128, 128, 0.22);
        }


        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            margin-top: 0.35rem;
            margin-bottom: 0.3rem;
            font-size: 1rem;
            line-height: 1.2;
        }

        [data-testid="stSidebar"] p {
            margin-bottom: 0.3rem;
        }

        [data-testid="stSidebar"] [data-testid="stFileUploader"] {
            margin-bottom: 0.25rem;
        }

        [data-testid="stSidebar"]
        [data-testid="stFileUploaderDropzone"] {
            min-height: 3.4rem;
            padding: 0.45rem;
        }

        [data-testid="stSidebar"] button {
            min-height: 2.25rem;
            padding-top: 0.3rem;
            padding-bottom: 0.3rem;
        }

        [data-testid="stSidebar"] .stButton,
        [data-testid="stSidebar"] .stFileUploader,
        [data-testid="stSidebar"] .stSelectbox,
        [data-testid="stSidebar"] .stTextInput,
        [data-testid="stSidebar"] .stNumberInput {
            margin-bottom: 0.25rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ======================================================
# Navigation
# ======================================================

def _show_navigation() -> None:
    """
    Displays the sidebar navigation structure.

    Navigation actions will be connected in a later step.
    """

    items = (
        ("dashboard", "Dashboard", True),
        ("fitness_center", "Treinos", False),
        ("flag", "Objetivos", False),
        ("event", "Eventos", False),
        ("analytics", "Análises", False),
        ("bar_chart", "Estatísticas", False),
        ("directions_bike", "Equipamento", False),
        ("settings", "Configurações", False),
    )

    for icon, label, active in items:

        active_class = (
            " sidebar-menu-item-active"
            if active
            else ""
        )

        st.markdown(
            f"""
            <div class="sidebar-menu-item{active_class}">
                <span class="sidebar-menu-icon">{icon}</span>
                <span class="sidebar-menu-label">{label}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ======================================================
# User account
# ======================================================

def _show_user_account(
    athlete,
) -> None:
    """
    Displays the athlete name as the linked user account.
    """

    athlete_name = escape(
        str(athlete.name)
    )

    st.markdown(
        f"""
        <div class="sidebar-account">
            <span class="sidebar-account-avatar">◯</span>
            <span class="sidebar-account-name">
                {athlete_name}
            </span>
            <span class="sidebar-account-arrow">›</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ======================================================
# Sidebar
# ======================================================

def show_sidebar(
    athlete,
):
    """
    Displays the application sidebar.

    Returns
    -------
    Athlete
        Current athlete instance.
    """

    with st.sidebar:

        _sidebar_styles()

        st.markdown(
            '<div class="performancelab-brand">'
            'performancelab'
            '</div>',
            unsafe_allow_html=True,
        )

        _show_user_account(
            athlete
        )

        st.divider()

        _show_navigation()

        st.divider()

        with st.expander(
            "Athlete data",
            expanded=False,
        ):

            athlete = show_storage_panel(
                athlete
            )

        st.markdown(
            '<div class="sidebar-section-label">'
            'Importar treino'
            '</div>',
            unsafe_allow_html=True,
        )

        athlete = show_activity_input(
            athlete
        )

    return athlete