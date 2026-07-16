"""
PerformanceLab

Sensor Card Streamlit Component.
"""

import pandas as pd
import streamlit as st

from performancelab.presentation import SensorCard


# ======================================================
# Sensor card
# ======================================================

def show_sensor_card(
    card: SensorCard,
) -> None:

    """
    Displays sensor statistics and a time-series chart.
    """

    if not card.available:

        return

    st.divider()

    st.subheader(card.title)

    average_column, \
        minimum_column, \
        maximum_column = st.columns(3)

    average_column.metric(
        "Average",
        card.average_label,
    )

    minimum_column.metric(
        "Minimum",
        card.minimum_label,
    )

    maximum_column.metric(
        "Maximum",
        card.maximum_label,
    )

    chart_rows = card.chart_data

    if not chart_rows:

        return

    chart = pd.DataFrame(
        {
            "Elapsed minutes": [
                row["elapsed_minutes"]
                for row in chart_rows
            ],
            card.title: [
                row["value"]
                for row in chart_rows
            ],
        }
    )

    chart = chart.set_index(
        "Elapsed minutes"
    )

    st.line_chart(
        chart,
    )