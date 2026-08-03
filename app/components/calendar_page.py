"""
PerformanceLab

Monthly training calendar page.
"""

from datetime import date
from html import escape

import streamlit as st

from performancelab.presentation import (
    CalendarPresenter,
)


def _shift_month(
    anchor: date,
    offset: int,
) -> date:
    """
    Moves a first-of-month date by the given month offset.
    """

    month_index = (
        anchor.year * 12
        + anchor.month
        - 1
        + offset
    )

    year, zero_based_month = divmod(
        month_index,
        12,
    )

    return date(
        year,
        zero_based_month + 1,
        1,
    )


def _set_calendar_month(
    anchor: date,
) -> None:
    """
    Stores the visible calendar month.
    """

    st.session_state.calendar_month_anchor = (
        anchor
    )


def _calendar_item_label(
    item,
) -> str:
    """
    Returns the visible label of one calendar item.
    """

    if (
        item.kind == "event"
        and item.priority
    ):
        return (
            f"[{item.priority.upper()}] "
            f"{item.title}"
        )

    return item.title


def _calendar_html(
    calendar,
) -> str:
    """
    Renders calendar presentation data as an HTML grid.
    """

    weekday_headers = (
        "Mon",
        "Tue",
        "Wed",
        "Thu",
        "Fri",
        "Sat",
        "Sun",
    )

    parts = [
        '<div class="training-calendar-scroll">',
        '<div class="training-calendar-grid">',
    ]

    for weekday in weekday_headers:

        parts.append(
            (
                '<div class="training-calendar-weekday">'
                f"{weekday}"
                "</div>"
            )
        )

    for week in calendar.weeks:

        for calendar_day in week:

            classes = [
                "training-calendar-day",
            ]

            if not calendar_day.is_current_month:
                classes.append(
                    "outside-month"
                )

            if calendar_day.is_today:
                classes.append(
                    "today"
                )

            parts.append(
                (
                    f'<div class="{" ".join(classes)}">'
                    '<div class="training-calendar-day-header">'
                    f"<strong>{calendar_day.day.day}</strong>"
                )
            )

            if calendar_day.phase:

                parts.append(
                    (
                        '<span class="training-calendar-phase">'
                        f"{escape(calendar_day.phase)}"
                        "</span>"
                    )
                )

            parts.append(
                "</div>"
            )

            for item in calendar_day.items:

                status_class = (
                    str(
                        item.status
                        or "none"
                    )
                    .replace("_", "-")
                )

                label = escape(
                    _calendar_item_label(
                        item
                    )
                )

                parts.append(
                    (
                        '<div class="training-calendar-item '
                        f'{escape(item.kind)} '
                        f'status-{escape(status_class)}">'
                        f"{label}"
                        "</div>"
                    )
                )

            parts.append(
                "</div>"
            )

    parts.extend(
        [
            "</div>",
            "</div>",
        ]
    )

    return "".join(parts)


