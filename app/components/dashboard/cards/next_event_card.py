"""
PerformanceLab

Next Event Card
"""

import streamlit as st

from .metric_card_body import (
    MetricCardDetail,
    MetricCardMetric,
    metric_card_body,
)


def next_event_card(
    event,
) -> None:
    """
    Displays the next sporting event.
    """

    if event is None or not event.name:

        st.caption(
            "No upcoming events."
        )

        return

    details = []

    event_date = _format_event_date(
        event.event_date,
        event.days_remaining,
    )

    if event_date:

        details.append(
            MetricCardDetail(
                label="Date",
                value=event_date,
            )
        )

    location = _format_location(
        event.location,
        event.country,
    )

    if location:

        details.append(
            MetricCardDetail(
                label="Location",
                value=location,
            )
        )

    if event.target_time:

        details.append(
            MetricCardDetail(
                label="Target",
                value=str(
                    event.target_time
                ),
            )
        )

    metric_card_body(
        metrics=[
            MetricCardMetric(
                value=event.name,
                label=_format_event_details(
                    event,
                )
                or "Upcoming event",
            )
        ],
        details=details,
    )


def _format_event_details(
    event,
) -> str:
    """
    Formats sport, distance and elevation.
    """

    parts = []

    if event.sport:

        parts.append(
            event.sport
        )

    if event.distance is not None:

        parts.append(
            f"{event.distance:g} km"
        )

    if event.elevation_gain is not None:

        parts.append(
            f"+{event.elevation_gain:g} m"
        )

    return " · ".join(
        parts
    )


def _format_event_date(
    event_date,
    days_remaining: int | None,
) -> str | None:
    """
    Formats the event date and countdown.
    """

    if event_date is None:

        return None

    formatted_date = event_date.strftime(
        "%d.%m.%Y"
    )

    countdown = _format_countdown(
        days_remaining
    )

    if countdown is None:

        return formatted_date

    return (
        f"{formatted_date} ({countdown})"
    )


def _format_countdown(
    days_remaining: int | None,
) -> str | None:
    """
    Formats the number of days remaining.
    """

    if days_remaining is None:

        return None

    if days_remaining == 0:

        return "today"

    if days_remaining == 1:

        return "tomorrow"

    return (
        f"{days_remaining}d left"
    )


def _format_location(
    location: str | None,
    country: str | None,
) -> str | None:
    """
    Formats the event location.
    """

    parts = [
        value
        for value in (
            location,
            country,
        )
        if value
    ]

    if not parts:

        return None

    return ", ".join(
        parts
    )