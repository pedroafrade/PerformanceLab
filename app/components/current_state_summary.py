"""
PerformanceLab

Reusable current physiological-state summary.
"""

from dataclasses import dataclass
from datetime import datetime
from html import escape


@dataclass(frozen=True, slots=True)
class CurrentStateSummaryData:
    """
    Values required by the current-state summary row.
    """

    recovery_score: float
    recovery_balance: float
    recovery_status: str

    chronic_load: float
    acute_load: float
    load_status: str

    form: float

    recovery_reference_time: (
        datetime | None
    ) = None

    hours_since_last_workout: (
        float | None
    ) = None

    recovery_is_time_aware: bool = False


def form_status(
    value: float,
) -> str:
    """
    Returns a concise current-form interpretation.
    """

    if value >= 5:
        return "Fresh"

    if value >= -5:
        return "Balanced"

    if value >= -15:
        return "Loaded"

    return "Fatigued"


def load_status(
    acute_load: float,
    chronic_load: float,
) -> str:
    """
    Describes recent load relative to chronic load.
    """

    if chronic_load <= 0:
        return "No baseline"

    ratio = (
        acute_load
        / chronic_load
    )

    if ratio > 1.2:
        return "Elevated"

    if ratio < 0.8:
        return "Reduced"

    return "Stable"


def recovery_context(
    summary: CurrentStateSummaryData,
) -> str:
    """
    Explains the temporal source of recovery.
    """

    values = [
        (
            "Balance "
            f"{summary.recovery_balance:+.1f}"
        )
    ]

    if summary.recovery_is_time_aware:
        if (
            summary.hours_since_last_workout
            is not None
        ):
            values.append(
                (
                    f"{round(summary.hours_since_last_workout)} "
                    "h since last session"
                )
            )
        else:
            values.append(
                "Time-aware estimate"
            )
    else:
        values.append(
            "Daily estimate"
        )

    if (
        summary.recovery_reference_time
        is not None
    ):
        values.append(
            (
                "Updated "
                f"{summary.recovery_reference_time:%H:%M}"
            )
        )

    return " · ".join(
        values
    )


# Compatibility name for components loaded independently in tests.
_recovery_context = recovery_context


def current_state_summary_html(
    summary: CurrentStateSummaryData,
) -> str:
    """
    Builds the four current physiological-state cards.
    """

    cards = (
        (
            "♡",
            "Estimated recovery",
            f"{summary.recovery_score:.0f}",
            summary.recovery_status,
            recovery_context(
                summary
            ),
        ),
        (
            "↗",
            "Chronic load",
            f"{summary.chronic_load:.0f}",
            load_status(
                summary.acute_load,
                summary.chronic_load,
            ),
            "Current training state",
        ),
        (
            "⚖",
            "Form",
            f"{summary.form:+.1f}",
            form_status(
                summary.form
            ),
            "Today",
        ),
        (
            "▥",
            "Acute load",
            f"{summary.acute_load:.0f}",
            summary.load_status,
            "Recent training load",
        ),
    )

    cards_html = []

    for (
        icon,
        label,
        value,
        status,
        context,
    ) in cards:
        cards_html.append(
            (
                '<section class="current-state-card">'
                '<div class="current-state-icon">'
                f"{escape(icon)}"
                "</div>"
                '<div class="current-state-content">'
                '<div class="current-state-label">'
                f"{escape(label)}"
                "</div>"
                '<div class="current-state-value">'
                f"{escape(value)}"
                "</div>"
                '<div class="current-state-status">'
                f"{escape(status)}"
                "</div>"
                '<div class="current-state-context">'
                f"{escape(context)}"
                "</div>"
                "</div>"
                "</section>"
            )
        )

    return (
        '<div class="current-state-grid">'
        + "".join(
            cards_html
        )
        + "</div>"
    )


def current_state_summary_styles() -> str:
    """
    Returns shared styles for the current-state row.
    """

    return """
    .current-state-grid {
        display: grid;
        grid-template-columns:
            repeat(4, minmax(0, 1fr));
        gap: 0.65rem;
        margin: 0 0 0.15rem 0;
    }

    .current-state-card {
        display: grid;
        grid-template-columns:
            2.65rem minmax(0, 1fr);
        gap: 0.6rem;
        align-items: center;
        min-height: 4.65rem;
        padding: 0.34rem 0.7rem;
        border:
            1px solid rgba(128, 128, 128, 0.22);
        border-radius: 0.65rem;
        background:
            rgba(128, 128, 128, 0.015);
        box-sizing: border-box;
    }

    .current-state-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 2.4rem;
        height: 2.4rem;
        border:
            1px solid rgba(128, 128, 128, 0.22);
        border-radius: 50%;
        background:
            rgba(128, 128, 128, 0.025);
        font-size: 1.02rem;
        font-weight: 500;
    }

    .current-state-content {
        min-width: 0;
    }

    .current-state-label {
        overflow: hidden;
        font-size: 0.65rem;
        line-height: 1.05;
        opacity: 0.58;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .current-state-value {
        margin-top: 0.08rem;
        font-size: 1.28rem;
        font-weight: 750;
        line-height: 1;
    }

    .current-state-status {
        margin-top: 0.16rem;
        font-size: 0.69rem;
        font-weight: 700;
        line-height: 1.05;
    }

    .current-state-context {
        overflow: hidden;
        margin-top: 0.18rem;
        font-size: 0.57rem;
        line-height: 1.1;
        opacity: 0.52;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    @media (max-width: 900px) {
        .current-state-grid {
            grid-template-columns:
                repeat(2, minmax(0, 1fr));
        }
    }

    @media (max-width: 560px) {
        .current-state-grid {
            grid-template-columns: 1fr;
        }
    }
    """
