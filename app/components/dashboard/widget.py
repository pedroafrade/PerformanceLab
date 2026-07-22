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
    key: str
    callback: Callable[[], None] | None = None


def _action_button_style(
    key: str,
) -> None:
    """
    Styles only the dashboard action button identified by its Streamlit key.
    """

    st.markdown(
        f"""
        <style>
        .st-key-{key} {{
            display: flex;
            justify-content: flex-end;
        }}

        .st-key-{key} button {{
            width: 1.65rem !important;
            min-width: 1.65rem !important;
            height: 1.65rem !important;
            min-height: 1.65rem !important;
            padding: 0 !important;
            border: none !important;
            border-radius: 0 !important;
            background: transparent !important;
            box-shadow: none !important;
            color: #8b949e !important;
        }}

        .st-key-{key} button:hover,
        .st-key-{key} button:focus,
        .st-key-{key} button:active {{
            border: none !important;
            background: transparent !important;
            box-shadow: none !important;
            color: #31333f !important;
        }}

        .st-key-{key} button p {{
            margin: 0 !important;
            font-size: 1.20rem !important;
            line-height: 1 !important;
        }}

        .st-key-{key} button svg {{
            display: none !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


@contextmanager
def dashboard_widget(
    *,
    title: str | None = None,
    icon: str | None = None,
    subtitle: str | None = None,
    action: DashboardAction | None = None,
    divider: bool = True,
    height: int | str | None = None,
) -> Iterator[None]:
    """
    Dashboard widget container.
    """

    container_options = {
        "border": True,
    }

    if height is not None:
        container_options["height"] = height

    with st.container(
        **container_options,
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

                    _action_button_style(
                        action.key
                    )

                    if st.button(
                        "⋮",
                        key=action.key,
                        help=action.label,
                    ):

                        if action.callback is not None:

                            action.callback()

            if divider:

                st.divider()

        yield