"""
PerformanceLab

Activities page.
"""

from datetime import (
    date,
    datetime,
    timedelta,
)
from html import escape
from calendar import monthrange

import streamlit as st

from performancelab import (
    activity_coach_context_hash,
    synchronize_vo2max_observation_from_notes,
)
from performancelab.coaching import (
    ActivityCoachResolutionStatus,
)

from performancelab.presentation import (
    ActivitiesPresenter,
    ActivityFilters,
    ActivityCoachPresenter,
    build_activity_coach_disclosure,
    build_activity_coach_prompt_payload,
    sensor_summary,
)
from .activity_analysis import (
    show_activity_analysis,
)
from .training_coach_consent import (
    show_training_coach_consent_dialog,
)
from .workout_editor import (
    show_workout_editor,
)

from .workout_table import (
    format_distance,
    format_duration,
    format_elevation,
    format_workout_date,
    format_workout_start_time,
)


_PERIOD_OPTIONS = (
    "All time",
    "Last 30 days",
    "Last 90 days",
    "This year",
)


_OUTCOME_OPTIONS = (
    "All results",
    "Equivalent",
    "Modified",
    "Substitute",
    "Unplanned",
    "Outside plan",
)

def _outcome_label(
    status: str | None,
) -> str:
    """
    Returns a readable plan-result label.
    """

    if status is None:
        return "Not assessed"

    return (
        status
        .replace("_", " ")
        .title()
    )

def _activity_date_label(
    value,
) -> str:
    """
    Formats the calendar date used in activity lists
    without exposing an exact workout start time.
    """

    if isinstance(
        value,
        datetime,
    ):
        value = value.date()

    return format_workout_date(
        value
    )

def _rpe_label(value) -> str:
    """Round RPE for display only; retain the original feedback for calculations."""
    return f"{value:.0f}" if value is not None else "—"


def _activity_rows(
    activities,
    *,
    history=None,
) -> list[dict]:
    """
    Converts activity presentation data into table rows.
    """

    return [
        {
            "Date": _activity_date_label(
                activity.workout_date
            ),
            "Activity": activity.title,
            "Sport": activity.sport,
            "Analysis": (
                _analysis_available(
                    history,
                    activity,
                )
                if history is not None
                else "—"
            ),
            "Distance": format_distance(
                activity.distance
            ),
            "Duration": format_duration(
                activity.duration
            ),
            "Elevation": format_elevation(
                activity.elevation_gain
            ),
            "RPE": (
                round(activity.rpe)
                if activity.rpe is not None
                else "—"
            ),
            "Plan result": (
                _outcome_label(
                    activity.outcome_status
                )
            ),
            "Planned": (
                activity.planned_title
                or "—"
            ),
        }
        for activity in activities
    ]


def _total_duration(
    activities,
) -> timedelta:
    """
    Returns the accumulated duration of the activities.
    """

    return sum(
        (
            activity.duration
            or timedelta()
            for activity in activities
        ),
        timedelta(),
    )



def _format_load(
    value: float | None,
    *,
    signed: bool = False,
) -> str:
    """
    Formats session-RPE load in arbitrary units.
    """

    if value is None:
        return "—"

    if signed:
        return f"{value:+.0f} AU"

    return f"{value:.0f} AU"


def _outcome_filter_value(
    label: str,
) -> str | None:
    """
    Converts the visible outcome label into a filter value.
    """

    if label == "All results":
        return None

    return (
        label
        .casefold()
        .replace(" ", "_")
    )

def _period_start_date(
    period: str,
    *,
    reference_day: date,
) -> date | None:
    """
    Converts a visible period option into a start date.
    """

    if period == "Last 30 days":

        return reference_day - timedelta(
            days=29
        )

    if period == "Last 90 days":

        return reference_day - timedelta(
            days=89
        )

    if period == "This year":

        return reference_day.replace(
            month=1,
            day=1,
        )

    return None


def _workout_for_activity(
    history,
    activity,
):
    """
    Resolves a presentation item to its domain workout.
    """

    for workout in history:

        if (
            str(workout.workout_id)
            == activity.workout_id
        ):
            return workout

    return None

def _analysis_available(
    history,
    activity,
) -> str:
    """
    Indicates whether the complete workout contains
    GPS and detailed sensor streams.
    """

    workout = (
        _workout_for_activity(
            history,
            activity,
        )
    )

    if workout is None:
        return "—"

    has_gps = bool(
        workout.sensors.get(
            "gps"
        )
    )

    has_performance = any(
        bool(
            workout.sensors.get(
                sensor
            )
        )
        for sensor in (
            "heart_rate",
            "power",
            "cadence",
        )
    )

    if (
        has_gps
        and has_performance
    ):
        return "Route + sensors"

    if has_gps:
        return "Route"

    if has_performance:
        return "Sensors"

    return "Basic"



