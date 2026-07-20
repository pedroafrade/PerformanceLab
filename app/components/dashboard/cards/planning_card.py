"""
PerformanceLab

Planning dashboard card.
"""

from datetime import timedelta
from html import escape

import streamlit as st


WEEKDAY_LABELS = (
    "seg",
    "ter",
    "qua",
    "qui",
    "sex",
    "sáb",
    "dom",
)


def _format_duration(
    duration: timedelta | None,
) -> str | None:
    """
    Format a duration for compact display.
    """

    if duration is None:
        return None

    total_minutes = int(
        duration.total_seconds() // 60
    )

    hours, minutes = divmod(
        total_minutes,
        60,
    )

    if hours and minutes:
        return f"{hours}h {minutes:02d}m"

    if hours:
        return f"{hours}h"

    return f"{minutes} min"


def _format_distance(
    distance: float | None,
) -> str | None:
    """
    Format a workout distance.
    """

    if distance is None:
        return None

    if float(distance).is_integer():
        return f"{int(distance)} km"

    return f"{distance:.1f} km"


def _planned(day) -> bool:
    """
    Return whether the day contains a planned workout.
    """

    return bool(
        day.title
        or day.sport
    )


def _completed(day) -> bool:
    """
    Return whether an activity was completed on the day.
    """

    return bool(day.completed)


def _day_title(day) -> str:
    """
    Return the primary description for one day.
    """

    completed_title = day.completed_title
    completed_sport = day.completed_sport

    if _completed(day) and not _planned(day):

        return (
            completed_title
            or completed_sport
            or "Atividade"
        )

    return (
        day.title
        or day.sport
        or "Descanso"
    )


def _day_details(day) -> str:
    """
    Return compact secondary details for one day.
    """

    completed_title = day.completed_title
    completed_sport = day.completed_sport

    actual_title = (
        completed_title
        or completed_sport
    )

    planned_title = (
        day.title
        or day.sport
    )

    if (
        _completed(day)
        and actual_title
        and planned_title
        and actual_title.lower()
        != planned_title.lower()
    ):

        return f"Feito: {actual_title}"

    details = []

    distance = _format_distance(
        day.distance
    )

    duration = _format_duration(
        day.duration
    )

    if distance:
        details.append(distance)

    if duration:
        details.append(duration)

    if day.intensity:
        details.append(day.intensity)

    return " · ".join(details)


def _marker_html(
    *,
    planned: bool,
    completed: bool,
) -> str:
    """
    Build the circular day status marker.
    """

    if completed:

        marker_class = (
            "weekly-plan-marker-completed"
        )

        symbol = "✓"

    elif planned:

        marker_class = (
            "weekly-plan-marker-planned"
        )

        symbol = ""

    else:

        marker_class = (
            "weekly-plan-marker-rest"
        )

        symbol = ""

    return (
        '<div class="weekly-plan-marker '
        f'{marker_class}">'
        f"{symbol}"
        "</div>"
    )


def _next_workout_description(
    workout,
) -> str | None:
    """
    Build the next-workout description.
    """

    if workout is None:
        return None

    title = (
        workout.title
        or workout.sport
        or "Treino"
    )

    details = []

    if workout.scheduled_at is not None:

        weekday = WEEKDAY_LABELS[
            workout.scheduled_at.weekday()
        ]

        details.append(
            workout.scheduled_at.strftime(
                f"{weekday}, %d/%m às %H:%M"
            )
        )

    distance = _format_distance(
        workout.distance
    )

    duration = _format_duration(
        workout.duration
    )

    if distance:
        details.append(distance)

    if duration:
        details.append(duration)

    summary = escape(title)

    if details:

        summary += (
            " · "
            + escape(
                " · ".join(details)
            )
        )

    description = ""

    if workout.description:

        description = (
            '<span class="weekly-plan-next-description">'
            f" — {escape(workout.description)}"
            "</span>"
        )

    return (
        f"<strong>{summary}</strong>"
        f"{description}"
    )


def show_planning_card(
    planning,
) -> None:
    """
    Display a compact horizontal seven-day plan.
    """

    if planning is None:

        st.info("No planning available.")

        return

    st.markdown(
        """
<style>
.weekly-plan-day {
    min-height: 112px;
    padding: 6px 3px;
    border: 1px solid transparent;
    border-radius: 9px;
    text-align: center;
    box-sizing: border-box;
}

.weekly-plan-day-today {
    border-color: rgba(128, 128, 128, 0.55);
}

.weekly-plan-weekday {
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: lowercase;
}

.weekly-plan-date {
    margin-left: 3px;
    font-size: 0.68rem;
    font-weight: 400;
    opacity: 0.55;
}

.weekly-plan-marker {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    margin: 7px auto;
    border-radius: 50%;
    box-sizing: border-box;
    font-size: 1rem;
    font-weight: 800;
    line-height: 1;
}

.weekly-plan-marker-rest {
    border: 1.5px solid rgba(128, 128, 128, 0.55);
}

.weekly-plan-marker-planned {
    border: 3px solid currentColor;
}

.weekly-plan-marker-completed {
    border: 3px solid currentColor;
}

.weekly-plan-title {
    min-height: 18px;
    overflow-wrap: anywhere;
    font-size: 0.76rem;
    font-weight: 600;
    line-height: 1.15;
}

.weekly-plan-details {
    min-height: 16px;
    margin-top: 3px;
    overflow-wrap: anywhere;
    font-size: 0.66rem;
    line-height: 1.15;
    opacity: 0.65;
}

.weekly-plan-next {
    margin-top: 8px;
    padding: 8px 11px;
    border: 1px solid rgba(128, 128, 128, 0.55);
    border-radius: 8px;
    line-height: 1.3;
}

.weekly-plan-next-label {
    margin-right: 6px;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.03em;
    opacity: 0.60;
    text-transform: uppercase;
}

.weekly-plan-next-description {
    font-size: 0.78rem;
    opacity: 0.65;
}
</style>
        """,
        unsafe_allow_html=True,
    )

    columns = st.columns(
        7,
        gap="small",
    )

    for column, day in zip(
        columns,
        planning.weekly_plan.days,
    ):

        classes = [
            "weekly-plan-day",
        ]

        if day.is_today:

            classes.append(
                "weekly-plan-day-today"
            )

        weekday = WEEKDAY_LABELS[
            day.day.weekday()
        ]

        title = _day_title(day)
        details = _day_details(day)

        marker = _marker_html(
            planned=_planned(day),
            completed=_completed(day),
        )

        with column:

            st.markdown(
                (
                    f'<div class="{" ".join(classes)}">'
                    '<div class="weekly-plan-weekday">'
                    f"{weekday}"
                    '<span class="weekly-plan-date">'
                    f"{day.day.day}"
                    "</span>"
                    "</div>"
                    f"{marker}"
                    '<div class="weekly-plan-title">'
                    f"{escape(title)}"
                    "</div>"
                    '<div class="weekly-plan-details">'
                    f"{escape(details)}"
                    "</div>"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )

    next_description = (
        _next_workout_description(
            planning.next_workout
        )
    )

    if next_description:

        st.markdown(
            (
                '<div class="weekly-plan-next">'
                '<span class="weekly-plan-next-label">'
                "Próximo treino"
                "</span>"
                f"{next_description}"
                "</div>"
            ),
            unsafe_allow_html=True,
        )