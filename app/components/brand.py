"""Journal brand assets shared by authentication and navigation."""

from base64 import b64encode
from functools import lru_cache
from pathlib import Path


_ASSET_DIRECTORY = Path(__file__).resolve().parents[1] / "assets"


@lru_cache(maxsize=4)
def _image_data_uri(filename: str) -> str:
    """Return one bundled PNG as a browser-safe data URI."""

    encoded = b64encode(
        (_ASSET_DIRECTORY / filename).read_bytes()
    ).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def journal_logo_html(
    *,
    placement: str,
    theme: str = "light",
) -> str:
    """Render the appropriate Journal wordmark for the active colour scheme."""

    if placement not in {"login", "sidebar"}:
        raise ValueError("placement must be 'login' or 'sidebar'.")
    if theme not in {"light", "dark"}:
        theme = "light"

    light_logo = _image_data_uri("journal-logo-black-1600x400.png")
    dark_logo = _image_data_uri("journal-logo-white-1600x400.png")
    selected_logo = dark_logo if theme == "dark" else light_logo
    initial_theme = theme

    return f"""
    <style>
    .journal-logo-{placement} {{
        display: block;
        width: 100%;
        max-width: {"24rem" if placement == "login" else "15rem"};
        height: auto;
        object-fit: contain;
        object-position: left center;
    }}
    [data-theme="dark"] .journal-logo-initial-light {{
        filter: invert(1) hue-rotate(180deg);
    }}
    [data-theme="light"] .journal-logo-initial-dark {{
        filter: invert(1) hue-rotate(180deg);
    }}
    @media (prefers-color-scheme: dark) {{
        html:not([data-theme="light"]) .journal-logo-initial-light {{
            filter: invert(1) hue-rotate(180deg);
        }}
    }}
    @media (prefers-color-scheme: light) {{
        html:not([data-theme="dark"]) .journal-logo-initial-dark {{
            filter: invert(1) hue-rotate(180deg);
        }}
    }}
    </style>
    <img class="journal-logo-{placement} journal-logo-initial-{initial_theme}"
         src="{selected_logo}"
         alt="Journal — Adaptive Endurance Training">
    """


def journal_sidebar_button_css(*, theme: str = "light") -> str:
    """Style the Dashboard button with the matching Journal wordmark."""

    if theme not in {"light", "dark"}:
        theme = "light"
    filename = (
        "journal-logo-white-1600x400.png"
        if theme == "dark"
        else "journal-logo-black-1600x400.png"
    )
    logo = _image_data_uri(filename)
    inverse_theme = "dark" if theme == "light" else "light"

    return f"""
    <style>
    .st-key-sidebar_brand button,
    .st-key-sidebar_brand button:hover,
    .st-key-sidebar_brand button:focus,
    .st-key-sidebar_brand button:active {{
        width: 15rem !important;
        height: 3.25rem !important;
        padding: 0 !important;
        background-color: transparent !important;
        background-image: url("{logo}") !important;
        background-position: left center !important;
        background-repeat: no-repeat !important;
        background-size: contain !important;
    }}
    [data-theme="{inverse_theme}"] .st-key-sidebar_brand button,
    [data-theme="{inverse_theme}"] .st-key-sidebar_brand button:hover,
    [data-theme="{inverse_theme}"] .st-key-sidebar_brand button:focus,
    [data-theme="{inverse_theme}"] .st-key-sidebar_brand button:active {{
        filter: invert(1) hue-rotate(180deg);
    }}
    .st-key-sidebar_brand button p {{
        visibility: hidden !important;
    }}
    </style>
    """
