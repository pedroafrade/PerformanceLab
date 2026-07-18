"""
PerformanceLab

Performance management dashboard card.
"""

from __future__ import annotations

from performancelab.presentation.dashboard_models import (
    DashboardSummaryData,
)

from .metric_card_body import (
    MetricCardMetric,
    metric_card_body,
)


def _performance_status(
    tsb: float,
) -> str:
    """
    Returns a short interpretation of the current form.
    """

    if tsb >= 10:

        return "Fresh and ready."

    if tsb >= -10:

        return "Balanced training state."

    return "High fatigue. Recovery may be needed."


def show_performance_management_card(
    summary: DashboardSummaryData,
) -> None:
    """
    Render the compact performance status card.
    """

    metric_card_body(
        metrics=(
            MetricCardMetric(
                value=f"{summary.ctl:.1f}",
                label="Fitness · CTL",
            ),
            MetricCardMetric(
                value=f"{summary.atl:.1f}",
                label="Fatigue · ATL",
            ),
            MetricCardMetric(
                value=f"{summary.tsb:+.1f}",
                label="Form · TSB",
            ),
        ),
        status=_performance_status(
            summary.tsb
        ),
    )