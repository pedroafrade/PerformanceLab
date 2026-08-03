"""
Tests for the Today page.
"""

from app.components import (
    today_page,
)
from app.components.today_page import (
    show_today_page,
)


def test_show_today_page_exists():

    assert callable(
        show_today_page
    )


def test_today_page_preserves_dashboard(
    monkeypatch,
):

    athlete = object()
    expected_result = object()
    received = []

    def fake_dashboard(
        current_athlete,
    ):

        received.append(
            current_athlete
        )

        return expected_result

    monkeypatch.setattr(
        today_page,
        "show_dashboard",
        fake_dashboard,
    )

    monkeypatch.setattr(
        today_page.st,
        "title",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        today_page.st,
        "caption",
        lambda *args, **kwargs: None,
    )

    result = show_today_page(
        athlete
    )

    assert result is expected_result
    assert received == [
        athlete
    ]