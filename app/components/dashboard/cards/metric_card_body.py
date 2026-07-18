"""
PerformanceLab

Reusable body for compact dashboard metric cards.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from html import escape

import streamlit as st


@dataclass(frozen=True)
class MetricCardMetric:
    """
    Primary metric displayed by a compact dashboard card.
    """

    value: str
    label: str


@dataclass(frozen=True)
class MetricCardDetail:
    """
    Secondary label-value detail displayed by a metric card.
    """

    label: str
    value: str


def _metric_html(
    metric: MetricCardMetric,
) -> str:
    """
    Builds the HTML for a primary metric.
    """

    return (
        "<div style='margin-bottom:0.90rem;'>"
        "<div style='"
        "font-size:1.30rem;"
        "font-weight:700;"
        "line-height:1.05;"
        "'>"
        f"{escape(metric.value)}"
        "</div>"
        "<div style='"
        "margin-top:0.18rem;"
        "font-size:0.72rem;"
        "line-height:1.1;"
        "color:#8b949e;"
        "'>"
        f"{escape(metric.label)}"
        "</div>"
        "</div>"
    )


def _detail_html(
    detail: MetricCardDetail,
) -> str:
    """
    Builds the HTML for a secondary detail.
    """

    return (
        "<div style='"
        "margin-bottom:0.60rem;"
        "font-size:0.82rem;"
        "line-height:1.2;"
        "'>"
        "<span style='color:#8b949e;'>"
        f"{escape(detail.label)}"
        "</span>"
        "<span style='"
        "margin-left:0.30rem;"
        "font-weight:600;"
        "'>"
        f"{escape(detail.value)}"
        "</span>"
        "</div>"
    )


def _progress_html(
    progress: int,
) -> str:
    """
    Builds a monochromatic progress bar.
    """

    clamped_progress = max(
        0,
        min(
            100,
            int(progress),
        ),
    )

    return (
        "<div style='"
        "width:100%;"
        "height:0.38rem;"
        "overflow:hidden;"
        "margin:0.10rem 0 0.75rem 0;"
        "border-radius:999px;"
        "background:#e5e7eb;"
        "'>"
        "<div style='"
        f"width:{clamped_progress}%;"
        "height:100%;"
        "border-radius:999px;"
        "background:#111111;"
        "'></div>"
        "</div>"
    )


def metric_card_body(
    *,
    metrics: Sequence[MetricCardMetric],
    details: Sequence[MetricCardDetail] = (),
    progress: int | None = None,
    status: str | None = None,
) -> None:
    """
    Render a compact, vertically aligned metric card body.
    """

    parts = [
        "<div style='"
        "display:flex;"
        "flex-direction:column;"
        "align-items:flex-start;"
        "width:100%;"
        "padding-top:0.65rem;"
        "padding-bottom:1.10rem;"
        "'>"
    ]

    parts.extend(
        _metric_html(metric)
        for metric in metrics
    )

    parts.extend(
        _detail_html(detail)
        for detail in details
    )

    if progress is not None:

        parts.append(
            _progress_html(
                progress
            )
        )

    if status:

        parts.append(
            (
                "<div style='"
                "font-size:0.84rem;"
                "font-weight:600;"
                "line-height:1.2;"
                "'>"
                f"{escape(status)}"
                "</div>"
            )
        )

    parts.append(
        "</div>"
    )

    st.markdown(
        "".join(parts),
        unsafe_allow_html=True,
    )