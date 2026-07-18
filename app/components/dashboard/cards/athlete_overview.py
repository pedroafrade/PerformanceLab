"""
PerformanceLab

Current physiology dashboard card.
"""

from __future__ import annotations

from performancelab.presentation.dashboard_models import (
    PhysiologyCardData,
)

from .metric_card_body import (
    MetricCardMetric,
    metric_card_body,
)


def _format_metric(
    value: float | None,
    unit: str = "",
    decimals: int = 0,
) -> str:
    """
    Format an optional physiology metric.
    """

    if value is None:

        return "—"

    formatted = f"{value:.{decimals}f}"

    if unit:

        return f"{formatted} {unit}"

    return formatted


def show_athlete_overview_card(
    data: PhysiologyCardData,
) -> None:
    """
    Render the compact current physiology card.
    """

    metric_card_body(
        metrics=(
            MetricCardMetric(
                value=_format_metric(
                    data.vo2_max,
                    decimals=1,
                ),
                label="VO₂max",
            ),
            MetricCardMetric(
                value=_format_metric(
                    data.resting_hr_30d,
                    unit="bpm",
                ),
                label="Resting HR · 30 d",
            ),
            MetricCardMetric(
                value=_format_metric(
                    data.walking_hr_30d,
                    unit="bpm",
                ),
                label="Walking HR · 30 d",
            ),
            MetricCardMetric(
                value=_format_metric(
                    data.hrv_30d,
                    unit="ms",
                ),
                label="HRV · 30 d",
            ),
            MetricCardMetric(
                value=_format_metric(
                    data.estimated_ftp,
                    unit="W",
                ),
                label="Estimated FTP",
            ),
            MetricCardMetric(
                value=_format_metric(
                    data.threshold_hr,
                    unit="bpm",
                ),
                label="Threshold HR",
            ),
        ),
    )