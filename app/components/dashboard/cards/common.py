"""
Dashboard card helpers.
"""

from datetime import timedelta


# ======================================================
# Formatting
# ======================================================

def format_duration(
    value: timedelta | None,
) -> str:
    """
    Formats a duration for display.
    """

    if value is None:

        return "—"

    total_seconds = int(
        value.total_seconds()
    )

    hours, remainder = divmod(
        total_seconds,
        3600,
    )

    minutes = remainder // 60

    return (
        f"{hours}h "
        f"{minutes:02d}m"
    )