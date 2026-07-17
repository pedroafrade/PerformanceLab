"""
PerformanceLab

Reusable dashboard widget.
"""

from collections.abc import Iterator
from contextlib import contextmanager
from html import escape

import streamlit as st


@contextmanager
def dashboard_widget(
    *,
    title: str | None = None,
    icon: str | None = None,
    subtitle: str | None = None,
    actions: str = "⋮",
) -> Iterator[None]:
    """
    Dashboard widget container.
    """

    with st.container(border=True):

        if title:

            left, right = st.columns(
                [12, 1],
                vertical_alignment="center",
            )

            with left:

                pieces = []

                if icon:
                    pieces.append(
                        f"<span style='margin-right:0.45rem'>{escape(icon)}</span>"
                    )

                pieces.append(
                    f"<span>{escape(title)}</span>"
                )

                st.markdown(
                    (
                        "<div style='display:flex;"
                        "align-items:center;"
                        "font-size:1rem;"
                        "font-weight:600;"
                        "padding:0.15rem 0 0.15rem 0;'>"
                        + "".join(pieces)
                        + "</div>"
                    ),
                    unsafe_allow_html=True,
                )

                if subtitle:

                    st.caption(
                        subtitle
                    )

            with right:

                st.markdown(
                    (
                        "<div style='display:flex;"
                        "justify-content:flex-end;"
                        "align-items:center;"
                        "height:100%;"
                        "font-size:1.2rem;"
                        "color:#9aa0a6;'>"
                        f"{escape(actions)}"
                        "</div>"
                    ),
                    unsafe_allow_html=True,
                )

            st.divider()

        yield