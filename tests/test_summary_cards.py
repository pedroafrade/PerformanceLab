"""
PerformanceLab

Tests for reusable summary metric cards.
"""

from app.components.summary_cards import (
    summary_cards_html,
    summary_cards_styles,
)


def test_builds_summary_metric_cards():

    result = summary_cards_html(
        (
            (
                "calendar_month",
                "Horizon",
                "10 weeks",
            ),
            (
                "monitoring",
                "Planned load",
                "8026 AU",
            ),
        )
    )

    assert (
        result.count(
            'class="summary-metric-card '
        )
        == 2
    )

    assert result.count("<svg ") == 2
    assert "Horizon" in result
    assert "10 weeks" in result
    assert "Planned load" in result
    assert "8026 AU" in result

    assert (
        ">calendar_month<"
        not in result
    )

    assert (
        ">monitoring<"
        not in result
    )


def test_uses_fallback_for_unknown_icon():

    result = summary_cards_html(
        (
            (
                "unknown_icon",
                "Example",
                "123",
            ),
        )
    )

    assert "<svg " in result
    assert "<circle " in result
    assert "Example" in result


def test_escapes_summary_card_content():

    result = summary_cards_html(
        (
            (
                "terrain",
                "<Elevation>",
                "1000 < 1200",
            ),
        )
    )

    assert "<Elevation>" not in result
    assert "&lt;Elevation&gt;" in result
    assert "1000 &lt; 1200" in result


def test_returns_empty_html_without_cards():

    assert (
        summary_cards_html(
            ()
        )
        == ""
    )


def test_exposes_summary_card_styles():

    styles = (
        summary_cards_styles()
    )

    assert (
        ".summary-metric-grid"
        in styles
    )

    assert (
        ".summary-metric-card"
        in styles
    )

    assert (
        ".summary-metric-icon svg"
        in styles
    )

    assert (
        ".summary-metric-value"
        in styles
    )

def test_adds_metric_specific_card_classes():

    result = summary_cards_html(
        (
            (
                "calendar_month",
                "Horizon",
                "9 weeks",
            ),
            (
                "monitoring",
                "Planned load",
                "8435 AU",
            ),
            (
                "route",
                "Max distance",
                "38 km/week",
            ),
            (
                "terrain",
                "Max elevation",
                "950 m/week",
            ),
        )
    )

    assert (
        "summary-metric-card-calendar-month"
        in result
    )

    assert (
        "summary-metric-card-monitoring"
        in result
    )

    assert (
        "summary-metric-card-route"
        in result
    )

    assert (
        "summary-metric-card-terrain"
        in result
    )


def test_normalizes_summary_card_icon_class():

    result = summary_cards_html(
        (
            (
                "Example_ICON",
                "Example",
                "123",
            ),
        )
    )

    assert (
        "summary-metric-card-example-icon"
        in result
    )


def test_summary_styles_define_metric_accents():

    styles = (
        summary_cards_styles()
    )

    assert (
        ".summary-metric-card::before"
        in styles
    )

    assert (
        ".summary-metric-card-calendar-month"
        in styles
    )

    assert (
        ".summary-metric-card-monitoring"
        in styles
    )

    assert (
        ".summary-metric-card-route"
        in styles
    )

    assert (
        ".summary-metric-card-terrain"
        in styles
    )