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


def journal_logo_html(*, placement: str) -> str:
    """Render the appropriate Journal wordmark for the active colour scheme."""

    if placement not in {"login", "sidebar"}:
        raise ValueError("placement must be 'login' or 'sidebar'.")

    light_logo = _image_data_uri("journal-logo-black-1600x400.png")
    dark_logo = _image_data_uri("journal-logo-white-1600x400.png")

    return f"""
    <style>
    .journal-logo-{placement} {{
        display: block;
        width: 100%;
        max-width: {"24rem" if placement == "login" else "12.5rem"};
        height: auto;
        object-fit: contain;
        object-position: left center;
    }}
    </style>
    <picture aria-label="Journal — Adaptive Endurance Training">
        <source media="(prefers-color-scheme: dark)" srcset="{dark_logo}">
        <img class="journal-logo-{placement}" src="{light_logo}"
             alt="Journal — Adaptive Endurance Training">
    </picture>
    """
