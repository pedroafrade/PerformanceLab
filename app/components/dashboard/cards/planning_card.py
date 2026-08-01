"""
PerformanceLab

Planning dashboard card.
"""

from datetime import date, timedelta
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
    if distance is None:
        return None

    if float(distance).is_integer():
        return f"{int(distance)} km"

    return f"{distance:.1f} km"

def _format_elevation_gain(
    elevation_gain: float | None,
) -> str | None:

    if elevation_gain is None:
        return None

    return (
        f"{round(elevation_gain)} D+"
    )

def _planned(day) -> bool:
    return bool(day.title or day.sport)


def _completed(day) -> bool:
    return bool(day.completed)


def _day_title(day) -> str:
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
        or "Rest"
    )

_OUTCOME_LABELS = {
    "missed": "Missed",
    "equivalent": "Equivalent",
    "modified": "Modified",
    "substitute": "Substitute",
}


def _outcome_label(
    day,
) -> str | None:

    status = getattr(
        day,
        "outcome_status",
        None,
    )

    return _OUTCOME_LABELS.get(
        status
    )

def _day_details(day) -> str:
    completed_title = day.completed_title
    completed_sport = day.completed_sport

    actual_title = completed_title or completed_sport
    planned_title = day.title or day.sport

    outcome_label = (
        _outcome_label(
            day
        )
    )

    if (
        _completed(day)
        and actual_title
        and planned_title
        and actual_title.lower()
        != planned_title.lower()
    ):
        details = [
            f"Feito: {actual_title}"
        ]

        if outcome_label:
            details.insert(
                0,
                outcome_label,
            )

        return " · ".join(
            details
        )

    prescription_summary = getattr(
        day,
        "prescription_summary",
        None,
    )

    if prescription_summary:

        if outcome_label:
            return (
                f"{outcome_label} · "
                f"{prescription_summary}"
            )

        return prescription_summary

    details = []

    if outcome_label:
        details.append(
            outcome_label
        )

    distance = _format_distance(
        day.distance
    )

    elevation_gain = (
        _format_elevation_gain(
            day.elevation_gain
        )
    )

    duration = _format_duration(
        day.duration
    )

    if (
        distance
        and elevation_gain
    ):
        rounded_distance = (
            _format_distance(
                round(day.distance)
            )
        )

        details.append(
            f"{rounded_distance} · "
            f"{elevation_gain}"
        )

        return " · ".join(
            details
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
    if completed:
        marker_class = "weekly-plan-marker-completed"
        symbol = "✓"
    elif planned:
        marker_class = "weekly-plan-marker-planned"
        symbol = ""
    else:
        marker_class = "weekly-plan-marker-rest"
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
    Builds a compact single-line execution summary for the
    next workout.
    """

    if workout is None:
        return None

    structure = [
        str(step).strip()
        for step in workout.structure
        if str(step).strip()
    ]

    if not structure:
        return None

    return escape(
        " + ".join(structure)
    )

def _default_plan_day(
    planning,
):
    days = tuple(
        planning.weekly_plan.days
    )

    selected_day = next(
        (
            day
            for day in days
            if day.is_next_workout
        ),
        None,
    )

    if selected_day is None:
        selected_day = next(
            (
                day
                for day in days
                if day.is_today
            ),
            None,
        )

    if selected_day is None and days:
        selected_day = days[0]

    return selected_day


def _selected_day_description(
    day,
) -> str:
    if day is None:
        return ""

    details = []

    if day.sport:
        details.append(
            str(day.sport).strip()
        )

    guidance_prefixes = (
        "Pacing: ",
        "Hydration: ",
        "Nutrition: ",
    )

    structure = [
        str(step).strip()
        for step in day.structure
        if (
            str(step).strip()
            and not str(step).strip().startswith(
                guidance_prefixes
            )
        )
    ]

    details.extend(
        structure
    )

    if details:
        return escape(
            " · ".join(details)
        )

    if not _planned(day):
        return "Rest day."

    return escape(
        day.title
        or "Planned workout"
    )

def _race_guidance(
    day,
) -> tuple[tuple[str, str], ...]:
    """
    Extracts domain-provided race guidance from the
    selected planned day.
    """

    if day is None:
        return ()

    guidance = []

    for step in day.structure:

        text = str(
            step
        ).strip()

        for category in (
            "Pacing",
            "Hydration",
            "Nutrition",
        ):

            prefix = f"{category}: "

            if text.startswith(prefix):
                guidance.append(
                    (
                        category,
                        text[len(prefix):],
                    )
                )
                break

    return tuple(
        guidance
    )

def _phase_segments(
    timeline,
):
    """
    Groups consecutive plan days belonging to the
    same training phase.
    """

    if timeline is None:
        return ()

    segments = []

    for phase_day in timeline.days:

        phase = (
            str(
                phase_day.phase
                or "Unassigned"
            ).strip()
        )

        if (
            segments
            and segments[-1][0]
            == phase
        ):
            segments[-1][1].append(
                phase_day.day
            )

        else:
            segments.append(
                (
                    phase,
                    [
                        phase_day.day,
                    ],
                )
            )

    return tuple(
        (
            phase,
            tuple(days),
        )
        for phase, days in segments
    )

def _phase_timeline_html(
    *,
    timeline,
    current_date,
    visible_start,
    visible_end,
) -> str:
    """
    Builds the full-plan phase progression.
    """

    segments = _phase_segments(
        timeline
    )

    if not segments:
        return ""

    segment_html = []

    for phase, days in segments:

        dots = []

        for day in days:

            classes = [
                "weekly-phase-dot",
            ]

            if (
                visible_start
                <= day
                <= visible_end
            ):
                classes.append(
                    "weekly-phase-dot-visible"
                )

            if day == current_date:
                classes.append(
                    "weekly-phase-dot-current"
                )

            if phase.lower() == "race":
                classes.append(
                    "weekly-phase-dot-race"
                )

            dots.append(
                (
                    '<span class="'
                    f'{" ".join(classes)}'
                    '" title="'
                    f"{escape(phase)} · "
                    f"{day:%d %b %Y}"
                    '"></span>'
                )
            )

        segment_html.append(
            (
                '<div class="weekly-phase-segment" '
                f'style="flex:{len(days)}">'
                '<div class="weekly-phase-label">'
                f"{escape(phase)}"
                "</div>"
                '<div class="weekly-phase-dots">'
                f'{"".join(dots)}'
                "</div>"
                "</div>"
            )
        )

    return (
        '<div class="weekly-phase-timeline">'
        '<div class="weekly-phase-segments">'
        f'{"".join(segment_html)}'
        "</div>"
        "</div>"
    )

def _planning_window_center() -> date:
    """
    Return the date at the centre of the planning viewport.
    """

    center_date = st.session_state.get(
        "planning_window_center_date"
    )

    if not isinstance(center_date, date):
        center_date = date.today()
        st.session_state[
            "planning_window_center_date"
        ] = center_date

    return center_date


def _move_planning_window(days: int) -> None:
    """
    Move the viewport without regenerating the training plan.
    """

    st.session_state[
        "planning_window_animation_direction"
    ] = (
        "next"
        if days > 0
        else "previous"
    )

    st.session_state[
        "planning_window_center_date"
    ] = (
        _planning_window_center()
        + timedelta(days=days)
    )


def _show_previous_button() -> None:
    """
    Display the button that moves the viewport three days back.
    """

    st.markdown(
        '<div class="weekly-plan-arrow-spacer"></div>',
        unsafe_allow_html=True,
    )

    if st.button(
        "‹",
        key="planning_window_previous",
        type="tertiary",
        use_container_width=True,
    ):
        _move_planning_window(-3)
        st.rerun()


def _show_next_button() -> None:
    """
    Display the button that moves the viewport three days forward.
    """

    st.markdown(
        '<div class="weekly-plan-arrow-spacer"></div>',
        unsafe_allow_html=True,
    )

    if st.button(
        "›",
        key="planning_window_next",
        type="tertiary",
        use_container_width=True,
    ):
        _move_planning_window(3)
        st.rerun()


def show_planning_card(
    planning,
) -> None:
    """
    Display a compact horizontal seven-day plan.
    """

    if planning is None:
        st.info("No planning available.")
        return

    animation_direction = (
        st.session_state.pop(
            "planning_window_animation_direction",
            None,
        )
    )

    animation_name = {
        "next": "weekly-plan-slide-left",
        "previous": "weekly-plan-slide-right",
    }.get(
        animation_direction
    )

    st.markdown(
        """
<style>

.weekly-phase-timeline {
    margin: -7px 0 8px 0;
}

.weekly-phase-segments {
    display: flex;
    align-items: flex-end;
    width: 100%;
    gap: 8px;
}

.weekly-phase-segment {
    min-width: 0;
    padding: 0 2px;
    text-align: center;
}

.weekly-phase-label {
    margin-bottom: 2px;
    overflow: hidden;
    font-size: 0.60rem;
    font-weight: 600;
    line-height: 1;
    opacity: 0.68;
    text-overflow: ellipsis;
    text-transform: capitalize;
    white-space: nowrap;
}

.weekly-phase-dots {
    display: flex;
    align-items: center;
    justify-content: space-around;
    min-height: 8px;
    gap: 1px;
}

.weekly-phase-dot {
    display: inline-block;
    flex: 0 0 auto;
    width: 5px;
    height: 5px;
    border: 1px solid currentColor;
    border-radius: 50%;
    opacity: 0.22;
    box-sizing: border-box;
}

.weekly-phase-dot-visible {
    opacity: 0.72;
}

.weekly-phase-dot-current {
    width: 7px;
    height: 7px;
    border-width: 2px;
    background: currentColor;
    opacity: 1;
}

.weekly-phase-dot-race {
    width: 7px;
    height: 7px;
    border-width: 2px;
    opacity: 0.85;
}

.weekly-phase-dot-race.weekly-phase-dot-current {
    width: 9px;
    height: 9px;
    opacity: 1;
}

.weekly-plan-day {
    min-height: 78px;
    padding: 1px 2px;
    border: 1px solid transparent;
    border-radius: 8px;
    text-align: center;
    box-sizing: border-box;
}

.weekly-plan-day-today {
    border-color: rgba(128, 128, 128, 0.55);
}

.weekly-plan-day-selected {
    border-color: currentColor;
    border-width: 2px;
}

.weekly-plan-weekday {
    font-size: 0.74rem;
    font-weight: 700;
    text-transform: lowercase;
}

.weekly-plan-date {
    margin-left: 3px;
    font-size: 0.64rem;
    font-weight: 400;
    opacity: 0.55;
}

.weekly-plan-marker {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 25px;
    height: 25px;
    margin: 2px auto;
    border-radius: 50%;
    box-sizing: border-box;
    font-size: 0.82rem;
    font-weight: 800;
    line-height: 1;
}

.weekly-plan-marker-rest {
    border: 1.5px solid rgba(128, 128, 128, 0.55);
}

.weekly-plan-marker-planned,
.weekly-plan-marker-completed {
    border: 2.5px solid currentColor;
}

.weekly-plan-title {
    min-height: 17px;
    overflow-wrap: anywhere;
    font-size: 0.72rem;
    font-weight: 600;
    line-height: 1.12;
}

.weekly-plan-details {
    min-height: 14px;
    margin-top: 2px;
    overflow-wrap: anywhere;
    font-size: 0.62rem;
    line-height: 1.12;
    opacity: 0.62;
}

.weekly-plan-next {
    margin-top: 0;
    padding-top: 3px;
    overflow: visible;
    overflow-wrap: anywhere;
    border-top: 1px solid rgba(128, 128, 128, 0.30);
    font-size: 0.68rem;
    line-height: 1.18;
    opacity: 0.72;
    text-overflow: clip;
    white-space: normal;
}

.weekly-plan-arrow-spacer {
    height: 2px;
}

/*
The navigation columns contain only these tertiary buttons.
Their height matches the 29 px day markers.
*/
div[data-testid="stButton"] > button[kind="tertiary"] {
    min-height: 25px;
    height: 25px;
    padding: 0;
    border: 0;
    background: transparent;
    box-shadow: none;
    font-size: 1.35rem;
    line-height: 1;
}

div[data-testid="stButton"] > button[kind="tertiary"]:hover,
div[data-testid="stButton"] > button[kind="tertiary"]:focus,
div[data-testid="stButton"] > button[kind="tertiary"]:active {
    border: 0;
    background: transparent;
    box-shadow: none;
}

div[class*="st-key-weekly_plan_selector_"] {
    margin-bottom: -8px;
}

div[class*="st-key-weekly_plan_selector_"] button {
    min-height: 24px;
    height: 24px;
    padding: 0 0.30rem;
    font-size: 0.68rem;
    line-height: 1;
}
</style>
        """,
        unsafe_allow_html=True,
    )

    if animation_name is not None:

        st.markdown(
            f"""
<style>
@keyframes {animation_name} {{
    from {{
        opacity: 0.20;
    }}

    to {{
        opacity: 1;
    }}
}}

.weekly-phase-timeline,
.weekly-plan-day,
.weekly-plan-next,
div[class*="st-key-weekly_plan_selector_"] {{
    animation: {animation_name}
        380ms cubic-bezier(
            0.22,
            1,
            0.36,
            1
        ) both;
}}
</style>
            """,
            unsafe_allow_html=True,
        )

    days = tuple(
        planning.weekly_plan.days
    )

    days = tuple(
        planning.weekly_plan.days
    )

    default_day = _default_plan_day(
        planning
    )

    day_by_date = {
        day.day: day
        for day in days
    }

    selector_key = (
        "weekly_plan_selector_"
        f"{planning.weekly_plan.start_date}"
        "_"
        f"{planning.weekly_plan.end_date}"
    )

    selected_date = (
        st.session_state.get(
            selector_key
        )
    )

    if selected_date not in day_by_date:

        selected_date = (
            default_day.day
            if default_day is not None
            else next(
                iter(day_by_date),
                None,
            )
        )

    timeline_html = (
        _phase_timeline_html(
            timeline=(
                planning.phase_timeline
            ),
            current_date=date.today(),
            visible_start=(
                planning.weekly_plan.start_date
            ),
            visible_end=(
                planning.weekly_plan.end_date
            ),
        )
    )

    if timeline_html:

        timeline_columns = st.columns(
            [
                0.42,
                7,
                0.42,
            ],
            gap="small",
        )

        with timeline_columns[1]:

            st.markdown(
                timeline_html,
                unsafe_allow_html=True,
            )

    selector_columns = st.columns(
        [
            0.42,
            7,
            0.42,
        ],
        gap="small",
    )

    with selector_columns[1]:

        selected_date = st.segmented_control(
            "Workout details",
            options=tuple(day_by_date),
            default=selected_date,
            required=True,
            format_func=lambda day: str(
                day.day
            ),
            key=selector_key,
            label_visibility="collapsed",
            width="stretch",
        )

    selected_day = day_by_date.get(
        selected_date
    )
    
    columns = st.columns(
        [
            0.55,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            0.55,
        ],
        gap="small",
    )

    previous_column = columns[0]
    day_columns = columns[1:-1]
    next_column = columns[-1]

    with previous_column:
        _show_previous_button()

    for column, day in zip(
        day_columns,
        planning.weekly_plan.days,
    ):
        classes = [
            "weekly-plan-day",
        ]

        if day.is_today:
            classes.append(
                "weekly-plan-day-today"
            )

        if day.day == selected_date:
            classes.append(
                "weekly-plan-day-selected"
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

    with next_column:
        _show_next_button()

    selected_description = (
        _selected_day_description(
            selected_day
        )
    )

    race_guidance = _race_guidance(
        selected_day
    )

    if (
        selected_description
        and race_guidance
    ):

        description_column, strategy_column = (
            st.columns(
                [
                    6,
                    1.35,
                ],
                gap="small",
                vertical_alignment="center",
            )
        )

        with description_column:

            st.markdown(
                (
                    '<div class="weekly-plan-next">'
                    f"{selected_description}"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )

        with strategy_column:

            with st.popover(
                "Race strategy",
                width="stretch",
            ):

                current_category = None

                for category, guidance in (
                    race_guidance
                ):

                    if (
                        category
                        != current_category
                    ):
                        st.markdown(
                            f"**{category}**"
                        )

                        current_category = (
                            category
                        )

                    st.caption(
                        guidance
                    )

    elif selected_description:

        st.markdown(
            (
                '<div class="weekly-plan-next">'
                f"{selected_description}"
                "</div>"
            ),
            unsafe_allow_html=True,
        )