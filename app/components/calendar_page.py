"""
PerformanceLab

Monthly training calendar page.
"""

from datetime import date
from html import escape

import streamlit as st

from performancelab.presentation import (
    CalendarPresenter,
    PlanPresenter,
)

from .dashboard.event_manager import (
    open_event_manager,
)
from .plan_page import _plan_calendar_ics


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
    Stores the visible month and selects its first day.
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


def _calendar_session_class(item) -> str:
    """Match explicit planned-session names; do not infer type from intensity."""
    if item.kind != "planned":
        return ""
    title = " ".join(str(item.title or "").casefold().replace("_", " ").replace("-", " ").split())
    groups = {
        "easy": {"easy run", "easy runs", "shakeout", "shakeouts", "shakeout run", "shakeout runs"},
        "tempo": {"tempo", "tempo run", "tempo runs", "interval", "intervals", "interval run", "interval runs", "lt2 run"},
        "hills": {"hill", "hills", "hill run", "hill runs", "hill reps", "hill repeats"},
        "long": {"long run", "long runs"},
    }
    return "session-" + next((group for group, titles in groups.items() if title in titles), "other")


def _phase_label(
    calendar_day,
) -> str | None:
    """
    Formats phase and contiguous plan-day progress.
    """

    if not calendar_day.phase:
        return None

    phase = str(
        calendar_day.phase
    ).upper()

    if (
        calendar_day.phase_day_number
        is None
        or calendar_day.phase_total_days
        is None
    ):
        return phase

    return (
        f"{phase} - "
        f"d{calendar_day.phase_day_number} "
        f"of {calendar_day.phase_total_days}"
    )


