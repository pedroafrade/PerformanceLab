"""
PerformanceLab

Performance chart dashboard card.
"""

import pandas as pd
import streamlit as st


def show_performance_chart_card(
    performance,
) -> None:
    """
    Displays the performance chart card.
    """

    if performance["dates"]:

        chart_data = pd.DataFrame(
            {
                "Load": performance["load"],
                "CTL": performance["ctl"],
                "ATL": performance["atl"],
                "TSB": performance["tsb"],
            },
            index=pd.to_datetime(
                performance["dates"]
            ),
        )

        chart_data.index.name = "Date"

        st.line_chart(
            chart_data,
        )

        with st.expander(
            "Show performance data"
        ):

            st.dataframe(
                chart_data,
                width="stretch",
            )

    else:

        st.info(
            "Add a workout to display "
            "performance data."
        )