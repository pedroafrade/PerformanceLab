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
    Applies the standard page header and calendar-specific
    visual styling.
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

        .calendar-page-header {
            margin: 0 0 0.35rem 0;
            padding: 0;
        }

        .calendar-page-title {
            margin: 0;
            font-size: 2.25rem;
            font-weight: 750;
            line-height: 1.05;
        }

        .calendar-page-subtitle {
            margin-top: 0.32rem;
            font-size: 0.76rem;
            line-height: 1.15;
            opacity: 0.58;
        }

        .st-key-calendar-month-navigation {
            margin-top: 0.15rem;
            margin-bottom: 0.42rem;
        }

        .calendar-month-heading {
            margin: 0;
            font-size: 1.35rem;
            font-weight: 700;
            line-height: 1.1;
        }

        .st-key-calendar_previous button,
        .st-key-calendar_next button {
            min-height: 2.1rem;
            padding: 0.15rem 0.35rem;
            font-size: 1.05rem;
            line-height: 1;
        }

        .training-calendar-scroll {
            width: 100%;
            overflow: visible;
        }

        .training-calendar-grid {
            width: 100%;
            min-width: 0;
            display: grid;
            grid-template-columns:
                repeat(7, minmax(0, 1fr));
            gap: 0;
            padding: 0;
            border:
                1px solid rgba(128, 128, 128, 0.35);
            border-radius: 0.65rem;
            background: transparent;
            overflow: hidden;
        }

        .training-calendar-grid > * {
            border-right:
                1px solid rgba(128, 128, 128, 0.28);
            border-bottom:
                1px solid rgba(128, 128, 128, 0.28);
            box-sizing: border-box;
        }

        .training-calendar-grid
        > :nth-child(7n) {
            border-right: 0;
        }

        .training-calendar-weekday {
            padding: 0.42rem 0.35rem;
            background: transparent;
            color: rgba(128, 128, 128, 0.95);
            font-size: 0.69rem;
            font-weight: 700;
            line-height: 1.1;
            text-align: center;
            text-transform: uppercase;
        }

        .training-calendar-day {
            min-width: 0;
            min-height: 84px;
            padding: 0.34rem 0.4rem;
            background: transparent;
        }

        .training-calendar-day:nth-last-child(-n + 7) {
            border-bottom: 0;
        }

        .training-calendar-day.outside-month {
            opacity: 0.38;
        }

        .training-calendar-day.today {
            position: relative;
            z-index: 1;
            box-shadow:
                inset 0 0 0 2px
                rgba(128, 128, 128, 0.9);
        }

        .training-calendar-day-header {
            min-height: 1rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.25rem;
            margin-bottom: 0.18rem;
            font-size: 0.78rem;
            line-height: 1;
        }

        .training-calendar-day.today
        .training-calendar-day-header strong {
            font-weight: 800;
        }

        .training-calendar-phase {
            overflow: hidden;
            color: rgba(128, 128, 128, 0.95);
            font-size: 0.55rem;
            line-height: 1;
            text-overflow: ellipsis;
            text-transform: uppercase;
            white-space: nowrap;
        }

        .training-calendar-item {
            margin-top: 0.18rem;
            padding: 0.22rem 0.3rem;
            overflow: hidden;
            border-left: 3px solid;
            border-radius: 0.26rem;
            font-size: 0.66rem;
            line-height: 1.1;
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
            gap: 0.85rem;
            margin-top: 0.42rem;
            color: rgba(128, 128, 128, 0.95);
            font-size: 0.68rem;
            line-height: 1.1;
        }

        .training-calendar-legend span::before {
            content: "";
            display: inline-block;
            width: 0.58rem;
            height: 0.58rem;
            margin-right: 0.28rem;
            border-radius: 0.13rem;
            vertical-align: -0.04rem;
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

        @media (max-width: 900px) {
            .training-calendar-grid {
                min-width: 760px;
            }

            .training-calendar-scroll {
                overflow-x: auto;
            }
        }
        </style>

        <div class="calendar-page-header">
            <div class="calendar-page-title">
                Calendar
            </div>
            <div class="calendar-page-subtitle">
                See planned training, completed activities
                and events in one timeline.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_calendar_page(
    athlete,
) -> None:
    """
    Displays the athlete's monthly training calendar.
    """

    _calendar_styles()

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

    with st.container(
        key="calendar-month-navigation"
    ):
        (
            heading_column,
            navigation_column,
        ) = st.columns(
            [8, 1],
            gap="small",
            vertical_alignment="center",
        )

        with heading_column:
            st.markdown(
                (
                    '<div class="calendar-month-heading">'
                    f"{escape(anchor.strftime('%B %Y'))}"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )

        with navigation_column:
            (
                previous_column,
                next_column,
            ) = st.columns(
                2,
                gap="small",
            )

            with previous_column:
                st.button(
                    "‹",
                    help="Previous month",
                    use_container_width=True,
                    key="calendar_previous",
                    on_click=_set_calendar_month,
                    args=(previous_month,),
                )

            with next_column:
                st.button(
                    "›",
                    help="Next month",
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