def _calendar_html(
    calendar,
    *,
    selected_day: date | None = None,
) -> str:
    """
    Renders calendar presentation data as a selectable
    HTML grid.
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

            if (
                selected_day
                == calendar_day.day
            ):
                classes.append(
                    "selected"
                )

            if calendar_day.is_today:
                classes.append(
                    "today"
                )

            day_value = (
                calendar_day.day.isoformat()
            )

            parts.append(
                (
                    '<a class="training-calendar-day-link" '
                    f'href="#calendar-detail-{day_value}" '
                    f'aria-label="Select {day_value}">'
                    '<div '
                    f'class="{" ".join(classes)}" '
                    f'data-calendar-day="{day_value}">'
                    '<div class="training-calendar-day-header">'
                    f"<strong>{calendar_day.day.day}</strong>"
                )
            )

            phase_label = (
                _phase_label(
                    calendar_day
                )
            )

            if phase_label:
                parts.append(
                    (
                        '<span class="training-calendar-phase">'
                        f"{escape(phase_label)}"
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

                summary = (
                    (
                        '<span class="training-calendar-item-summary">'
                        f"{escape(item.summary)}"
                        "</span>"
                    )
                    if item.summary
                    else ""
                )

                parts.append(
                    (
                        '<div class="training-calendar-item '
                        f'{escape(item.kind)} '
                        f'status-{escape(status_class)} {_calendar_session_class(item)}" '
                        f'title="{escape(item.title)} — {escape(status_class)}">'
                        '<span class="training-calendar-item-title">'
                        f"{label}"
                        "</span>"
                        f"{summary}"
                        "</div>"
                    )
                )

            if calendar_day.is_rest_day:
                parts.append(
                    (
                        '<div class="training-calendar-rest">'
                        "Rest day"
                        "</div>"
                    )
                )

            parts.extend(
                [
                    "</div>",
                    "</a>",
                ]
            )

    parts.extend(
        [
            "</div>",
            "</div>",
        ]
    )

    return "".join(parts)


def _selected_day_html(
    calendar_day,
) -> str:
    """
    Builds the selected-day details.
    """

    if calendar_day is None:
        return (
            '<div class="calendar-sidebar-empty">'
            "Select a day in the visible month."
            "</div>"
        )

    parts = [
        '<div class="calendar-selected-date">',
        escape(
            calendar_day.day.strftime(
                "%A, %d %B %Y"
            )
        ),
        "</div>",
    ]

    phase_label = _phase_label(
        calendar_day
    )

    if phase_label:
        parts.extend(
            [
                '<div class="calendar-selected-phase">',
                escape(phase_label),
                "</div>",
            ]
        )

    if not calendar_day.items:
        parts.append(
            (
                '<div class="calendar-selected-rest">'
                "Rest day"
                "</div>"
            )
        )

    for item in calendar_day.items:
        label = escape(
            _calendar_item_label(
                item
            )
        )

        summary = (
            escape(item.summary)
            if item.summary
            else "No additional details"
        )

        status = (
            str(
                item.status
                or item.kind
            )
            .replace("_", " ")
            .title()
        )

        parts.append(
            (
                '<div class="calendar-selected-item">'
                '<div class="calendar-selected-item-title">'
                f"{label}"
                "</div>"
                '<div class="calendar-selected-item-summary">'
                f"{summary}"
                "</div>"
                '<div class="calendar-selected-item-status">'
                f"{escape(status)}"
                "</div>"
                "</div>"
            )
        )

    return "".join(parts)

def _selected_days_html(
    calendar,
    *,
    default_day: date,
) -> str:
    """
    Builds one locally selectable detail panel for every
    day in the visible calendar grid.
    """

    parts = [
        '<div class="calendar-selected-day-stack">'
    ]

    for week in calendar.weeks:
        for calendar_day in week:
            day_value = (
                calendar_day.day.isoformat()
            )

            classes = [
                "calendar-selected-panel",
            ]

            if (
                calendar_day.day
                == default_day
            ):
                classes.append(
                    "calendar-selected-default"
                )

            parts.append(
                (
                    f'<div id="calendar-detail-{day_value}" '
                    f'class="{" ".join(classes)}">'
                    f"{_selected_day_html(calendar_day)}"
                    "</div>"
                )
            )

    parts.append(
        "</div>"
    )

    return "".join(parts)

def _upcoming_events_html(
    events,
) -> str:
    """
    Builds the factual six-month event list.
    """

    if not events:
        return (
            '<div class="calendar-sidebar-empty">'
            "No events are scheduled in the next six months."
            "</div>"
        )

    parts = [
        '<div class="calendar-upcoming-events-list">'
    ]

    for event in events:
        details = tuple(
            value
            for value in (
                event.sport,
                (
                    f"{event.distance:g} km"
                    if event.distance
                    is not None
                    else None
                ),
                (
                    f"+{event.elevation_gain:g} m"
                    if event.elevation_gain
                    is not None
                    else None
                ),
            )
            if value
        )

        details_label = (
            " · ".join(details)
            if details
            else "Event"
        )

        priority = (
            (
                '<span class="calendar-event-priority">'
                f"{escape(event.priority.upper())}"
                "</span>"
            )
            if event.priority
            else ""
        )

        parts.append(
            (
                '<div class="calendar-upcoming-event">'
                '<div class="calendar-upcoming-event-header">'
                '<span class="calendar-upcoming-event-name">'
                f"{escape(event.name)}"
                "</span>"
                f"{priority}"
                "</div>"
                '<div class="calendar-upcoming-event-date">'
                f"{event.event_date:%d %b %Y}"
                "</div>"
                '<div class="calendar-upcoming-event-details">'
                f"{escape(details_label)}"
                "</div>"
                "</div>"
            )
        )

    parts.append(
        "</div>"
    )

    return "".join(parts)


def _calendar_styles() -> None:
    """
    Applies the Calendar page styles.
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

        .training-calendar-day-link,
        .training-calendar-day-link:link,
        .training-calendar-day-link:visited,
        .training-calendar-day-link:hover,
        .training-calendar-day-link:active {
            min-width: 0;
            color: inherit !important;
            text-decoration: none !important;
        }

        .training-calendar-day-link * {
            color: inherit !important;
            text-decoration: none !important;
        }

        .training-calendar-day-link:nth-last-child(-n + 7) {
            border-bottom: 0;
        }

        .training-calendar-day {
            min-width: 0;
            min-height: 102px;
            height: 100%;
            padding: 0.38rem 0.4rem;
            background: transparent;
            box-sizing: border-box;
        }

        .training-calendar-day-link:hover
        .training-calendar-day {
            background: rgba(128, 128, 128, 0.035);
        }

        .training-calendar-day.outside-month {
            opacity: 0.7;
        }

        .training-calendar-day.selected {
            box-shadow:
                inset 0 0 0 2px
                var(--primary-color);
        }

        .training-calendar-day.today {
            position: relative;
            z-index: 2;
            box-shadow:
                inset 0 0 0 2px
                currentColor !important;
        }

        .calendar-selected-day-stack {
            display: block;
        }

        .calendar-selected-panel {
            display: none;
            scroll-margin-top: 5rem;
        }

        .calendar-selected-panel.calendar-selected-default {
            display: block;
        }

        .calendar-selected-day-stack:has(
            .calendar-selected-panel:target
        )
        .calendar-selected-panel.calendar-selected-default {
            display: none;
        }

        .calendar-selected-panel:target {
            display: block;
        }

        .training-calendar-day-header {
            min-height: 1rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.25rem;
            margin-bottom: 0.22rem;
            font-size: 0.78rem;
            line-height: 1;
        }

        .training-calendar-day.today
        .training-calendar-day-header strong {
            font-weight: 800;
        }

        .training-calendar-phase {
            min-width: 0;
            overflow: hidden;
            color: rgba(128, 128, 128, 0.95);
            font-size: 0.5rem;
            line-height: 1;
            text-align: right;
            text-overflow: ellipsis;
            text-transform: uppercase;
            white-space: nowrap;
        }

        .training-calendar-item {
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            justify-content: flex-start;
            gap: 0.12rem;
            min-width: 0;
            margin-top: 0.2rem;
            padding: 0.2rem 0.28rem;
            overflow: hidden;
            border-left: 3px solid;
            border-radius: 0.2rem;
            font-size: 0.62rem;
            line-height: 1.1;
        }

        .training-calendar-item-title {
            width: 100%;
            min-width: 0;
            overflow: hidden;
            font-weight: 650;
            text-align: left;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .training-calendar-item-summary {
            width: 100%;
            min-width: 0;
            overflow: hidden;
            max-width: 100%;
            font-size: 0.56rem;
            line-height: 1.1;
            opacity: 0.72;
            text-align: left;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .training-calendar-rest {
            margin-top: 0.42rem;
            color: inherit !important;
            opacity: 0.75;
            font-size: 0.64rem;
            line-height: 1.1;
            text-decoration: none !important;
        }

        .training-calendar-item.planned {
            border-color: #87909b;
            background: rgba(160, 160, 160, 0.14);
        }

        .training-calendar-item.completed {
            border-color: #39a96b;
            background: transparent;
        }

        .training-calendar-item.event {
            border-color: #e05a5a;
            background: rgba(224, 90, 90, 0.15);
            font-weight: 700;
        }

        .training-calendar-item.status-missed {
            border-left-style: dotted;
        }

        .training-calendar-item.planned.session-easy { border-color: #8bcf91; }
        .training-calendar-item.planned.session-tempo { border-color: #e4b932; }
        .training-calendar-item.planned.session-hills { border-color: #287342; }
        .training-calendar-item.planned.session-long { border-color: #a078cf; }
        .training-calendar-item.planned.session-other { border-color: #87909b; }

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
            background: #87909b;
        }
        .training-calendar-legend .session-easy::before { background: #8bcf91; }
        .training-calendar-legend .session-tempo::before { background: #e4b932; }
        .training-calendar-legend .session-hills::before { background: #287342; }
        .training-calendar-legend .session-long::before { background: #a078cf; }

        .training-calendar-legend .completed::before {
            background: #39a96b;
        }

        .training-calendar-legend .event::before {
            background: #e05a5a;
        }

        .calendar-sidebar-title {
            margin: 0;
            font-size: 0.92rem;
            font-weight: 700;
            line-height: 1.15;
        }

        .calendar-selected-date {
            margin-top: 0.35rem;
            font-size: 0.72rem;
            opacity: 0.62;
        }

        .calendar-selected-phase {
            margin-top: 0.22rem;
            font-size: 0.58rem;
            font-weight: 700;
            opacity: 0.58;
        }

        .calendar-selected-rest {
            margin-top: 0.75rem;
            font-size: 0.82rem;
            opacity: 0.45;
        }

        .calendar-selected-item {
            margin-top: 0.65rem;
            padding-top: 0.6rem;
            border-top:
                1px solid rgba(128, 128, 128, 0.18);
        }

        .calendar-selected-item-title {
            font-size: 0.82rem;
            font-weight: 700;
        }

        .calendar-selected-item-summary {
            margin-top: 0.24rem;
            font-size: 0.69rem;
            line-height: 1.3;
        }

        .calendar-selected-item-status {
            margin-top: 0.22rem;
            font-size: 0.61rem;
            opacity: 0.58;
        }

        .calendar-upcoming-events-list {
            max-height: 18rem;
            overflow-y: auto;
        }

        .calendar-upcoming-event {
            padding: 0.6rem 0;
            border-bottom:
                1px solid rgba(128, 128, 128, 0.18);
        }

        .calendar-upcoming-event:last-child {
            border-bottom: 0;
        }

        .calendar-upcoming-event-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.5rem;
        }

        .calendar-upcoming-event-name {
            min-width: 0;
            overflow: hidden;
            font-size: 0.78rem;
            font-weight: 700;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .calendar-event-priority {
            flex: 0 0 auto;
            padding: 0.1rem 0.3rem;
            border: 1px solid rgba(128, 128, 128, 0.3);
            border-radius: 0.25rem;
            font-size: 0.55rem;
            font-weight: 750;
        }

        .calendar-upcoming-event-date {
            margin-top: 0.2rem;
            font-size: 0.65rem;
        }

        .calendar-upcoming-event-details {
            margin-top: 0.14rem;
            font-size: 0.61rem;
            opacity: 0.62;
        }

        .calendar-sidebar-empty {
            margin-top: 0.65rem;
            font-size: 0.69rem;
            line-height: 1.35;
            opacity: 0.58;
        }

        .st-key-calendar-manage-events button {
            min-height: 2rem;
            padding: 0.2rem 0.4rem;
            font-size: 0.68rem;
        }

        .st-key-calendar-month-navigation .calendar-month-heading {
            font-size: 1.1rem;
            line-height: 1.3;
        }
        @media (min-width: 901px) {
            .st-key-calendar_layout [data-testid="stHorizontalBlock"]:has(.st-key-calendar_grid_area) {
                align-items: stretch;
            }
            .st-key-calendar_layout [data-testid="stHorizontalBlock"]:has(.st-key-calendar_grid_area)
            > [data-testid="stColumn"] > [data-testid="stVerticalBlock"] {
                height: 100%;
            }
            .st-key-calendar_layout [data-testid="stLayoutWrapper"] {
                flex-shrink: 0;
            }
            .st-key-calendar_layout [data-testid="stLayoutWrapper"]:has(> .st-key-calendar_events_card) {
                flex: 1 0 auto;
                display: flex;
            }
            .st-key-calendar_events_card { flex: 1; }
            .st-key-calendar_layout [data-testid="stLayoutWrapper"]:has(> .st-key-calendar_grid_area),
            .st-key-calendar_grid_area,
            .st-key-calendar_grid_area [data-testid="stElementContainer"],
            .st-key-calendar_grid_area [data-testid="stHtml"],
            .st-key-calendar_grid_area .training-calendar-scroll {
                display: flex;
                flex: 1 0 auto;
                flex-direction: column;
            }
            .st-key-calendar_grid_area .training-calendar-grid {
                flex: 1;
            }
        }
        @media (max-width: 900px) {
            .training-calendar-grid {
                min-width: 760px;
            }

            .training-calendar-scroll {
                overflow-x: auto;
            }
        }
        .stApp:has(
            .calendar-selected-panel:target
        )
        .training-calendar-day.selected {
            box-shadow: none;
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


def _show_month_navigation(
    *,
    anchor: date,
    previous_month: date,
    next_month: date,
) -> None:
    """
    Displays the month heading and grouped navigation.
    """

    with st.container(
        key="calendar-month-navigation"
    ):
        (
            heading_column,
            navigation_column,
        ) = st.columns(
            [2, 1],
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


def _show_selected_day(
    calendar,
    *,
    default_day: date,
) -> None:
    """
    Displays the locally selected calendar day.
    """

    with st.container(
        border=True, key="calendar_selected_card"
    ):
        st.markdown(
            (
                '<div class="calendar-sidebar-title">'
                "Selected day"
                "</div>"
            ),
            unsafe_allow_html=True,
        )

        st.html(
            _selected_days_html(
                calendar,
                default_day=default_day,
            )
        )


def _show_upcoming_events(
    *,
    athlete,
    events,
) -> None:
    """
    Displays events scheduled in the next six months.
    """

    with st.container(
        border=True, key="calendar_events_card"
    ):
        (
            title_column,
            action_column,
        ) = st.columns(
            [1.35, 1],
            gap="small",
            vertical_alignment="center",
        )

        with title_column:
            st.markdown(
                (
                    '<div class="calendar-sidebar-title">'
                    "Upcoming events"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )

        with action_column:
            st.button(
                "Manage Events",
                use_container_width=True,
                key="calendar-manage-events",
                on_click=lambda: open_event_manager(
                    athlete
                ),
            )

        st.html(
            _upcoming_events_html(
                events
            )
        )


def _show_calendar_export(athlete, *, reference_day: date) -> None:
    """Export the complete persistent plan, independently of the visible month."""
    plan = PlanPresenter(
        plan=athlete.training_plan,
        history=athlete.history,
    ).build(reference_day=reference_day)
    st.download_button(
        "Export calendar",
        data=_plan_calendar_ics(plan) if plan.weeks else "",
        file_name="performancelab-plan.ics",
        mime="text/calendar; charset=utf-8",
        use_container_width=True,
        disabled=not bool(plan.weeks),
        key="calendar_export",
        help="Export the complete training plan, not just the visible month.",
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

    default_selected_day = (
        today
        if (
            anchor.year == today.year
            and anchor.month == today.month
        )
        else anchor
    )

    previous_month = _shift_month(
        anchor,
        -1,
    )

    next_month = _shift_month(
        anchor,
        1,
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
        selected_day=(
            default_selected_day
        ),
    )

    with st.container(key="calendar_layout"):
        calendar_column, sidebar_column = st.columns(
            [3.4, 1], gap="medium", vertical_alignment="top",
        )
        with calendar_column:
            with st.container(key="calendar_grid_area"):
                st.html(_calendar_html(calendar, selected_day=default_selected_day))

        with sidebar_column:
            _show_month_navigation(
                anchor=anchor, previous_month=previous_month, next_month=next_month,
            )
            _show_calendar_export(athlete, reference_day=today)
            _show_selected_day(calendar, default_day=default_selected_day)
            _show_upcoming_events(athlete=athlete, events=calendar.upcoming_events)

    st.markdown(
        """
        <div class="training-calendar-legend">
            <span class="session-easy">Easy / Shakeout</span>
            <span class="session-tempo">Tempo / Intervals</span>
            <span class="session-hills">Hills</span>
            <span class="session-long">Long run</span>
            <span class="planned">Other planned workout</span>
            <span class="completed">Completed activity</span>
            <span class="event">Event</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
