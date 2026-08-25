"""
PerformanceLab

Private alpha participation consent interface.
"""

import streamlit as st

from performancelab.alpha_participation_consent import (
    ALPHA_PARTICIPATION_CONSENT_VERSION,
)


@st.dialog(
    "Private alpha participation"
)
def show_alpha_participation_consent_dialog(
    *,
    on_accept,
    on_logout,
) -> None:
    """
    Require informed acceptance before athlete data is loaded.
    """

    st.markdown(
        "**PerformanceLab is currently an experimental "
        "private alpha.**"
    )

    st.write(
        (
            "Access is limited to invited participants. "
            "Features, calculations and recommendations "
            "may change and may contain errors."
        )
    )

    st.markdown(
        """
- Your account may store training activities, routes, location, heart rate, performance, recovery and subjective feedback.
- Imported activity files are processed to create training records. The original uploaded files are not retained.
- Training Coach is optional and requires separate permission before selected activity context is sent to Google Gemini.
- Training recommendations support training decisions and are not medical advice.
- Do not rely on PerformanceLab as the only copy of important training information.
        """
    )

    st.caption(
        (
            "Participation is voluntary. Before external "
            "participants are invited, processes for "
            "support, data access, export and deletion "
            "will be made available."
        )
    )

    acknowledged = st.checkbox(
        (
            "I have read and understand this private "
            "alpha notice, and I agree to participate."
        ),
        key=(
            "alpha_participation_acknowledged"
        ),
    )

    st.caption(
        (
            "Notice version: "
            f"{ALPHA_PARTICIPATION_CONSENT_VERSION}"
        )
    )

    logout_column, accept_column = (
        st.columns(
            2
        )
    )

    with logout_column:

        if st.button(
            "Sign out",
            key=(
                "decline_alpha_participation"
            ),
            use_container_width=True,
        ):

            on_logout()

    with accept_column:

        if st.button(
            "Accept and continue",
            key=(
                "accept_alpha_participation"
            ),
            type="primary",
            use_container_width=True,
            disabled=(
                not acknowledged
            ),
        ):

            on_accept()

            st.rerun()