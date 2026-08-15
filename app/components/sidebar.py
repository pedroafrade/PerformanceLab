"""
PerformanceLab

Sidebar Component.
"""

from html import escape

import streamlit as st

from .activity_input import (
    show_activity_input,
)
from .i18n import translate


# ======================================================
# Navigation configuration
# ======================================================

_NAVIGATION_ITEMS = (
    (
        "today",
        "nav.today",
        ":material/home:",
    ),
    (
        "training",
        "nav.plan",
        ":material/fitness_center:",
    ),
    (
        "activities",
        "nav.activities",
        ":material/directions_run:",
    ),
    (
        "calendar",
        "nav.calendar",
        ":material/calendar_month:",
    ),
    (
        "development",
        "nav.development",
        ":material/trending_up:",
    ),
    (
        "settings",
        "nav.settings",
        ":material/settings:",
    ),
)
_HOME_PAGE = "dashboard"

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
            height: 100dvh;
            min-height: 0;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }}

        [data-testid="stSidebarContent"]
        > div:first-child {{
            min-height: 0;
            display: flex;
            flex: 1 1 auto;
            flex-direction: column;
            justify-content: flex-start;
            align-items: stretch;
        }}

        [data-testid="stSidebarContent"]
        > div:first-child
        > [data-testid="stVerticalBlock"] {{
            width: 100%;
            min-height: 0;
            display: flex;
            flex: 1 1 auto;
            flex-direction: column;
            justify-content: flex-start;
            align-items: stretch;
        }}

        [data-testid="stSidebarHeader"] {{
            min-height: 1rem;
            height: 1rem;
            padding: 0;
        }}

        [data-testid="stSidebar"] > div:first-child {{
            padding:
                0
                0.7rem
                clamp(0.12rem, 0.45vh, 0.25rem);
        }}

        .st-key-sidebar_brand {{
            margin:
                clamp(-0.55rem, -0.8vh, -0.2rem)
                0
                0.35rem;
            overflow: visible;
        }}

        .st-key-sidebar_brand button {{
            width: auto !important;
            min-width: 0 !important;
            min-height: 0 !important;
            height: auto !important;
            margin: 0 !important;
            padding: 0 0.45rem !important;
            justify-content: flex-start !important;
            overflow: visible !important;
            border: 0 !important;
            border-radius: 0 !important;
            background: transparent !important;
            box-shadow: none !important;
            color: inherit !important;
        }}

        .st-key-sidebar_brand button,
        .st-key-sidebar_brand button div,
        .st-key-sidebar_brand button p,
        .st-key-sidebar_brand button span {{
            color: inherit !important;
            font-size: 2rem !important;
            font-weight: 800 !important;
            letter-spacing: -0.06em !important;
            line-height: 1 !important;
            white-space: nowrap !important;
        }}

        .st-key-sidebar_brand button p {{
            width: auto !important;
            margin: 0 !important;
        }}

        .st-key-sidebar_brand button:hover,
        .st-key-sidebar_brand button:focus,
        .st-key-sidebar_brand button:active {{
            border: 0 !important;
            background: transparent !important;
            box-shadow: none !important;
            color: inherit !important;
        }}

        .sidebar-account-label {{
            display: flex;
            min-height: clamp(1.8rem, 4vh, 2.2rem);
            align-items: center;
            gap: 0.5rem;
            padding: 0.2rem 0.45rem;
            font-size: 0.82rem;
        }}

        .sidebar-account-icon {{
            display: inline-flex;
            width: 1.45rem;
            height: 1.45rem;
            align-items: center;
            justify-content: center;
            border: 1px solid rgba(128, 128, 128, 0.35);
            border-radius: 50%;
            font-size: 0.72rem;
        }}

        .st-key-sidebar_edit_athlete button,
        .st-key-sidebar_logout button {{
            min-height: clamp(1.65rem, 3.6vh, 2rem);
            padding:
                clamp(0.08rem, 0.3vh, 0.2rem)
                0.35rem;
            font-size: clamp(0.7rem, 1.4vh, 0.8rem);
        }}

        [data-testid="stSidebar"] hr {{
            margin: clamp(0.08rem, 0.42vh, 0.25rem) 0;
            border-color: rgba(128, 128, 128, 0.22);
        }}

        .st-key-sidebar_navigation {{
            min-height: 0;
            margin: 0;
            display: flex;
            flex: 0 0 auto;
            flex-direction: column;
        }}

        .st-key-sidebar_navigation
        > [data-testid="stVerticalBlock"] {{
            gap: clamp(0.01rem, 0.16vh, 0.08rem);
        }}

        .st-key-sidebar_navigation .stButton {{
            margin: 0;
        }}

        .st-key-sidebar_navigation .stButton button {{
            min-height: clamp(1.55rem, 3.55vh, 1.95rem);
            height: clamp(1.55rem, 3.55vh, 1.95rem);
            margin: 0;
            padding:
                clamp(0.08rem, 0.35vh, 0.25rem)
                0.55rem;
            justify-content: flex-start;
            border: 0;
            border-radius: 0.5rem;
            background: transparent;
            box-shadow: none;
            color: inherit;
            font-size: clamp(0.74rem, 1.55vh, 0.86rem);
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

        .st-key-sidebar_top {{
            position: sticky;
            top: 0;
            z-index: 2;
            flex: 0 0 auto;
            min-height: 0;
            margin: 0;
            padding: 0;
            background: var(--background-color);
        }}

        .st-key-sidebar_lower {{
            flex: 1 1 auto;
            min-height: 0;
            margin: 0;
            padding-top: clamp(0.05rem, 0.3vh, 0.15rem);
            padding-right: 0.15rem;
            overflow-y: auto;
            overflow-x: hidden;
        }}

        .st-key-sidebar_lower
        > [data-testid="stVerticalBlock"] {{
            gap: clamp(0.12rem, 0.42vh, 0.45rem);
        }}

        .sidebar-section-label {{
            margin:
                clamp(0.05rem, 0.3vh, 0.15rem)
                0
                clamp(0.02rem, 0.14vh, 0.05rem);
            padding: 0 0.4rem;
            color: rgba(128, 128, 128, 0.9);
            font-size: clamp(0.56rem, 1.12vh, 0.63rem);
            font-weight: 600;
            letter-spacing: 0.05em;
            line-height: 1.05;
            text-transform: uppercase;
        }}

        [data-testid="stSidebar"] details {{
            margin: 0;
        }}

        [data-testid="stSidebar"] details summary {{
            min-height: clamp(1.55rem, 3.3vh, 1.85rem);
            padding-top: clamp(0.08rem, 0.3vh, 0.2rem);
            padding-bottom: clamp(0.08rem, 0.3vh, 0.2rem);
            font-size: clamp(0.72rem, 1.42vh, 0.8rem);
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
            min-height: clamp(1.45rem, 3.1vh, 1.75rem);
            padding-top: clamp(0.05rem, 0.22vh, 0.15rem);
            padding-bottom: clamp(0.05rem, 0.22vh, 0.15rem);
            font-size: clamp(0.68rem, 1.35vh, 0.76rem);
        }}

        .st-key-sidebar_activity
        [data-testid="stFileUploader"] {{
            margin: 0;
        }}

        .st-key-sidebar_activity
        [data-testid="stFileUploaderDropzone"] {{
            min-height: clamp(2.2rem, 5.1vh, 2.85rem);
            padding: clamp(0.18rem, 0.45vh, 0.3rem);
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

        @media (max-height: 820px) {{
            [data-testid="stSidebarHeader"] {{
                min-height: 0.5rem;
                height: 0.5rem;
            }}

            .st-key-sidebar_navigation .stButton button {{
                min-height: 1.62rem;
                height: 1.62rem;
                font-size: 0.76rem;
            }}

            .st-key-sidebar_lower
            > [data-testid="stVerticalBlock"] {{
                gap: 0.12rem;
            }}

            .st-key-sidebar_activity p {{
                margin: 0;
                font-size: 0.67rem;
                line-height: 1.05;
            }}
        }}

        @media (max-height: 700px) {{
            .st-key-sidebar_navigation .stButton button {{
                min-height: 1.45rem;
                height: 1.45rem;
                padding-top: 0.04rem;
                padding-bottom: 0.04rem;
                font-size: 0.72rem;
            }}

            .sidebar-section-label {{
                margin: 0;
                font-size: 0.54rem;
            }}

            [data-testid="stSidebar"] hr {{
                margin: 0.05rem 0;
            }}
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


def _show_navigation(
    current_user,
) -> str:
    """
    Display the application navigation.

    Coach accounts receive access to the Accounts page.
    """

    if "page" not in st.session_state:
        st.session_state.page = _HOME_PAGE

    with st.container(
        key="sidebar_navigation",
    ):

        if current_user.is_coach:

            st.button(
                "Accounts",
                icon=":material/group:",
                use_container_width=True,
                key="sidebar_nav_accounts",
                on_click=_set_page,
                args=("accounts",),
            )

        for page, label_key, icon in _NAVIGATION_ITEMS:

            st.button(
                translate(label_key),
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
    current_user,
    on_logout,
) -> None:
    """
    Display the authenticated account and its actions.
    """

    if current_user.is_coach:
        account_name = "Coach"
    else:
        account_name = str(athlete.name)

    account_name = escape(
        account_name
    )

    athlete_name = escape(
        str(athlete.name)
    )

    st.markdown(
        (
            '<div class="sidebar-account-label">'
            '<span class="sidebar-account-icon">◯</span>'
            f"<strong>{account_name}</strong>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )

    edit_column, logout_column = st.columns(
        2,
        gap="small",
    )

    with edit_column:

        st.button(
            "Edit",
            icon=":material/edit:",
            use_container_width=True,
            key="sidebar_edit_athlete",
            on_click=_set_page,
            args=("athlete",),
        )

    with logout_column:

        if st.button(
            "Logout",
            icon=":material/logout:",
            use_container_width=True,
            key="sidebar_logout",
        ):
            on_logout()

    if current_user.is_coach:

        st.caption(
            f"Viewing: {athlete_name}"
        )


# ======================================================
# Sidebar
# ======================================================

def show_sidebar(
    athlete,
    *,
    current_user,
    on_logout,
    on_import_activities,
    on_generate_plan=None,
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
        _HOME_PAGE,
    )

    with st.sidebar:

        _sidebar_styles(
            active_page
        )

        with st.container(
            key="sidebar_top",
        ):

            st.button(
                "performancelab",
                key="sidebar_brand",
                on_click=_set_page,
                args=(_HOME_PAGE,),
            )

            _show_user_account(
                athlete,
                current_user,
                on_logout,
            )

            st.divider()

            _show_navigation(
                current_user
            )

            st.divider()

        with st.container(
            key="sidebar_lower",
        ):

            st.markdown(
                (
                    '<div class="sidebar-section-label">'
                    f'{translate("activity.section")}'
                    '</div>'
                ),
                unsafe_allow_html=True,
            )

            with st.container(
                key="sidebar_activity",
            ):

                athlete = show_activity_input(
                    athlete,
                    on_import_activities=(
                        on_import_activities
                    ),
                    key_prefix="sidebar_activity",
                )

        return athlete