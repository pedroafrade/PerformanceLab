"""
PerformanceLab

Sidebar Component.
"""

from html import escape

import streamlit as st

from .activity_input import (
    show_activity_input,
)


# ======================================================
# Navigation configuration
# ======================================================

_NAVIGATION_ITEMS = (
    (
        "dashboard",
        "Dashboard",
        ":material/dashboard:",
    ),
    (
        "training",
        "Treinos",
        ":material/fitness_center:",
    ),
    (
        "goals",
        "Objetivos",
        ":material/flag:",
    ),
    (
        "events",
        "Eventos",
        ":material/event:",
    ),
    (
        "analytics",
        "Análises",
        ":material/analytics:",
    ),
    (
        "statistics",
        "Estatísticas",
        ":material/bar_chart:",
    ),
    (
        "equipment",
        "Equipamento",
        ":material/directions_bike:",
    ),
    (
        "settings",
        "Configurações",
        ":material/settings:",
    ),
)


# ======================================================
# Styling
# ======================================================

def _sidebar_styles(
    active_page: str,
) -> None:
    """
    Applies the sidebar visual styling.
    """

    active_selector = (
        f".st-key-sidebar_nav_{active_page} button"
    )

    st.markdown(
        f"""
        <style>
        [data-testid="stAppViewContainer"],
        [data-testid="stSidebar"],
        [data-testid="stSidebarContent"] {{
            background: var(--background-color);
        }}

        [data-testid="stSidebar"] {{
            min-width: 240px;
            max-width: 240px;
            border-right: 1px solid rgba(128, 128, 128, 0.22);
        }}

        [data-testid="stSidebarContent"] {{
            height: 100vh;
            overflow: hidden;
        }}

        [data-testid="stSidebarHeader"] {{
            min-height: 1rem;
            height: 1rem;
            padding: 0;
        }}

        [data-testid="stSidebar"] > div:first-child {{
            padding: 0 0.7rem 0.25rem;
        }}

        .performancelab-brand {{
            margin: -0.55rem 0 0;
            padding: 0 0.45rem;
            font-size: 1.3rem;
            font-weight: 700;
            letter-spacing: -0.04em;
            line-height: 1.2;
        }}

        .sidebar-account {{
            display: flex;
            align-items: center;
            gap: 0.55rem;
            margin: 0.2rem 0 0.25rem;
            padding: 0.3rem 0.45rem;
            border-radius: 0.5rem;
        }}

        .sidebar-account-avatar {{
            display: flex;
            align-items: center;
            justify-content: center;
            width: 1.7rem;
            height: 1.7rem;
            flex: 0 0 1.7rem;
            border: 1px solid rgba(128, 128, 128, 0.35);
            border-radius: 50%;
            font-size: 0.8rem;
        }}

        .sidebar-account-name {{
            min-width: 0;
            flex: 1;
            overflow: hidden;
            font-size: 0.82rem;
            font-weight: 600;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}

        [data-testid="stSidebar"] hr {{
            margin: 0.25rem 0;
            border-color: rgba(128, 128, 128, 0.22);
        }}

        .st-key-sidebar_navigation {{
            margin: 0;
        }}

        .st-key-sidebar_navigation .stButton {{
            margin: 0;
        }}

        .st-key-sidebar_navigation .stButton button {{
            min-height: 1.95rem;
            height: 1.95rem;
            margin: 0.015rem 0;
            padding: 0.25rem 0.55rem;
            justify-content: flex-start;
            border: 0;
            border-radius: 0.5rem;
            background: transparent;
            box-shadow: none;
            color: inherit;
            font-size: 0.86rem;
            font-weight: 500;
        }}

        .st-key-sidebar_navigation .stButton button:hover {{
            background: rgba(128, 128, 128, 0.10);
            border: 0;
            color: inherit;
        }}

        .st-key-sidebar_navigation .stButton button:focus {{
            box-shadow: none;
        }}

        {active_selector} {{
            padding-left: calc(0.55rem - 3px);
            background: rgba(100, 149, 237, 0.14);
            border-left: 3px solid rgb(100, 149, 237);
            font-weight: 700;
        }}

        {active_selector}:hover {{
            background: rgba(100, 149, 237, 0.18);
            border-left: 3px solid rgb(100, 149, 237);
        }}

        .st-key-sidebar_lower {{
            margin-top: 0.15rem;
        }}

        .sidebar-section-label {{
            margin: 0.15rem 0 0.05rem;
            padding: 0 0.4rem;
            color: rgba(128, 128, 128, 0.9);
            font-size: 0.63rem;
            font-weight: 600;
            letter-spacing: 0.05em;
            line-height: 1.1;
            text-transform: uppercase;
        }}

        [data-testid="stSidebar"] details {{
            margin: 0;
        }}

        [data-testid="stSidebar"] details summary {{
            min-height: 1.85rem;
            padding-top: 0.2rem;
            padding-bottom: 0.2rem;
            font-size: 0.8rem;
        }}

        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {{
            margin: 0;
            font-size: 0.9rem;
            line-height: 1.1;
        }}

        .st-key-sidebar_activity
        [data-testid="stHeadingWithActionElements"] {{
            display: none;
        }}

        .st-key-sidebar_activity
        [data-testid="stSegmentedControl"] {{
            margin-bottom: 0.1rem;
        }}

        .st-key-sidebar_activity
        [data-testid="stSegmentedControl"] button {{
            min-height: 1.75rem;
            padding-top: 0.15rem;
            padding-bottom: 0.15rem;
            font-size: 0.76rem;
        }}

        .st-key-sidebar_activity
        [data-testid="stFileUploader"] {{
            margin: 0;
        }}

        .st-key-sidebar_activity
        [data-testid="stFileUploaderDropzone"] {{
            min-height: 2.85rem;
            padding: 0.3rem;
        }}

        .st-key-sidebar_activity
        [data-testid="stFileUploaderDropzoneInstructions"] {{
            font-size: 0.72rem;
            line-height: 1.05;
        }}

        .st-key-sidebar_activity
        [data-testid="stFileUploaderDropzone"] button {{
            min-height: 1.7rem;
            padding: 0.15rem 0.45rem;
            font-size: 0.72rem;
        }}

        .st-key-sidebar_activity p {{
            margin-bottom: 0.1rem;
            font-size: 0.72rem;
        }}

        [data-testid="stSidebar"] .stSelectbox,
        [data-testid="stSidebar"] .stTextInput,
        [data-testid="stSidebar"] .stNumberInput {{
            margin-bottom: 0.15rem;
        }}

        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label {{
            text-align: left !important;
        }}

        [data-testid="stSidebar"] button {{
            text-align: left !important;
        }}

        [data-testid="stSidebar"] button > div,
        [data-testid="stSidebar"] button p {{
            width: 100%;
            justify-content: flex-start !important;
            text-align: left !important;
        }}

        [data-testid="stSidebar"] details summary,
        [data-testid="stSidebar"] details summary > div {{
            justify-content: flex-start !important;
            text-align: left !important;
        }}

        </style>
        """,
        unsafe_allow_html=True,
    )


