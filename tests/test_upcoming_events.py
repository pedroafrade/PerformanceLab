"""Tests for the event presentation shared by Dashboard and Calendar."""

from datetime import date
from types import SimpleNamespace

from app.components.upcoming_events import upcoming_events_html


def test_renders_compact_next_event_and_full_upcoming_events():
    event = SimpleNamespace(
        name="Trail Pé Firme",
        event_date=date(2026, 9, 27),
        days_remaining=23,
        sport="Trail Running",
        distance=25.0,
        elevation_gain=900.0,
        priority="A",
        location="Sintra",
        country="Portugal",
        target_time=None,
    )

    compact = upcoming_events_html((event,), compact=True)
    complete = upcoming_events_html((event,))

    assert "upcoming-events-compact" in compact
    assert "Trail Pé Firme" in compact
    assert "25 km" in compact
    assert "+900 m" in compact
    assert "23d left" in compact
    assert "Sintra · Portugal" in compact
    assert "upcoming-events-compact" not in complete


def test_renders_empty_event_state():
    assert "No upcoming events." in upcoming_events_html(())
