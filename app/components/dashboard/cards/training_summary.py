"""
PerformanceLab

Weekly training summary dashboard card.
"""

from __future__ import annotations

from performancelab.presentation.dashboard_models import (
    DashboardSummaryData,
)

from .common import format_duration
from .metric_card_body import (
    MetricCardMetric,
    metric_card_body,
)


def show_training_summary_card(
    summary: DashboardSummaryData,
) -> None:
    """
    Render the compact weekly training summary card.
    """

    metric_card_body(
        metrics=(
            MetricCardMetric(
                value=str(summary.workouts),
                label="Workouts",
            ),
            MetricCardMetric(
                value=str(summary.training_days),
                label="Training days",
            ),
            MetricCardMetric(
                value=format_duration(
                    summary.total_duration
                ),
                label="Duration",
            ),
            MetricCardMetric(
                value=str(summary.sports),
                label="Sports",
            ),
        ),
    )