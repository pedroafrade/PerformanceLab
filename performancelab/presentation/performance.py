"""
PerformanceLab

Performance presentation utilities.
"""

import plotly.graph_objects as go


def performance_chart(
    performance: dict,
) -> go.Figure:
    """
    Builds the performance management chart.

    Parameters
    ----------
    performance
        Presentation-ready performance data containing
        dates, load, CTL, ATL and TSB values.

    Returns
    -------
    plotly.graph_objects.Figure
        Performance chart ready to be rendered by the UI.
    """

    figure = go.Figure()

    figure.add_trace(
        go.Scatter(
            x=performance.dates,
            y=performance.load,
            mode="lines",
            name="Load",
        )
    )

    figure.add_trace(
        go.Scatter(
            x=performance.dates,
            y=performance.ctl,
            mode="lines",
            name="CTL",
        )
    )

    figure.add_trace(
        go.Scatter(
            x=performance.dates,
            y=performance.atl,
            mode="lines",
            name="ATL",
        )
    )

    figure.add_trace(
        go.Scatter(
            x=performance.dates,
            y=performance.tsb,
            mode="lines",
            name="TSB",
        )
    )

    figure.update_layout(
        height=400,
        margin={
            "l": 20,
            "r": 20,
            "t": 20,
            "b": 20,
        },
        hovermode="x unified",
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "left",
            "x": 0,
        },
        xaxis_title=None,
        yaxis_title=None,
    )

    return figure