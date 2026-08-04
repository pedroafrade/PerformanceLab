"""
PerformanceLab

Reusable training-plan phase timeline.
"""

from html import escape


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


def phase_timeline_html(
    *,
    timeline,
    current_date,
    visible_start,
    visible_end,
) -> str:
    """
    Builds the full-plan phase progression.
    """

    segments = phase_segments(
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


def phase_timeline_styles() -> str:
    """
    Returns the shared CSS used by the phase timeline.
    """

    return """
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
"""