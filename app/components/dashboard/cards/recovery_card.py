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
)


def recovery_card(
    data: RecoveryCardData,
) -> None:
    """
    Render the compact recovery dashboard card.
    """

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
                value=str(data.score),
                label="Recovery",
            ),
        ),
        details=tuple(details),
        progress=data.score,
        status=data.recommendation,
    )