def _calendar_styles() -> None:
    """
    Applies calendar-specific visual styling.
    """

    st.markdown(
        """
        <style>
        .training-calendar-scroll {
            width: 100%;
            overflow-x: auto;
        }

        .training-calendar-grid {
            min-width: 980px;
            display: grid;
            grid-template-columns: repeat(7, minmax(130px, 1fr));
            gap: 1px;
            padding: 1px;
            border: 1px solid rgba(128, 128, 128, 0.25);
            border-radius: 0.65rem;
            background: rgba(128, 128, 128, 0.22);
            overflow: hidden;
        }

        .training-calendar-weekday {
            padding: 0.65rem;
            background: var(--secondary-background-color);
            color: rgba(128, 128, 128, 0.95);
            font-size: 0.76rem;
            font-weight: 700;
            text-align: center;
            text-transform: uppercase;
        }

        .training-calendar-day {
            min-height: 118px;
            padding: 0.5rem;
            background: var(--background-color);
        }

        .training-calendar-day.outside-month {
            opacity: 0.42;
        }

        .training-calendar-day.today {
            box-shadow:
                inset 0 0 0 2px
                var(--primary-color);
        }

        .training-calendar-day-header {
            min-height: 1.35rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.3rem;
            margin-bottom: 0.35rem;
        }

        .training-calendar-phase {
            overflow: hidden;
            color: rgba(128, 128, 128, 0.95);
            font-size: 0.62rem;
            text-overflow: ellipsis;
            text-transform: uppercase;
            white-space: nowrap;
        }

        .training-calendar-item {
            margin-top: 0.28rem;
            padding: 0.3rem 0.4rem;
            overflow: hidden;
            border-left: 3px solid;
            border-radius: 0.3rem;
            font-size: 0.7rem;
            line-height: 1.15;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .training-calendar-item.planned {
            border-color: #4f86f7;
            background: rgba(79, 134, 247, 0.13);
        }

        .training-calendar-item.completed {
            border-color: #39a96b;
            background: rgba(57, 169, 107, 0.13);
        }

        .training-calendar-item.event {
            border-color: #e05a5a;
            background: rgba(224, 90, 90, 0.15);
            font-weight: 700;
        }

        .training-calendar-item.status-missed {
            border-color: #d28b27;
            background: rgba(210, 139, 39, 0.15);
        }

        .training-calendar-item.status-substitute,
        .training-calendar-item.status-modified {
            border-style: dashed;
        }

        .training-calendar-legend {
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            margin-top: 0.75rem;
            color: rgba(128, 128, 128, 0.95);
            font-size: 0.75rem;
        }

        .training-calendar-legend span::before {
            content: "";
            display: inline-block;
            width: 0.65rem;
            height: 0.65rem;
            margin-right: 0.3rem;
            border-radius: 0.15rem;
            vertical-align: -0.05rem;
        }

        .training-calendar-legend .planned::before {
            background: #4f86f7;
        }

        .training-calendar-legend .completed::before {
            background: #39a96b;
        }

        .training-calendar-legend .event::before {
            background: #e05a5a;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_calendar_page(
    athlete,
) -> None:
    """
    Displays the athlete's monthly training calendar.
    """

    st.title(
        "Calendar"
    )

    st.caption(
        "See planned training, completed activities "
        "and events in one timeline."
    )

    today = date.today()

    if (
        "calendar_month_anchor"
        not in st.session_state
    ):
        st.session_state.calendar_month_anchor = (
            today.replace(day=1)
        )

    anchor = (
        st.session_state
        .calendar_month_anchor
    )

    previous_month = _shift_month(
        anchor,
        -1,
    )

    next_month = _shift_month(
        anchor,
        1,
    )

    (
        previous_column,
        heading_column,
        today_column,
        next_column,
    ) = st.columns(
        [1, 5, 1, 1]
    )

    with previous_column:

        st.button(
            "Previous",
            icon=":material/chevron_left:",
            use_container_width=True,
            key="calendar_previous",
            on_click=_set_calendar_month,
            args=(previous_month,),
        )

    with heading_column:

        st.subheader(
            anchor.strftime(
                "%B %Y"
            )
        )

    with today_column:

        st.button(
            "Today",
            use_container_width=True,
            key="calendar_today",
            on_click=_set_calendar_month,
            args=(
                today.replace(day=1),
            ),
        )

    with next_column:

        st.button(
            "Next",
            icon=":material/chevron_right:",
            use_container_width=True,
            key="calendar_next",
            on_click=_set_calendar_month,
            args=(next_month,),
        )

    calendar = CalendarPresenter(
        history=athlete.history,
        training_plan=(
            athlete.training_plan
        ),
        events=athlete.events,
    ).build(
        year=anchor.year,
        month=anchor.month,
        reference_day=today,
    )

    _calendar_styles()

    st.markdown(
        _calendar_html(
            calendar
        ),
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="training-calendar-legend">
            <span class="planned">Planned workout</span>
            <span class="completed">Completed activity</span>
            <span class="event">Event</span>
        </div>
        """,
        unsafe_allow_html=True,
    )