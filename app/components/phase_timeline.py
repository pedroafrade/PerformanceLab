"""
PerformanceLab

Reusable training-plan phase timeline.
"""

from datetime import date, timedelta
from html import escape
from math import ceil


def phase_segments(
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


def phase_range_segments(
    phases,
):
    """
    Expands phase date ranges into daily timeline
    segments.
    """

    segments = []

    for phase in phases:

        days = []

        current_day = (
            phase.start_date
        )

        while current_day <= phase.end_date:

            days.append(
                current_day
            )

            current_day += timedelta(
                days=1
            )

        segments.append(
            (
                str(
                    phase.name
                    or "Unassigned"
                ).strip(),
                tuple(days),
            )
        )

    return tuple(
        segments
    )


def _phase_date_range(
    days: tuple[date, ...],
) -> str:
    """
    Formats the visible date range of one phase.
    """

    start_date = days[0]
    end_date = days[-1]

    if start_date == end_date:
        return start_date.strftime(
            "%d %b %Y"
        )

    if (
        start_date.month
        == end_date.month
        and start_date.year
        == end_date.year
    ):
        return (
            f"{start_date.strftime('%d')} – "
            f"{end_date.strftime('%d %b')}"
        )

    if start_date.year == end_date.year:
        return (
            f"{start_date.strftime('%d %b')} – "
            f"{end_date.strftime('%d %b')}"
        )

    return (
        f"{start_date.strftime('%d %b %Y')} – "
        f"{end_date.strftime('%d %b %Y')}"
    )


def _current_segment_index(
    *,
    segments,
    current_date: date,
) -> int | None:
    """
    Returns the phase segment containing the current date.
    """

    return next(
        (
            index
            for index, (_, days)
            in enumerate(segments)
            if (
                days
                and days[0]
                <= current_date
                <= days[-1]
            )
        ),
        None,
    )


def _phase_week_progress(
    *,
    days: tuple[date, ...],
    current_date: date,
) -> tuple[int, int]:
    """
    Returns the current week and total weeks of a phase.
    """

    elapsed_days = max(
        0,
        (
            current_date
            - days[0]
        ).days,
    )

    current_week = (
        elapsed_days // 7
        + 1
    )

    total_weeks = max(
        1,
        ceil(
            len(days) / 7
        ),
    )

    return (
        min(
            current_week,
            total_weeks,
        ),
        total_weeks,
    )


def _phase_timeline_footer_html(
    *,
    segments,
    current_date: date,
) -> str:
    """
    Builds current-phase and next-phase context.
    """

    current_index = (
        _current_segment_index(
            segments=segments,
            current_date=current_date,
        )
    )

    if current_index is None:
        return ""

    phase, days = (
        segments[current_index]
    )

    current_week, total_weeks = (
        _phase_week_progress(
            days=days,
            current_date=current_date,
        )
    )

    current_text = (
        f"{escape(phase)}"
        f" · week {current_week} of {total_weeks}"
    )

    next_text = ""

    if current_index + 1 < len(segments):

        next_phase, next_days = (
            segments[current_index + 1]
        )

        days_until_next = max(
            0,
            (
                next_days[0]
                - current_date
            ).days,
        )

        if days_until_next == 1:
            timing = "in 1 day"
        else:
            timing = (
                f"in {days_until_next} days"
            )

        next_text = (
            "Next phase: "
            f"{escape(next_phase)} "
            f"{timing}"
        )

    footer_parts = [
        '<div class="weekly-phase-footer">',
        '<div class="weekly-phase-current-summary">',
        current_text,
        "</div>",
    ]

    if next_text:

        footer_parts.extend(
            (
                '<div class="weekly-phase-next-summary">',
                next_text,
                "</div>",
            )
        )

    footer_parts.append(
        "</div>"
    )

    return "".join(
        footer_parts
    )


def _phase_timeline_from_segments_html(
    *,
    segments,
    current_date,
    visible_start,
    visible_end,
) -> str:
    """
    Builds timeline HTML from prepared phase segments.
    """

    if not segments:
        return ""

    current_index = (
        _current_segment_index(
            segments=segments,
            current_date=current_date,
        )
    )

    segment_html = []

    for index, (phase, days) in enumerate(
        segments
    ):

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

        segment_classes = [
            "weekly-phase-segment",
        ]

        if index == current_index:
            segment_classes.append(
                "weekly-phase-segment-current"
            )

        if phase.lower() == "race":
            segment_classes.append(
                "weekly-phase-segment-race"
            )

        segment_html.append(
            (
                '<div class="'
                f'{" ".join(segment_classes)}'
                '" '
                f'style="flex:{len(days)}">'
                '<div class="weekly-phase-heading">'
                '<div class="weekly-phase-label">'
                f"{escape(phase)}"
                "</div>"
                '<div class="weekly-phase-range">'
                f"{escape(_phase_date_range(days))}"
                "</div>"
                "</div>"
                '<div class="weekly-phase-track">'
                '<div class="weekly-phase-track-line"></div>'
                '<div class="weekly-phase-dots">'
                f'{"".join(dots)}'
                "</div>"
                "</div>"
                "</div>"
            )
        )

    footer_html = (
        _phase_timeline_footer_html(
            segments=segments,
            current_date=current_date,
        )
    )

    return (
        '<div class="weekly-phase-timeline">'
        '<div class="weekly-phase-segments">'
        f'{"".join(segment_html)}'
        "</div>"
        f"{footer_html}"
        "</div>"
    )


def phase_timeline_html(
    *,
    timeline,
    current_date,
    visible_start,
    visible_end,
) -> str:
    """
    Builds a phase timeline from daily timeline data.
    """

    return (
        _phase_timeline_from_segments_html(
            segments=phase_segments(
                timeline
            ),
            current_date=current_date,
            visible_start=visible_start,
            visible_end=visible_end,
        )
    )


def phase_timeline_from_phases_html(
    *,
    phases,
    current_date,
    visible_start,
    visible_end,
) -> str:
    """
    Builds the same timeline from phase date ranges.
    """

    return (
        _phase_timeline_from_segments_html(
            segments=phase_range_segments(
                phases
            ),
            current_date=current_date,
            visible_start=visible_start,
            visible_end=visible_end,
        )
    )


def phase_timeline_styles() -> str:
    """
    Returns the shared CSS used by the phase timeline.
    """

    return """
.weekly-phase-timeline {
    margin: 0 0 0.25rem 0;
    padding: 0.45rem 0.7rem 0.35rem 0.7rem;
    border: 1px solid rgba(128, 128, 128, 0.22);
    border-radius: 0.7rem;
    background: rgba(128, 128, 128, 0.025);
}

.weekly-phase-segments {
    display: flex;
    align-items: stretch;
    width: 100%;
    gap: 0;
}

.weekly-phase-segment {
    min-width: 0;
    padding: 0 0.3rem 0.3rem 0.3rem;
    border-bottom: 2px solid transparent;
    text-align: center;
    box-sizing: border-box;
}

.weekly-phase-segment + .weekly-phase-segment {
    border-left: 1px solid rgba(128, 128, 128, 0.18);
}

.weekly-phase-segment-current {
    border-bottom-color: #ff4b4b;
}

.weekly-phase-heading {
    min-height: 1.75rem;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
}

.weekly-phase-label {
    overflow: hidden;
    font-size: 0.66rem;
    font-weight: 700;
    line-height: 1;
    opacity: 0.88;
    text-overflow: ellipsis;
    text-transform: capitalize;
    white-space: nowrap;
}

.weekly-phase-segment-current .weekly-phase-label {
    color: #ff4b4b;
    opacity: 1;
}

.weekly-phase-range {
    margin-top: 0.18rem;
    overflow: hidden;
    font-size: 0.56rem;
    line-height: 1;
    opacity: 0.58;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.weekly-phase-track {
    position: relative;
    min-height: 0.55rem;
    padding-top: 0.15rem;
}

.weekly-phase-track-line {
    position: absolute;
    top: 0.39rem;
    left: 0;
    right: 0;
    height: 1px;
    background: rgba(128, 128, 128, 0.28);
}

.weekly-phase-dots {
    position: relative;
    z-index: 1;
    display: flex;
    align-items: center;
    justify-content: space-around;
    min-height: 0.45rem;
    gap: 1px;
}

.weekly-phase-dot {
    display: inline-block;
    flex: 0 0 auto;
    width: 4px;
    height: 4px;
    border: 1px solid currentColor;
    border-radius: 50%;
    background: var(--background-color);
    opacity: 0.22;
    box-sizing: border-box;
}

.weekly-phase-dot-visible {
    opacity: 0.72;
}

.weekly-phase-dot-current {
    width: 7px;
    height: 7px;
    border: 2px solid #ff4b4b;
    background: var(--background-color);
    opacity: 1;
}

.weekly-phase-dot-race {
    width: 6px;
    height: 6px;
    border-width: 2px;
    opacity: 0.85;
}

.weekly-phase-dot-race.weekly-phase-dot-current {
    width: 8px;
    height: 8px;
    border-color: #ff4b4b;
    opacity: 1;
}

.weekly-phase-footer {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    margin-top: 0.28rem;
    padding-top: 0.28rem;
    border-top: 1px solid rgba(128, 128, 128, 0.14);
    font-size: 0.6rem;
    line-height: 1.1;
}

.weekly-phase-current-summary {
    color: #ff4b4b;
    font-weight: 700;
}

.weekly-phase-next-summary {
    text-align: right;
    opacity: 0.62;
}

@media (max-width: 900px) {
    .weekly-phase-range {
        display: none;
    }

    .weekly-phase-footer {
        flex-direction: column;
        gap: 0.2rem;
    }

    .weekly-phase-next-summary {
        text-align: left;
    }
}
"""