"""Searchable plain-language guide to PerformanceLab metrics and plans."""

from dataclasses import dataclass

import streamlit as st


@dataclass(frozen=True)
class GuideEntry:
    name: str
    aliases: tuple[str, ...]
    category: str
    summary: str
    details: str


GUIDE_ENTRIES = (
    GuideEntry(
        "Acute load (ATL)", ("fatigue", "ATL"), "Training load",
        "A short-term view of recent training load.",
        "It reacts faster than chronic load. PerformanceLab uses it together "
        "with CTL when describing current form; it is an estimate, not a direct measurement.",
    ),
    GuideEntry(
        "Chronic load (CTL)", ("fitness", "CTL"), "Training load",
        "A longer-term view of accumulated training load.",
        "It changes more gradually than ATL and represents training consistency, "
        "not a laboratory measurement of fitness.",
    ),
    GuideEntry(
        "Form (TSB)", ("form", "freshness", "TSB"), "Training load",
        "The balance between chronic and acute load.",
        "Positive and negative values describe the calculated balance between "
        "longer-term load and recent fatigue. Context and trend matter more than one value.",
    ),
    GuideEntry(
        "RPE", ("effort", "perceived exertion"), "Activities",
        "The athlete's rating of how hard a session felt.",
        "The displayed value is rounded to a whole unit in Activities, while the "
        "stored precision remains available to calculations.",
    ),
    GuideEntry(
        "Estimated recovery", ("recovery", "readiness"), "Recovery",
        "A calculated indication of readiness based on available training data.",
        "It supports training decisions but is not a diagnosis or a medical assessment. "
        "Missing or older inputs reduce what can safely be concluded.",
    ),
    GuideEntry(
        "Training-plan phases", ("base", "peak", "taper", "regeneration"), "Plans",
        "Blocks that organise how training emphasis changes toward an objective.",
        "Objectives, events, availability, recent execution and constraints can influence "
        "phase content. Training Coach text does not itself change the plan.",
    ),
)


def filter_guide_entries(query: str, category: str = "All") -> tuple[GuideEntry, ...]:
    """Filter entries without depending on Streamlit state."""

    normalized = query.strip().casefold()
    return tuple(
        entry for entry in GUIDE_ENTRIES
        if (category == "All" or entry.category == category)
        and (
            not normalized
            or normalized in " ".join((entry.name, *entry.aliases, entry.summary)).casefold()
        )
    )


def show_metrics_guide_page() -> None:
    """Render the guide in the normal desktop and mobile document flow."""

    st.title("Metrics & Plans Guide")
    st.caption(
        "Plain-language explanations of the metrics and planning concepts used "
        "throughout PerformanceLab. Technical detail is added only after code verification."
    )

    search_column, category_column = st.columns((2, 1), gap="small")
    with search_column:
        query = st.text_input(
            "Search the guide",
            placeholder="Try ATL, recovery, RPE or taper",
        )
    with category_column:
        categories = ("All", *sorted({entry.category for entry in GUIDE_ENTRIES}))
        category = st.selectbox("Category", categories)

    entries = filter_guide_entries(query, category)
    if not entries:
        st.info("No matching concept was found.")
        return

    for entry in entries:
        with st.expander(f"{entry.name} · {entry.category}"):
            st.markdown(f"**In simple terms:** {entry.summary}")
            st.write(entry.details)
            st.caption("Formula and verified coefficients will be added from the implementation inventory.")
