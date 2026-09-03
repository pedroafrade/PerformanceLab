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
    center_text: str | None = None,
    action: DashboardAction | None = None,
    divider: bool = True,
    height: int | str | None = None,
    key: str | None = None,
) -> Iterator[None]:
    """
    Dashboard widget container.
    """

    container_options = {
        "border": True,
    }
    if key is not None:
        container_options["key"] = key
        # Set the bordered container height, not only its inner content block.
        if key.startswith("dashboard_top_"):
            container_options["height"] = 360
        elif key in {"dashboard_load", "dashboard_recovery", "dashboard_brief", "dashboard_next_workout", "dashboard_summary"}:
            container_options["height"] = 380

    if height is not None:
        container_options["height"] = height

    with st.container(
        **container_options,
    ):

        if title:

            if center_text:

                (
                    title_col,
                    center_col,
                    action_col,
                ) = st.columns(
                    [1, 1, 1],
                    vertical_alignment="center",
                )

            else:

                title_col, action_col = st.columns(
                    [12, 1],
                    vertical_alignment="center",
                )

                center_col = None

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

                    st.markdown(
                        f"<div style='margin-top:-0.35rem; margin-bottom:0.15rem; "
                        "font-size:0.82rem; color:#8b949e;'>"
                        f"{subtitle}"
                        "</div>",
                        unsafe_allow_html=True,
                    )

            if center_col is not None:

                with center_col:

                    st.markdown(
                        (
                            "<div style='"
                            "text-align:center;"
                            "font-size:0.76rem;"
                            "color:#8b949e;"
                            "white-space:nowrap;"
                            "'>"
                            f"{center_text}"
                            "</div>"
                        ),
                        unsafe_allow_html=True,
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
