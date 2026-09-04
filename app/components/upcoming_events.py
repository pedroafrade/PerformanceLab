"""Shared presentation for the next and upcoming events."""

from html import escape


def _event_details(event) -> str:
    values = (
        getattr(event, "sport", None),
        f"{event.distance:g} km" if getattr(event, "distance", None) is not None else None,
        f"+{event.elevation_gain:g} m" if getattr(event, "elevation_gain", None) is not None else None,
    )
    return " · ".join(value for value in values if value) or "Event"


def upcoming_events_html(events, *, compact: bool = False) -> str:
    """Render the same factual event component at two densities."""

    events = tuple(event for event in events if event is not None)
    if not events:
        return '<div class="upcoming-events-empty">No upcoming events.</div>'

    items = []
    for event in events[:1] if compact else events:
        priority = getattr(event, "priority", None)
        location = " · ".join(
            value for value in (
                getattr(event, "location", None),
                getattr(event, "country", None),
            ) if value
        )
        target = getattr(event, "target_time", None)
        countdown = getattr(event, "days_remaining", None)
        date_label = f"{event.event_date:%d %b %Y}"
        if countdown is not None:
            date_label += " · today" if countdown == 0 else (
                " · tomorrow" if countdown == 1 else f" · {countdown}d left"
            )

        metadata = [date_label]
        if location:
            metadata.append(location)
        if target:
            metadata.append(f"Target {target}")

        items.append(
            '<article class="upcoming-event">'
            '<div class="upcoming-event-heading">'
            f'<strong>{escape(str(event.name or "Event"))}</strong>'
            + (f'<span>{escape(str(priority).upper())}</span>' if priority else "")
            + "</div>"
            f'<div class="upcoming-event-details">{escape(_event_details(event))}</div>'
            f'<div class="upcoming-event-meta">{escape(" · ".join(metadata))}</div>'
            "</article>"
        )

    density = " upcoming-events-compact" if compact else ""
    return f'<div class="upcoming-events{density}">{"".join(items)}</div>'


def upcoming_events_styles() -> str:
    """Return styles shared by Dashboard and Calendar."""

    return """
    .upcoming-events {display:flex;flex-direction:column;gap:.45rem;}
    .upcoming-event {padding:.55rem .65rem;border:1px solid rgba(128,128,128,.2);
        border-radius:.55rem;background:rgba(128,128,128,.015);}
    .upcoming-event-heading {display:flex;align-items:center;justify-content:space-between;
        gap:.5rem;font-size:.82rem;}
    .upcoming-event-heading span {font-size:.58rem;font-weight:750;opacity:.62;}
    .upcoming-event-details {margin-top:.14rem;font-size:.67rem;opacity:.68;}
    .upcoming-event-meta {margin-top:.3rem;font-size:.62rem;line-height:1.35;opacity:.58;}
    .upcoming-events-empty {font-size:.72rem;opacity:.62;}
    .upcoming-events-compact .upcoming-event {border:0;padding:.25rem 0;background:transparent;}
    .upcoming-events-compact .upcoming-event-heading {font-size:1rem;}
    """
