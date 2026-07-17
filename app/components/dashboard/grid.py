"""
PerformanceLab

Dashboard grid layouts.
"""

from collections.abc import Sequence

import streamlit as st


TOP_ROW_WIDTHS = (1, 2)
SUMMARY_ROW_WIDTHS = (1, 1)
BOTTOM_ROW_WIDTHS = (1, 2)

DEFAULT_GAP = "medium"
SECTION_GAP = "large"


def dashboard_row(
    widths: Sequence[int | float],
    *,
    gap: str = DEFAULT_GAP,
):
    """
    Creates a dashboard row with configurable column widths.
    """

    return st.columns(
        list(widths),
        gap=gap,
        vertical_alignment="top",
    )


def dashboard_top_row():
    """
    Creates the athlete and overview row.
    """

    return dashboard_row(
        TOP_ROW_WIDTHS,
        gap=SECTION_GAP,
    )


def dashboard_summary_row():
    """
    Creates the training summary and status row.
    """

    return dashboard_row(
        SUMMARY_ROW_WIDTHS,
        gap=DEFAULT_GAP,
    )


def dashboard_bottom_row():
    """
    Creates the planning and workout history row.
    """

    return dashboard_row(
        BOTTOM_ROW_WIDTHS,
        gap=SECTION_GAP,
    )