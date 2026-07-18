"""
PerformanceLab

Reusable dashboard widget.
"""

from collections.abc import Iterator
from contextlib import contextmanager

import streamlit as st


@contextmanager
def dashboard_widget(
    *,
    title: str | None = None,
    icon: str | None = None,
    subtitle: str | None = None,
    actions: str = "⋮",
    divider: bool = True,
) -> Iterator[None]:
    """
    Dashboard widget container.
    """

    with st.container(
        border=True,
    ):

        if title:

            title_col, action_col = st.columns(
                [12, 1],
                vertical_alignment="center",
            )

            with title_col:

                title_content = (
                    f"{icon} **{title}**"
                    if icon
                    else f"**{title}**"
                )

                st.markdown(
                    title_content
                )

                if subtitle:

                    st.caption(
                        subtitle
                    )

            with action_col:

                st.markdown(
                    (
                        "<div style='"
                        "text-align:right;"
                        "font-size:1.15rem;"
                        "line-height:1;"
                        "color:#8b949e;"
                        "'>"
                        f"{actions}"
                        "</div>"
                    ),
                    unsafe_allow_html=True,
                )

            if divider:

                st.divider()

        yield