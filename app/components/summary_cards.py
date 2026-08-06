"""
PerformanceLab

Reusable summary metric cards.
"""

from html import escape


_ICON_PATHS = {
    "calendar_month": (
        '<rect x="3" y="5" width="18" height="16" '
        'rx="2"></rect>'
        '<path d="M16 3v4"></path>'
        '<path d="M8 3v4"></path>'
        '<path d="M3 10h18"></path>'
    ),
    "monitoring": (
        '<path d="M3 3v18h18"></path>'
        '<path d="m7 16 4-5 4 3 5-7"></path>'
    ),
    "route": (
        '<circle cx="6" cy="19" r="2"></circle>'
        '<circle cx="18" cy="5" r="2"></circle>'
        '<path d="M8 19h3a3 3 0 0 0 3-3V8'
        'a3 3 0 0 1 3-3"></path>'
    ),
    "terrain": (
        '<path d="m3 20 7-12 4 7 2-3 5 8"></path>'
        '<path d="M8.5 10.5 10 13l1.5-2.5"></path>'
    ),
}


def _icon_svg(
    icon: str,
) -> str:
    """
    Returns a safe inline SVG for one known icon.
    """

    paths = _ICON_PATHS.get(
        str(icon)
    )

    if paths is None:
        paths = (
            '<circle cx="12" cy="12" r="8">'
            "</circle>"
        )

    return (
        '<svg '
        'viewBox="0 0 24 24" '
        'width="24" '
        'height="24" '
        'fill="none" '
        'stroke="currentColor" '
        'stroke-width="1.8" '
        'stroke-linecap="round" '
        'stroke-linejoin="round" '
        'aria-hidden="true">'
        f"{paths}"
        "</svg>"
    )


def summary_cards_html(
    cards,
) -> str:
    """
    Builds presentation-ready summary cards.

    Each card contains:
    icon, label and value.
    """

    if not cards:
        return ""

    card_parts = []

    for icon, label, value in cards:

        icon_name = str(
            icon
        )

        safe_icon_class = (
            icon_name
            .strip()
            .lower()
            .replace(
                "_",
                "-",
            )
        )

        card_parts.append(
            (
                '<div class="summary-metric-card '
                f'summary-metric-card-{escape(safe_icon_class)}">'
                '<div class="summary-metric-icon">'
                f"{_icon_svg(icon_name)}"
                "</div>"
                '<div class="summary-metric-content">'
                '<div class="summary-metric-label">'
                f"{escape(str(label))}"
                "</div>"
                '<div class="summary-metric-value">'
                f"{escape(str(value))}"
                "</div>"
                "</div>"
                "</div>"
            )
        )

    return (
        '<div class="summary-metric-grid">'
        f'{"".join(card_parts)}'
        "</div>"
    )


def summary_cards_styles() -> str:
    """
    Returns the shared summary-card CSS.
    """

    return """
.summary-metric-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 0.65rem;
    width: 100%;
}

.summary-metric-card {
    position: relative;
    display: flex;
    align-items: center;
    min-width: 0;
    min-height: 70px;
    padding: 0.7rem 0.78rem;
    gap: 0.68rem;
    border: 1px solid rgba(128, 128, 128, 0.22);
    border-radius: 0.7rem;
    background:
        linear-gradient(
            135deg,
            rgba(128, 128, 128, 0.045),
            rgba(128, 128, 128, 0.018)
        );
    box-sizing: border-box;
    overflow: hidden;
}

.summary-metric-card::before {
    content: "";
    position: absolute;
    top: 0.7rem;
    bottom: 0.7rem;
    left: 0;
    width: 2px;
    border-radius: 0 2px 2px 0;
    background: currentColor;
    opacity: 0.7;
}

.summary-metric-icon {
    display: flex;
    flex: 0 0 auto;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    border: 1px solid currentColor;
    border-radius: 0.6rem;
    background: rgba(128, 128, 128, 0.07);
    box-sizing: border-box;
}

.summary-metric-icon svg {
    display: block;
    width: 21px;
    height: 21px;
}

.summary-metric-content {
    min-width: 0;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.summary-metric-label {
    overflow: hidden;
    margin-bottom: 0.14rem;
    font-size: 0.64rem;
    font-weight: 650;
    letter-spacing: 0.015em;
    line-height: 1;
    opacity: 0.58;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.summary-metric-value {
    overflow: hidden;
    font-size: 1.12rem;
    font-weight: 750;
    letter-spacing: -0.015em;
    line-height: 1.08;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.summary-metric-card-calendar-month,
.summary-metric-card-monitoring,
.summary-metric-card-route,
.summary-metric-card-terrain {
    color: currentColor;
}

.summary-metric-card .summary-metric-label,
.summary-metric-card .summary-metric-value {
    color: var(--text-color);
}

@media (max-width: 1100px) {
    .summary-metric-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

@media (max-width: 650px) {
    .summary-metric-grid {
        grid-template-columns: 1fr;
    }
}
"""