# ======================================================
# Navigation
# ======================================================

def _set_page(
    page: str,
) -> None:
    """
    Stores the selected application page.
    """

    st.session_state.page = page


def _show_navigation() -> str:
    """
    Displays the application navigation.

    Returns
    -------
    str
        Selected page identifier.
    """

    if "page" not in st.session_state:

        st.session_state.page = "dashboard"

    with st.container(
        key="sidebar_navigation",
    ):

        for page, label, icon in _NAVIGATION_ITEMS:

            st.button(
                label,
                icon=icon,
                use_container_width=True,
                key=f"sidebar_nav_{page}",
                on_click=_set_page,
                args=(page,),
            )

    return st.session_state.page


# ======================================================
# User account
# ======================================================

def _show_user_account(
    athlete,
) -> None:
    """
    Displays the athlete name below the branding.
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
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.button(
        "Edit athlete",
        icon=":material/edit:",
        use_container_width=True,
        key="sidebar_edit_athlete",
        on_click=_set_page,
        args=("athlete",),
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

    active_page = st.session_state.get(
        "page",
        "dashboard",
    )

    with st.sidebar:

        _sidebar_styles(
            active_page
        )

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

        with st.container(
            key="sidebar_lower",
        ):

            st.markdown(
                '<div class="sidebar-section-label">'
                'Importar treino'
                '</div>',
                unsafe_allow_html=True,
            )

            with st.container(
                key="sidebar_activity",
            ):

                athlete = show_activity_input(
                    athlete
                )

    return athlete