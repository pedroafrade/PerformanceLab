"""
PerformanceLab

Training Coach consent interface.
"""

import streamlit as st

def _show_training_coach_permission_scope() -> None:
    """The same combined disclosure in Activities and Settings."""
    st.write(
        "One Training Coach permission covers activity interpretations you "
        "request in Activities and automatic Daily Briefs from Google Gemini."
    )
    st.caption(
        "Daily Brief will be generated on your first authenticated session "
        "each local day, without a Generate button, and may be regenerated "
        "when important plan, activity or reported information changes."
    )
    st.caption(
        "Automatic generation is still in preparation and is not active yet. "
        "Accepting this permission does not generate a Daily Brief now."
    )
    with st.expander("Data use and permission details", expanded=False):
        st.write(
            "Only relevant context is sent: activity summaries and RPE; "
            "profile and threshold references; training plan, goals, events "
            "and availability; recent load and recovery; and dated Additional "
            "Information, including symptoms you report. Original activity "
            "files and credentials are not sent."
        )
        st.caption(
            "Generated interpretations are retained with your account and "
            "included in data export and deletion. The result supports training "
            "decisions and is not medical advice. It does not change your plan."
        )
        st.caption(
            "Withdraw permission in Settings to stop both manual interpretations "
            "and automatic Daily Brief generation. Previously generated records "
            "remain until deleted with your data."
        )
        st.caption(
            "This replaces the earlier manual-only permission. Existing users "
            "confirm the updated scope once using the same Allow Training Coach "
            "button; there is no separate Daily Brief permission."
        )


@st.dialog(
    "Training Coach"
)
def show_training_coach_consent_dialog(
    *,
    on_allow,
) -> None:
    """
    Ask for the combined Training Coach scope using the existing single action.
    """

    _show_training_coach_permission_scope()

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

        _show_training_coach_permission_scope()

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
