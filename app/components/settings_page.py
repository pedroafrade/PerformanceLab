"""
PerformanceLab

Athlete settings page.
"""

import streamlit as st

from .athlete_panel import (
    show_athlete_panel,
)
from .training_coach_consent import (
    show_training_coach_consent_settings,
)

def _settings_page_header() -> None:
    """
    Displays the standard page header used throughout
    the main application pages.
    """

    st.markdown(
        """
        <style>
        div[data-testid="stMainBlockContainer"] {
            padding-top: 3.65rem;
            padding-bottom: 0 !important;
        }

        section[data-testid="stMain"] > div {
            padding-bottom: 0 !important;
        }

        div[data-testid="stMainBlockContainer"]
        > div:last-child {
            margin-bottom: 0 !important;
            padding-bottom: 0 !important;
        }

        .settings-page-header {
            margin: 0 0 0.45rem 0;
            padding: 0;
        }

        .settings-page-title {
            margin: 0;
            font-size: 2.25rem;
            font-weight: 750;
            line-height: 1.05;
        }

        .settings-page-subtitle {
            margin-top: 0.32rem;
            font-size: 0.76rem;
            line-height: 1.15;
            opacity: 0.58;
        }
        </style>

        <div class="settings-page-header">
            <div class="settings-page-title">
                Settings
            </div>
            <div class="settings-page-subtitle">
                Manage the personal, physiological,
                nutrition and availability information
                used by PerformanceLab.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def show_settings_page(
    athlete,
    *,
    training_coach_permitted: bool = False,
    on_allow_training_coach=None,
    on_withdraw_training_coach=None,
):
    """
    Displays athlete settings while reusing the
    existing validated athlete editor.
    """

    _settings_page_header()

    st.info(
        "Changes to physiological values, heart-rate "
        "zones and availability can influence future "
        "training plans and recommendations."
    )

    st.divider()

    show_training_coach_consent_settings(
        permitted=(
            training_coach_permitted
        ),
        on_allow=(
            on_allow_training_coach
        ),
        on_withdraw=(
            on_withdraw_training_coach
        ),
    )

    st.divider()

    st.subheader(
        "Athlete profile"
    )

    st.caption(
        "These values are inputs to the PerformanceLab "
        "domain and planning system."
    )

    return show_athlete_panel(
        athlete,
        show_heading=False,
    )