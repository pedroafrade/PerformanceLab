"""
PerformanceLab

Training Coach consent interface.
"""

import streamlit as st

from performancelab.presentation import (
    build_activity_coach_disclosure,
)


@st.dialog(
    "Training Coach"
)
def show_training_coach_consent_dialog(
    *,
    on_allow,
) -> None:
    """
    Ask once per session for global Training Coach consent.
    """

    disclosure = (
        build_activity_coach_disclosure()
    )

    st.markdown(
        f"**{disclosure.heading}**"
    )

    st.write(
        disclosure.purpose
    )

    st.caption(
        (
            "Data sent when you request an "
            "interpretation: "
            f"{disclosure.data_summary}."
        )
    )

    st.caption(
        (
            "The original activity file is not sent. "
            "Generated interpretations are saved with "
            "your athlete profile."
        )
    )

    st.caption(
        disclosure.limitation
    )

    not_now_column, allow_column = (
        st.columns(
            2
        )
    )

    with not_now_column:

        if st.button(
            "Not now",
            key=(
                "dismiss_training_coach_consent"
            ),
            use_container_width=True,
        ):

            st.session_state[
                "training_coach_prompt_dismissed"
            ] = True

            st.rerun()

    with allow_column:

        if st.button(
            "Allow Training Coach",
            key=(
                "confirm_training_coach_consent"
            ),
            type="primary",
            use_container_width=True,
        ):

            on_allow()

            st.session_state[
                "training_coach_prompt_dismissed"
            ] = True

            st.rerun()


def show_training_coach_consent_settings(
    *,
    permitted: bool,
    on_allow,
    on_withdraw,
) -> None:
    """
    Display persistent Training Coach consent controls.
    """

    with st.container(
        border=True
    ):

        st.markdown(
            "### Training Coach"
        )

        st.caption(
            (
                "Training Coach sends selected factual "
                "activity context to Google Gemini only "
                "when you explicitly request an "
                "interpretation."
            )
        )

        st.caption(
            (
                "Original activity files are not sent. "
                "The result supports training decisions "
                "and is not medical advice."
            )
        )

        if permitted:

            st.write(
                "**Status:** Allowed"
            )

            st.button(
                "Withdraw permission",
                key=(
                    "withdraw_training_coach_consent"
                ),
                use_container_width=True,
                on_click=on_withdraw,
            )

        else:

            st.write(
                "**Status:** Not allowed"
            )

            st.button(
                "Allow Training Coach",
                key=(
                    "allow_training_coach_in_settings"
                ),
                type="primary",
                use_container_width=True,
                on_click=on_allow,
            )