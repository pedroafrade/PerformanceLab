"""
Recovery dashboard card.
"""

from __future__ import annotations

from performancelab.presentation.dashboard_models import (
    RecoveryCardData,
)

from .metric_card_body import (
    MetricCardDetail,
    MetricCardMetric,
    metric_card_body,
    metric_status_color,
)
from ...current_state_summary import CurrentStateSummaryData, recovery_context as _recovery_context


def recovery_card(
    data: RecoveryCardData,
    *,
    current_state=None,
) -> None:
    """
    Render the compact recovery dashboard card.
    """

    if current_state is not None:
        state = current_state
        summary = CurrentStateSummaryData(
            recovery_score=state.recovery_score,
            recovery_balance=state.recovery_balance,
            recovery_status=state.recovery_status,
            chronic_load=state.ctl, acute_load=state.atl, load_status="",
            form=state.form, recovery_reference_time=state.reference_time,
            hours_since_last_workout=state.hours_since_last_workout,
            recovery_is_time_aware=state.recovery_is_time_aware,
        )
        metric_card_body(
            metrics=(MetricCardMetric(f"{state.recovery_score:.0f}", "Estimated recovery"),),
            details=(MetricCardDetail("Status", state.recovery_status),
                     MetricCardDetail("", _recovery_context(summary))),
            progress=state.recovery_score,
            progress_color=metric_status_color(state.recovery_status),
            status=state.recovery_recommendation,
        )
        return

    details = []

    if data.trend:

        details.append(
            MetricCardDetail(
                label="Trend",
                value=data.trend,
            )
        )

    details.append(
        MetricCardDetail(
            label="Status",
            value=data.status,
        )
    )

    metric_card_body(
        metrics=(
            MetricCardMetric(
                value=f"{data.score:.0f}",
                label="Recovery",
            ),
        ),
        details=tuple(details),
        progress=data.score,
        progress_color=metric_status_color(data.status),
        status=data.recommendation,
    )
