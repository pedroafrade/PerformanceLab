"""Daily Brief timezone confirmation controls for Settings."""

import streamlit as st


COMMON_TIMEZONES = (
    "Europe/Lisbon",
    "Atlantic/Azores",
    "Europe/London",
    "Europe/Madrid",
    "Europe/Paris",
    "America/New_York",
    "America/Los_Angeles",
    "UTC",
)


def timezone_options(current_timezone: str | None) -> tuple[str, ...]:
    """Keep a valid saved value visible even when it is not a common option."""

    if current_timezone and current_timezone not in COMMON_TIMEZONES:
        return (current_timezone, *COMMON_TIMEZONES)
    return COMMON_TIMEZONES


def show_daily_brief_timezone_settings(
    *,
    current_timezone: str | None,
    on_confirm=None,
) -> None:
    """Let the signed-in user explicitly confirm their local day boundary."""

    st.subheader("Daily Brief timezone")
    st.caption(
        "Confirm your local timezone so the automatic Daily Brief is created "
        "for the correct day. PerformanceLab does not infer it from your device."
    )

    options = timezone_options(current_timezone)
    selected = st.selectbox(
        "Timezone",
        options,
        index=options.index(current_timezone) if current_timezone else 0,
        key="daily_brief_timezone_selection",
    )

    if current_timezone:
        st.caption(f"Currently confirmed: {current_timezone}")
    else:
        st.info("Confirm a timezone before automatic Daily Brief generation can start.")

    if st.button(
        "Confirm timezone",
        key="confirm_daily_brief_timezone",
        use_container_width=True,
    ):
        if on_confirm is None:
            st.error("Timezone confirmation is unavailable in this environment.")
        else:
            on_confirm(selected)
            st.success("Timezone confirmed.")
