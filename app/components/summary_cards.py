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

        card_parts.append(
            (
                '<div class="summary-metric-card">'
                '<div class="summary-metric-icon">'
                f"{_icon_svg(str(icon))}"
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
    gap: 0.75rem;
    width: 100%;
}

.summary-metric-card {
    display: flex;
    align-items: center;
    min-width: 0;
    min-height: 76px;
    padding: 0.85rem 0.9rem;
    gap: 0.75rem;
    border: 1px solid rgba(128, 128, 128, 0.22);
    border-radius: 0.75rem;
    background: rgba(128, 128, 128, 0.035);
    box-sizing: border-box;
}

.summary-metric-icon {
    display: flex;
    flex: 0 0 auto;
    align-items: center;
    justify-content: center;
    width: 38px;
    height: 38px;
    border-radius: 0.65rem;
    background: rgba(128, 128, 128, 0.11);
}

.summary-metric-icon svg {
    display: block;
    width: 24px;
    height: 24px;
}

.summary-metric-content {
    min-width: 0;
}

.summary-metric-label {
    overflow: hidden;
    margin-bottom: 0.16rem;
    font-size: 0.72rem;
    font-weight: 600;
    line-height: 1.1;
    opacity: 0.66;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.summary-metric-value {
    overflow: hidden;
    font-size: 1rem;
    font-weight: 700;
    line-height: 1.2;
    text-overflow: ellipsis;
    white-space: nowrap;
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