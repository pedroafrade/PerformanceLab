"""
Training load dashboard card.
"""

from __future__ import annotations

from performancelab.presentation.dashboard_models import (
    TrainingLoadCardData,
)

from .metric_card_body import (
    MetricCardDetail,
    MetricCardMetric,
    metric_card_body,
)


def training_load_card(
    data: TrainingLoadCardData,
) -> None:
    """
    Render the compact training load dashboard card.
    """

    metric_card_body(
        metrics=(
            MetricCardMetric(
                value=f"{data.acute_load:.1f}",
                label="Acute",
            ),
            MetricCardMetric(
                value=f"{data.chronic_load:.1f}",
                label="Chronic",
            ),
        ),
        details=(
            MetricCardDetail(
                label="Ramp",
                value=f"{data.ramp_rate:+.1f}%",
            ),
            MetricCardDetail(
                label="Score",
                value=f"{data.score}/100",
            ),
        ),
        progress=data.score,
        status=data.status,
    )