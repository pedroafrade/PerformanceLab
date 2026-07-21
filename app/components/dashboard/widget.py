"""
PerformanceLab

Reusable dashboard widget.
"""

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass

import streamlit as st


@dataclass(frozen=True)
class DashboardAction:
    """
    Action displayed in the dashboard widget header.
    """

    label: str
    icon: str = ":material/more_vert:"
    callback: Callable[[], None] | None = None


@contextmanager
def dashboard_widget(
    *,
    title: str | None = None,
    icon: str | None = None,
    subtitle: str | None = None,
    action: DashboardAction | None = None,
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

                if action is None:

                    st.markdown(
                        (
                            "<div style='"
                            "text-align:right;"
                            "font-size:1.15rem;"
                            "line-height:1;"
                            "color:#8b949e;"
                            "'>"
                            "⋮"
                            "</div>"
                        ),
                        unsafe_allow_html=True,
                    )

                else:

                    with st.popover(
                        "",
                        icon=action.icon,
                        use_container_width=True,
                    ):

                        if st.button(
                            action.label,
                            use_container_width=True,
                        ):

                            if action.callback is not None:

                                action.callback()

            if divider:

                st.divider()

        yield