def _apply_activities_page_styles() -> None:
    """
    Keeps Activities within the viewport and turns the
    history into one compact internally scrolling panel.
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

        .activities-page-header {
            margin: 0 0 0.55rem 0;
            padding: 0;
        }

        .activities-page-title {
            margin: 0;
            font-size: 2.25rem;
            font-weight: 750;
            line-height: 1.05;
        }

        .activities-page-subtitle {
            margin-top: 0.32rem;
            font-size: 0.76rem;
            line-height: 1.15;
            opacity: 0.58;
        }

        .activities-section-heading {
            margin: 0 0 0.08rem 0;
            font-size: 1.25rem;
            font-weight: 700;
            line-height: 1.1;
        }

        .activities-section-copy {
            margin-bottom: 0.38rem;
            font-size: 0.68rem;
            line-height: 1.2;
            opacity: 0.58;
        }

        /* =================================================
           Scrollable activity browser
           ================================================= */

        .st-key-activities_browser {
            border-color:
                rgba(128, 128, 128, 0.22) !important;
            border-radius: 0.6rem !important;
        }

        .st-key-activities_browser
        div[data-testid="stVerticalBlock"] {
            gap: 0 !important;
        }

        .st-key-activities_browser
        div[data-testid="stElementContainer"] {
            margin-top: 0 !important;
            margin-bottom: 0 !important;
        }

        /*
        Activity rows use a real visual grid with one
        transparent button covering the complete row.
        */
        div[class*="st-key-activity_grid_row_"] {
            position: relative;
            min-height: 2.05rem;
            margin: 0 !important;
            padding: 0 !important;

            border-bottom:
                1px solid
                rgba(128, 128, 128, 0.15);
        }

        div[class*="st-key-activity_grid_row_"]
        > div[data-testid="stVerticalBlock"] {
            gap: 0 !important;
        }

        div[class*="st-key-activity_grid_row_"]
        div[data-testid="stElementContainer"] {
            margin: 0 !important;
            padding: 0 !important;
        }

        .activity-row-grid {
            display: grid;
            grid-template-columns:
                minmax(6.4rem, 0.9fr)
                minmax(5.5rem, 0.8fr)
                minmax(10rem, 2fr)
                minmax(5rem, 0.75fr)
                minmax(4.5rem, 0.7fr)
                minmax(4.2rem, 0.65fr)
                minmax(4.2rem, 0.65fr)
                minmax(6.8rem, 1fr);

            column-gap:
                clamp(0.45rem, 1.2vw, 1rem);

            align-items: center;

            width: 100%;
            min-height: 2.05rem;
            padding: 0.08rem 0.65rem;

            box-sizing: border-box;

            font-family: inherit;
            font-size: 0.88rem;
            font-weight: 720;
            line-height: 1.1;

            background: transparent;
            pointer-events: none;
        }

        .activity-row-grid.is-selected {
            padding-left: calc(
                0.65rem - 2px
            );

            border-left:
                2px solid #ff4b4b;

            background:
                rgba(255, 75, 75, 0.065);
        }

        .activity-row-cell {
            min-width: 0;
            overflow: hidden;

            text-align: left;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .activity-row-numeric {
            text-align: right;
        }

        .activity-row-result {
            text-align: right;
        }

        div[class*="st-key-activity_grid_row_"] div[data-testid="stElementContainer"]:has(div[data-testid="stButton"]) {
            position: absolute !important;
            inset: 0 !important;
            z-index: 2;

            width: 100% !important;
            height: 100% !important;
        }

        div[class*="st-key-activity_grid_row_"]
        div[data-testid="stButton"] {
            width: 100% !important;
            height: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        div[class*="st-key-activity_grid_row_"]
        div[data-testid="stButton"] > button {
            width: 100% !important;
            height: 100% !important;
            min-height: 2.05rem !important;
            margin: 0 !important;
            padding: 0 !important;

            border: 0 !important;
            border-radius: 0 !important;
            background: transparent !important;
            box-shadow: none !important;

            cursor: pointer;
            opacity: 0;
        }

        div[class*="st-key-activity_grid_row_"]
        :has(button:hover)
        .activity-row-grid {
            background:
                rgba(128, 128, 128, 0.055);
        }

        div[class*="st-key-activity_grid_row_"]
        :has(button:focus-visible) {
            outline:
                1px solid rgba(255, 75, 75, 0.55);
            outline-offset: -1px;
        }

        @media (max-width: 1200px) {
            .activity-row-grid {
                grid-template-columns:
                    minmax(5.8rem, 0.9fr)
                    minmax(4.8rem, 0.75fr)
                    minmax(8rem, 1.7fr)
                    minmax(4.5rem, 0.7fr)
                    minmax(4rem, 0.65fr)
                    minmax(3.8rem, 0.6fr)
                    minmax(3.8rem, 0.6fr)
                    minmax(6rem, 1fr);

                column-gap: 0.4rem;
                font-size: 0.74rem;
            }
        }

        /* =================================================
           Expanded activity
           ================================================= */

        .activities-metrics-grid {
            display: grid;
            grid-template-columns:
                repeat(8, minmax(0, 1fr));
            gap: 0;
            margin: 0;
            padding: 0.34rem 0.55rem;
            border-bottom:
                1px solid rgba(128, 128, 128, 0.16);
        }

        .activities-metric {
            min-width: 0;
            padding: 0.2rem 0.42rem;
            border-right:
                1px solid rgba(128, 128, 128, 0.13);
        }

        .activities-metric:nth-child(8n) {
            border-right: 0;
        }

        .activities-metric-label {
            overflow: hidden;
            margin-bottom: 0.08rem;
            font-size: 0.58rem;
            line-height: 1.1;
            opacity: 0.58;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .activities-metric-value {
            overflow: hidden;
            font-size: 0.76rem;
            font-weight: 680;
            line-height: 1.15;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        @media (max-width: 1200px) {
            .activities-metrics-grid {
                grid-template-columns:
                    repeat(4, minmax(0, 1fr));
            }

            .activities-metric:nth-child(8n) {
                border-right:
                    1px solid rgba(128, 128, 128, 0.13);
            }

            .activities-metric:nth-child(4n) {
                border-right: 0;
            }
        }
        .st-key-activities_browser
        div[data-testid="stMetric"] {
            padding: 0.18rem 0 !important;
        }

        .st-key-activities_browser
        div[data-testid="stMetricLabel"] {
            font-size: 0.62rem !important;
        }

        .st-key-activities_browser
        div[data-testid="stMetricValue"] {
            font-size: 0.9rem !important;
        }

        .st-key-activities_browser
        div[data-testid="stTabs"] {
            margin-top: 0.1rem;
        }

        .st-key-activities_browser
        button[data-baseweb="tab"] {
            min-height: 1.8rem !important;
            padding-top: 0.15rem !important;
            padding-bottom: 0.15rem !important;
            font-size: 0.7rem !important;
        }

        /* =================================================
           Right utility cards
           ================================================= */

        .activities-coach-header {
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            gap: 0.75rem;
            margin-bottom: 0.35rem;
        }

        .activities-coach-heading {
            flex: 0 0 auto;
            font-size: 0.95rem;
            font-weight: 700;
            line-height: 1.2;
        }

        .st-key-activity_coach_card
        div[data-testid="stMarkdownContainer"] p {
            font-size: 0.86rem;
            line-height: 1.45;
        }

        /* Three explicit rows fill the 234px inside the 268px bordered slot.
           Scope this to the notes block, never to nested widget containers. */
        [data-testid="stVerticalBlock"].st-key-activity_coach_notes {
            display: grid !important;
            grid-template-columns: minmax(0, 1fr);
            grid-template-rows: 24px 152px 34px;
            width: 100% !important;
            row-gap: 12px !important;
            align-content: start;
        }

        .st-key-activity_coach_notes > div {
            width: 100% !important;
            min-width: 0 !important;
            justify-self: stretch;
            margin: 0 !important;
            min-height: 0;
        }

        .st-key-activity_coach_notes > div:first-child {
            align-self: center;
        }

        .st-key-activity_coach_notes
        div[data-testid="stMarkdownContainer"] p {
            margin: 0;
            font-size: 0.82rem;
            line-height: 1.2;
        }

        .st-key-activity_coach_notes
        textarea {
            line-height: 1.5;
            padding: 0.75rem;
        }

        .st-key-activity_coach_notes
        div[data-testid="stButton"] > button {
            height: 34px;
            min-height: 34px;
            padding-top: 0.25rem;
            padding-bottom: 0.25rem;
        }

        @media (min-width: 1100px) {
            .st-key-activities_utility {
                gap: 0.75rem;
            }
            .st-key-activities_utility > [data-testid="stLayoutWrapper"] {
                flex-shrink: 0;
            }
        }
        @media (max-width: 1099px) {
            .st-key-activities_bottom_slot {
                height: auto !important;
                max-height: none !important;
                overflow: visible !important;
            }
        }
        .activities-summary-grid {
            display: grid;
            grid-template-columns:
                repeat(2, minmax(0, 1fr));
            gap: 0.42rem;
        }

        .activities-summary-item {
            padding: 0.52rem 0.58rem;
            border:
                1px solid rgba(128, 128, 128, 0.18);
            border-radius: 0.5rem;
            box-sizing: border-box;
        }

        .activities-summary-label {
            margin-bottom: 0.08rem;
            font-size: 0.6rem;
            opacity: 0.55;
        }

        .activities-summary-value {
            font-size: 0.92rem;
            font-weight: 720;
            line-height: 1.05;
        }

        @media (max-width: 900px) {
            .activities-summary-grid {
                grid-template-columns: 1fr;
            }
        }
        </style>

        <div class="activities-page-header">
            <div class="activities-page-title">
                Activities
            </div>
            <div class="activities-page-subtitle">
                Completed training, route analysis
                and performance progression.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def _activity_row_html(
    activity,
    *,
    selected: bool = False,
) -> str:
    """
    Builds one visual activity grid below a transparent
    full-row selection button.
    """

    row_class = (
        "activity-row-grid is-selected"
        if selected
        else "activity-row-grid"
    )

    date_label = _activity_date_label(
        activity.workout_date
    )

    sport_label = (
        activity.sport
        or "—"
    )

    title_label = (
        activity.title
        or "Activity"
    )

    distance_label = format_distance(
        activity.distance
    )

    duration_label = format_duration(
        activity.duration
    )

    elevation_label = format_elevation(
        activity.elevation_gain
    )

    rpe_label = (
        f"RPE {_rpe_label(activity.rpe)}"
        if activity.rpe is not None
        else "—"
    )

    result_label = _outcome_label(
        activity.outcome_status
    )

    cells = (
        (
            "date",
            date_label,
        ),
        (
            "sport",
            sport_label,
        ),
        (
            "title",
            title_label,
        ),
        (
            "distance numeric",
            distance_label,
        ),
        (
            "duration numeric",
            duration_label,
        ),
        (
            "elevation numeric",
            elevation_label,
        ),
        (
            "rpe numeric",
            rpe_label,
        ),
        (
            "result",
            result_label,
        ),
    )

    content = "".join(
        (
            '<div class="activity-row-cell '
            f'activity-row-{css_class}">'
            f"{escape(str(value))}"
            "</div>"
        )
        for css_class, value
        in cells
    )

    return (
        f'<div class="{row_class}">'
        f"{content}"
        "</div>"
    )

_SUMMARY_PERIODS = ("All time", "1 year", "6 months", "1 month", "This year")


def _summary_start_date(period, *, reference_day):
    if period == "All time":
        return None
    if period == "This year":
        return date(reference_day.year, 1, 1)
    months = {"1 year": 12, "6 months": 6, "1 month": 1}[period]
    year, month_index = divmod(reference_day.year * 12 + reference_day.month - 1 - months, 12)
    month = month_index + 1
    return date(year, month, min(reference_day.day, monthrange(year, month)[1]))


def _summary_sport(activity):
    return str(activity.sport or "").strip() or "Unknown sport"


def _summary_activities(activities, *, period, sport, reference_day):
    start = _summary_start_date(period, reference_day=reference_day)
    selected = []
    for activity in activities:
        day = activity.workout_date
        if isinstance(day, datetime):
            day = day.date()
        if not isinstance(day, date) or day > reference_day:
            continue
        if start is not None and day < start:
            continue
        if sport is not None and _summary_sport(activity) != sport:
            continue
        selected.append(activity)
    return tuple(selected)


def _summary_totals(activities):
    """Sum available measurements without treating wholly unknown totals as zero."""
    activities = tuple(activities)
    totals = {"count": len(activities), "partial": False}
    for field in ("duration", "distance", "elevation_gain"):
        values = [getattr(activity, field) for activity in activities
                  if getattr(activity, field) is not None]
        zero = timedelta() if field == "duration" else 0.0
        totals[field] = sum(values, zero) if values or not activities else None
        totals["partial"] |= len(values) != len(activities)
    return totals


def _activities_summary_html(*, activities) -> str:
    totals = _summary_totals(activities)
    items = (
        ("Activities", str(totals["count"])),
        ("Total duration", format_duration(totals["duration"])),
        ("Total distance", format_distance(totals["distance"])),
        ("Total elevation gain", format_elevation(totals["elevation_gain"])),
    )

    content = "".join(
        (
            '<div class="activities-summary-item">'
            '<div class="activities-summary-label">'
            f"{label}"
            "</div>"
            '<div class="activities-summary-value">'
            f"{value}"
            "</div>"
            "</div>"
        )
        for label, value in items
    )

    return (
        '<div class="activities-summary-grid">'
        f"{content}"
        "</div>"
    )


def _show_activity_summary(all_activities, *, reference_day, show_title=True):
    """Summary controls use independent session keys, not browser filters."""
    with st.container(border=False, key="activities_summary_card"):
        if show_title:
            st.markdown("**Activities Summary**")
        sports = [None] + sorted({_summary_sport(a) for a in all_activities}, key=str.casefold)
        if st.session_state.get("activities_summary_period", "1 month") not in _SUMMARY_PERIODS:
            st.session_state["activities_summary_period"] = "1 month"
        if st.session_state.get("activities_summary_sport") not in sports:
            st.session_state["activities_summary_sport"] = None
        period_col, sport_col = st.columns(2, gap="small")
        with period_col:
            period = st.selectbox("Summary period", _SUMMARY_PERIODS, index=3,
                                  key="activities_summary_period")
        with sport_col:
            sport = st.selectbox("Summary sport", sports,
                                 format_func=lambda value: "All sports" if value is None else value,
                                 key="activities_summary_sport")
        selected = _summary_activities(all_activities, period=period, sport=sport,
                                       reference_day=reference_day)
        st.html(_activities_summary_html(activities=selected))
        if not selected:
            st.caption("No activities in this period for this selection.")
        elif _summary_totals(selected)["partial"]:
            st.caption("Some measurements are missing; totals include available values only.")


def _sensor_summary_label(
    workout,
    sensor_name: str,
    *,
    suffix: str,
) -> str:
    """
    Formats the average and maximum of one sensor.
    """

    summary = sensor_summary(
        workout,
        sensor_name,
    )

    average = summary["average"]
    maximum = summary["maximum"]

    if (
        average is None
        and maximum is None
    ):
        return "—"

    if maximum is None:
        return (
            f"{average:.0f} {suffix}"
        )

    if average is None:
        return (
            f"— / {maximum:.0f} {suffix}"
        )

    return (
        f"{average:.0f} / "
        f"{maximum:.0f} {suffix}"
    )


def _environment_metric_label(
    value,
    *,
    suffix: str = "",
    decimals: int = 0,
) -> str:
    """
    Formats one optional environment measurement.
    """

    if value is None:
        return "—"

    if isinstance(
        value,
        (int, float),
    ) and not isinstance(
        value,
        bool,
    ):
        return (
            f"{value:.{decimals}f}"
            f"{suffix}"
        )

    return str(value)

def _vo2max_metric_label(
    observation,
) -> str:
    """
    Formats one factual VO2max observation.
    """

    if observation is None:

        return "—"

    return (
        f"{observation.value:.1f} "
        "ml/kg/min"
    )



def _compact_activity_metrics_html(
    *,
    activity,
    workout,
    vo2max_observation=None,
) -> str:
    """
    Builds one uniform metrics grid above the route map.
    """

    normalized_sport = str(
        activity.sport or ""
    ).strip().casefold()

    is_cycling = any(
        token in normalized_sport
        for token in (
            "cycl",
            "bike",
            "bicycle",
        )
    )

    cadence_unit = (
        "rpm"
        if is_cycling
        else "spm"
    )

    effective_rpe = (
        workout.feedback.effective_rpe
    )

    environment = workout.environment

    metrics = (
        (
            "Start time",
            format_workout_start_time(
                workout.date
            ),
        ),
        (
            "Distance",
            format_distance(
                activity.distance
            ),
        ),
        (
            "Duration",
            format_duration(
                activity.duration
            ),
        ),
        (
            "Elevation",
            format_elevation(
                activity.elevation_gain
            ),
        ),
        (
            "RPE",
            (
                _rpe_label(effective_rpe)
                if effective_rpe is not None
                else "—"
            ),
        ),
        (
            "HR avg / max",
            _sensor_summary_label(
                workout,
                "heart_rate",
                suffix="bpm",
            ),
        ),
        (
            "Power avg / max",
            _sensor_summary_label(
                workout,
                "power",
                suffix="W",
            ),
        ),
        (
            "Cadence avg / max",
            _sensor_summary_label(
                workout,
                "cadence",
                suffix=cadence_unit,
            ),
        ),
        (
            "Planned load",
            _format_load(
                activity.planned_load
            ),
        ),
        (
            "Completed load",
            _format_load(
                activity.completed_load
            ),
        ),
        (
            "Δ load",
            _format_load(
                activity.load_difference,
                signed=True,
            ),
        ),
        (
            "Air temperature",
            _environment_metric_label(
                environment.temperature,
                suffix=" °C",
                decimals=1,
            ),
        ),
        (
            "Humidity",
            _environment_metric_label(
                environment.humidity,
                suffix="%",
            ),
        ),
        (
            "Terrain",
            (
                environment.terrain
                or "—"
            ),
        ),
        (
            "Plan result",
            _outcome_label(
                activity.outcome_status
            ),
        ),
        (
            "VO₂max",
            _vo2max_metric_label(
                vo2max_observation
            ),
        ),
    )

    content = "".join(
        (
            '<div class="activities-metric">'
            '<div class="activities-metric-label">'
            f"{escape(str(label))}"
            "</div>"
            '<div class="activities-metric-value">'
            f"{escape(str(value))}"
            "</div>"
            "</div>"
        )
        for label, value
        in metrics
    )

    return (
        '<div class="activities-metrics-grid">'
        f"{content}"
        "</div>"
    )

def _show_selected_activity_dashboard(
    *,
    activity,
    workout,
    athlete,
    on_update_workout,
    on_delete_workouts,
) -> None:
    """
    Compact dashboard rendered inside the scrolling
    activity browser itself.
    """

    vo2max_observation = (
        athlete.vo2max_observations
        .find_for_workout(
            workout.workout_id
        )
    )

    st.html(
        _compact_activity_metrics_html(
            activity=activity,
            workout=workout,
            vo2max_observation=(
                vo2max_observation
            ),
        )
    )

    show_activity_analysis(
        workout,
        history=athlete.history,
        key_prefix=(
            "activities_inline_"
            f"{activity.workout_id}"
        ),
        show_heading=False,
        compact=True,
        environment_first=False,
    )
    show_workout_editor(
        workout,
        on_update_workout=(
            on_update_workout
        ),
        on_delete_workouts=(
            on_delete_workouts
        ),
        key_prefix=(
            "activities_inline_editor_"
            f"{activity.workout_id}"
        ),
    )

def _save_activity_coach_notes(
    *,
    athlete,
    workout,
    state_key: str,
) -> None:
    """
    Routes athlete-entered notes to the workout domain and
    synchronizes an explicit VO2max observation.
    """

    notes = st.session_state.get(
        state_key,
        "",
    )

    notes_changed = (
        workout.feedback.record_notes(
            notes
        )
    )

    vo2max_changed = (
        synchronize_vo2max_observation_from_notes(
            observations=(
                athlete.vo2max_observations
            ),
            notes=notes,
            observed_at=workout.date,
            workout_id=workout.workout_id,
        )
    )

    if (
        notes_changed
        or vo2max_changed
    ):
        st.session_state[
            "activity_coach_notes_changed"
        ] = True

def _activity_coach_material(
    *,
    activity,
    workout,
    athlete,
):
    """
    Build the current payload and find a saved interpretation.

    An exact context match is preferred. If the context changed,
    the latest saved interpretation remains available but is
    explicitly marked as belonging to an earlier context.
    """

    assessment = (
        ActivityCoachPresenter(
            activity=activity,
            workout=workout,
            athlete=athlete,
        ).build()
    )

    payload = (
        build_activity_coach_prompt_payload(
            assessment
        )
    )

    contract_version = payload[
        "contract_version"
    ]

    context_hash = (
        activity_coach_context_hash(
            payload
        )
    )

    stored = (
        athlete
        .activity_coach_interpretations
        .find(
            workout_id=(
                activity.workout_id
            ),
            contract_version=(
                contract_version
            ),
            context_hash=(
                context_hash
            ),
        )
    )

    stored_matches_current_context = (
        stored is not None
    )

    if stored is None:

        stored = (
            athlete
            .activity_coach_interpretations
            .latest_for_workout(
                workout_id=(
                    activity.workout_id
                )
            )
        )

    return (
        payload,
        stored,
        stored_matches_current_context,
    )

def _activity_coach_display_text(
    value: str,
) -> str:
    """
    Converts escaped line breaks into real line breaks
    when presenting saved Training Coach text.
    """

    return (
        value
        .replace(
            "\\r\\n",
            "\n",
        )
        .replace(
            "\\n",
            "\n",
        )
        .strip()
    )


def _show_activity_coach_narrative(
    narrative,
    *,
    stale: bool = False,
) -> None:
    """
    Presents the generated interpretation compactly.
    """

    st.markdown(
        _activity_coach_display_text(
            narrative.prudent_interpretation
        )
    )

    st.markdown(
        "**Next training**"
    )

    st.markdown(
        _activity_coach_display_text(
            narrative.recommendations
        )
    )

    with st.expander(
        "Evidence and limitations",
        expanded=False,
    ):

        st.markdown(
            "**Measured facts**"
        )

        st.markdown(
            _activity_coach_display_text(
                narrative.measured_facts
            )
        )

        st.markdown(
            "**Deterministic signals**"
        )

        st.markdown(
            _activity_coach_display_text(
                narrative.deterministic_signals
            )
        )

        st.markdown(
            "**Data limitations**"
        )

        st.markdown(
            _activity_coach_display_text(
                narrative.data_limitations
            )
        )

    st.caption(
        (
            f"Generated by "
            f"{narrative.provider} · "
            f"{narrative.model}"
        )
    )

    if stale:
        st.caption(
            "This saved interpretation was generated from an earlier "
            "version of the activity context. Regenerate it to include "
            "the current information."
        )

def _training_coach_error_message(
    error_code: str | None,
) -> str:
    """
    Return a safe explanation without exposing provider
    exceptions or credentials.
    """

    messages = {
        "provider_configuration": (
            "The Training Coach is not configured "
            "in this environment."
        ),
        "provider_authentication": (
            "The Training Coach could not authenticate "
            "with its provider. Please try again later."
        ),
        "provider_quota": (
            "The Training Coach provider quota is "
            "currently unavailable. Please try again later."
        ),
        "provider_request": (
            "The Training Coach could not process this "
            "request. No interpretation was saved."
        ),
        "provider_safety": (
            "The Training Coach provider did not accept "
            "this request. No interpretation was saved."
        ),
        "provider_unavailable": (
            "The Training Coach provider is temporarily "
            "unavailable. Please try again later."
        ),
    }

    return messages.get(
        error_code,
        (
            "The interpretation could not be generated. "
            "No result was saved."
        ),
    )

def _training_coach_limit_message(
    error_code: str | None,
) -> str:
    """
    Return a clear daily-limit message.
    """

    if error_code == "user_daily_limit":

        return (
            "You have reached your Training Coach "
            "limit for today. You can generate "
            "another interpretation tomorrow."
        )

    return (
        "The Training Coach has reached its "
        "overall limit for today. Please try "
        "again tomorrow."
    )

def _resolve_activity_coach(
    *,
    athlete,
    activity,
    payload,
    regenerate: bool,
    consent_permitted: bool,
    resolver=None,
):
    """
    Route generation through the application use case.
    """

    if not consent_permitted:

        raise PermissionError(
            "Training Coach consent is required."
        )

    if resolver is None:

        raise RuntimeError(
            "Training Coach generation is not configured."
        )

    return resolver(
        athlete=athlete,
        workout_id=(
            activity.workout_id
        ),
        payload=payload,
        regenerate=regenerate,
    )

def show_activities_page(
    athlete,
    *,
    on_update_workout=None,
    on_delete_workouts=None,
    training_coach_permitted: bool = False,
    on_allow_training_coach=None,
    on_resolve_training_coach=None,
) -> bool:
    """
    Displays a compact scrolling activity browser.
    """
    athlete_changed = bool(
        st.session_state.pop(
            "activity_coach_notes_changed",
            False,
        )
    )

    _apply_activities_page_styles()

    presenter = ActivitiesPresenter(
        athlete.history,
        training_plan=(
            athlete.training_plan
        ),
        reference_day=date.today(),
    )

    all_activities = presenter.build()

    if not all_activities:

        st.info(
            "No activities are available yet. "
            "Import a file or add an activity manually."
        )

        return False

    available_sports = sorted(
        {
            activity.sport
            for activity
            in all_activities
        },
        key=str.casefold,
    )

    # ==================================================
    # Current filter state
    # ==================================================

    query = st.session_state.get(
        "activities_search",
        "",
    )

    selected_sport = (
        st.session_state.get(
            "activities_sport",
            "All sports",
        )
    )

    selected_outcome = (
        st.session_state.get(
            "activities_outcome",
            "All results",
        )
    )

    selected_period = (
        st.session_state.get(
            "activities_period",
            "All time",
        )
    )

    today = date.today()

    activities = presenter.build(
        filters=ActivityFilters(
            query=query,
            sport=(
                None
                if selected_sport
                == "All sports"
                else selected_sport
            ),
            outcome_status=(
                _outcome_filter_value(
                    selected_outcome
                )
            ),
            start_date=(
                _period_start_date(
                    selected_period,
                    reference_day=today,
                )
            ),
            end_date=today,
        )
    )

    selected_id = (
        st.session_state.get(
            "activities_selected_id"
        )
    )

    selected_activity = next(
        (
            activity
            for activity in activities
            if str(
                activity.workout_id
            )
            == selected_id
        ),
        None,
    )

    selected_workout = None

    if selected_activity is not None:

        selected_workout = (
            _workout_for_activity(
                athlete.history,
                selected_activity,
            )
        )

    (
        activity_column,
        utility_column,
    ) = st.columns(
        [1.85, 1],
        gap="large",
        vertical_alignment="top",
    )

    # ==================================================
    # LEFT — activity browser
    # ==================================================

    with activity_column:

        with st.container(
            height=720,
            border=True,
            key="activities_browser",
        ):

            # ==========================================
            # Activity rows
            # ==========================================

            if not activities:

                st.caption(
                    "No activities match "
                    "the selected filters."
                )

            for activity in activities:

                activity_id = str(
                    activity.workout_id
                )

                is_selected = (
                    selected_id
                    == activity_id
                )

                with st.container(
                    key=(
                        "activity_grid_row_"
                        f"{activity_id}"
                    )
                ):

                    st.html(
                        _activity_row_html(
                            activity,
                            selected=is_selected,
                        )
                    )

                    clicked = st.button(
                        (
                            "Open "
                            f"{activity.title or 'activity'}"
                        ),
                        key=(
                            "activity_row_"
                            f"{activity_id}"
                        ),
                        use_container_width=True,
                    )

                if clicked:

                    st.session_state[
                        "activities_selected_id"
                    ] = (
                        None
                        if is_selected
                        else activity_id
                    )

                    st.rerun()

                if not is_selected:
                    continue

                workout = (
                    _workout_for_activity(
                        athlete.history,
                        activity,
                    )
                )

                if workout is None:

                    st.warning(
                        "The selected activity "
                        "is no longer available."
                    )

                    continue

                _show_selected_activity_dashboard(
                    activity=activity,
                    workout=workout,
                    athlete=athlete,
                    on_update_workout=(
                        on_update_workout
                    ),
                    on_delete_workouts=(
                        on_delete_workouts
                    ),
                )

        # ==========================================
        # Filters outside the scrolling list
        # ==========================================

        with st.container(
            key="activities_browser_filters"
        ):

            (
                search_column,
                sport_column,
                result_column,
                period_column,
            ) = st.columns(
                [
                    2.0,
                    0.85,
                    0.9,
                    0.9,
                ],
                gap="small",
            )

            with search_column:

                st.text_input(
                    "Search",
                    placeholder=(
                        "Search activities"
                    ),
                    label_visibility=(
                        "collapsed"
                    ),
                    key=(
                        "activities_search"
                    ),
                )

            with sport_column:

                st.selectbox(
                    "Sport",
                    options=(
                        "All sports",
                        *available_sports,
                    ),
                    label_visibility=(
                        "collapsed"
                    ),
                    key=(
                        "activities_sport"
                    ),
                )

            with result_column:

                st.selectbox(
                    "Result",
                    options=(
                        _OUTCOME_OPTIONS
                    ),
                    label_visibility=(
                        "collapsed"
                    ),
                    key=(
                        "activities_outcome"
                    ),
                )

            with period_column:

                st.selectbox(
                    "Period",
                    options=(
                        _PERIOD_OPTIONS
                    ),
                    label_visibility=(
                        "collapsed"
                    ),
                    key=(
                        "activities_period"
                    ),
                )


    # ==================================================
    # RIGHT — Training coach
    # ==================================================

    with utility_column:
        with st.container(key="activities_utility"):
            with st.container(
                height=440,
                border=True,
                key="activity_coach_card",
            ):

                st.html(
                    (
                        '<div class="activities-coach-header">'
                        '<div class="activities-coach-heading">'
                        "Training coach"
                        "</div>"
                        "</div>"
                    )
                )

                if selected_activity is None:

                    st.html(
                        (
                            '<div class="'
                            'activities-coach-placeholder">'
                            "Select an activity to receive "
                            "a concise training interpretation."
                            "</div>"
                        )
                    )

                elif selected_workout is None:

                    st.warning(
                        "The selected activity "
                        "is no longer available."
                    )

                else:

                    (
                        coach_payload,
                        stored_interpretation,
                        stored_matches_current_context,
                    ) = _activity_coach_material(
                        activity=(
                            selected_activity
                        ),
                        workout=(
                            selected_workout
                        ),
                        athlete=athlete,
                    )
                    if (
                        stored_interpretation
                        is None
                    ):

                        disclosure = (
                            build_activity_coach_disclosure()
                        )

                        st.markdown(
                            f"**{disclosure.heading}**"
                        )

                        st.caption(
                            disclosure.purpose
                        )

                        st.caption(
                            (
                                "Data sent: "
                                f"{disclosure.data_summary}."
                            )
                        )

                        st.caption(
                            (
                                "The original activity file is "
                                "not sent. The generated "
                                "interpretation is saved with "
                                "the activity."
                            )
                        )

                        st.caption(
                            disclosure.limitation
                        )
                    if not training_coach_permitted:

                        st.caption(
                            (
                                "Training Coach is disabled. "
                                "You can enable it in Settings."
                            )
                        )
                    if (
                        stored_interpretation
                        is not None
                    ):

                        regenerate = st.button(
                            "Regenerate interpretation",
                            key=(
                                "regenerate_activity_coach_"
                                f"{selected_activity.workout_id}"
                            ),
                            use_container_width=True,
                        )

                        if (
                            regenerate
                            and not training_coach_permitted
                        ):

                            if (
                                on_allow_training_coach
                                is not None
                            ):

                                show_training_coach_consent_dialog(
                                    on_allow=(
                                        on_allow_training_coach
                                    )
                                )

                            else:

                                st.warning(
                                    "Training Coach permission "
                                    "cannot be changed right now."
                                )

                        elif not regenerate:

                            _show_activity_coach_narrative(
                                stored_interpretation
                                .narrative,
                                stale=not stored_matches_current_context,
                            )

                        else:

                            with st.spinner(
                                "Regenerating interpretation..."
                            ):

                                resolution = (
                                    _resolve_activity_coach(
                                        athlete=athlete,
                                        activity=(
                                            selected_activity
                                        ),
                                        payload=(
                                            coach_payload
                                        ),
                                        regenerate=True,
                                        consent_permitted=(
                                            training_coach_permitted
                                        ),
                                        resolver=(
                                            on_resolve_training_coach
                                        ),
                                    )
                                )

                            if (
                                resolution.status
                                is ActivityCoachResolutionStatus
                                .GENERATED
                                and resolution.interpretation
                                is not None
                            ):

                                st.session_state[
                                    "activity_coach_refresh_requested"
                                ] = True

                                _show_activity_coach_narrative(
                                    resolution
                                    .interpretation
                                    .narrative
                                )

                            elif (
                                resolution.status
                                is ActivityCoachResolutionStatus
                                .IN_PROGRESS
                            ):

                                st.warning(
                                    "An interpretation for this "
                                    "activity is already being "
                                    "generated. Please wait."
                                )

                                _show_activity_coach_narrative(
                                    stored_interpretation
                                    .narrative,
                                    stale=not stored_matches_current_context,
                                )

                            elif (
                                resolution.status
                                is ActivityCoachResolutionStatus
                                .LIMIT_REACHED
                            ):

                                st.warning(
                                    _training_coach_limit_message(
                                        resolution.error_code
                                    )
                                )

                                _show_activity_coach_narrative(
                                    stored_interpretation
                                    .narrative,
                                    stale=not stored_matches_current_context,
                                )

                            else:

                                st.warning(
                                    _training_coach_error_message(
                                        resolution.error_code
                                    )
                                )

                                _show_activity_coach_narrative(
                                    stored_interpretation
                                    .narrative,
                                    stale=not stored_matches_current_context,
                                )

                    else:

                        generate = st.button(
                            "Generate interpretation",
                            key=(
                                "generate_activity_coach_"
                                f"{selected_activity.workout_id}"
                            ),
                            type="primary",
                            use_container_width=True,
                        )

                        if (
                            generate
                            and not training_coach_permitted
                        ):

                            if (
                                on_allow_training_coach
                                is not None
                            ):

                                show_training_coach_consent_dialog(
                                    on_allow=(
                                        on_allow_training_coach
                                    )
                                )

                            else:

                                st.warning(
                                    "Training Coach permission "
                                    "cannot be changed right now."
                                )

                        elif generate:

                            with st.spinner(
                                "Generating interpretation..."
                            ):

                                resolution = (
                                    _resolve_activity_coach(
                                        athlete=athlete,
                                        activity=(
                                            selected_activity
                                        ),
                                        payload=(
                                            coach_payload
                                        ),
                                        regenerate=False,
                                        consent_permitted=(
                                            training_coach_permitted
                                        ),
                                        resolver=(
                                            on_resolve_training_coach
                                        ),
                                    )
                                )

                            if (
                                resolution.status
                                is ActivityCoachResolutionStatus
                                .GENERATED
                                and resolution.interpretation
                                is not None
                            ):

                                st.session_state[
                                    "activity_coach_refresh_requested"
                                ] = True

                                _show_activity_coach_narrative(
                                    resolution
                                    .interpretation
                                    .narrative
                                )

                            elif (
                                resolution.status
                                is ActivityCoachResolutionStatus
                                .IN_PROGRESS
                            ):

                                st.warning(
                                    "An interpretation for this "
                                    "activity is already being "
                                    "generated. Please wait."
                                )

                            elif (
                                resolution.status
                                is ActivityCoachResolutionStatus
                                .LIMIT_REACHED
                            ):

                                st.warning(
                                    _training_coach_limit_message(
                                        resolution.error_code
                                    )
                                )

                            elif (
                                resolution.status
                                in {
                                    ActivityCoachResolutionStatus
                                    .UNAVAILABLE,
                                    ActivityCoachResolutionStatus
                                    .FAILED,
                                }
                            ):

                                st.warning(
                                    _training_coach_error_message(
                                        resolution.error_code
                                    )
                                )
            with st.container(height=268, border=True, key="activities_bottom_slot"):
                if selected_workout is not None:

                    with st.container(
                        border=False,
                        key="activity_coach_notes",
                    ):

                        st.markdown(
                            "**Additional information**"
                        )

                        notes_key = (
                            "activity_coach_notes_"
                            f"{selected_activity.workout_id}"
                        )

                        st.text_area(
                            "Information for the Training Coach",
                            value=(
                                selected_workout
                                .feedback
                                .notes
                            ),
                            placeholder=(
                                "Add observations not available in "
                                "the activity file, such as pain, "
                                "stiffness, sleep, stress, motivation, "
                                "soreness, how the session felt, or "
                                "VO2max: 52.4 ."
                            ),
                            height=152,
                            label_visibility="collapsed",
                            key=notes_key,
                        )

                        st.button(
                            "Save information",
                            key=(
                                "save_activity_coach_notes_"
                                f"{selected_activity.workout_id}"
                            ),
                            use_container_width=True,
                            on_click=(
                                _save_activity_coach_notes
                            ),
                            kwargs={
                                "athlete": athlete,
                                "workout": (
                                    selected_workout
                                ),
                                "state_key": notes_key,
                            },
                        )
                else:
                    _show_activity_summary(all_activities, reference_day=today)


    return athlete_changed
