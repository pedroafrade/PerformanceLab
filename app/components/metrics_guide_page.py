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
    inputs: str = ""
    formula: str = ""
    example: str = ""
    limitations: str = ""
    implementation: str = ""


GUIDE_ENTRIES = (
    GuideEntry(
        "Acute load (ATL)", ("fatigue", "ATL"), "Training load",
        "A short-term view of recent training load.",
        "It reacts faster than chronic load. PerformanceLab uses it together "
        "with CTL when describing current form; it is an estimate, not a direct measurement.",
        inputs="One training-load value per calendar day, in arbitrary load units (AU); rest and missing days are zero.",
        formula="α = 1 − exp(−1/7); ATL(today) = ATL(previous) + α × (daily load − ATL(previous)).",
        example="Starting from zero, a 100 AU day produces ATL ≈ 13.31 AU.",
        limitations="The 7-day value is an exponential time constant, not a simple seven-day average.",
        implementation="performancelab.analysis.performance.atl · DEFAULT_ATL_DAYS = 7",
    ),
    GuideEntry(
        "Chronic load (CTL)", ("fitness", "CTL"), "Training load",
        "A longer-term view of accumulated training load.",
        "It changes more gradually than ATL and represents training consistency, "
        "not a laboratory measurement of fitness.",
        inputs="The same chronological daily AU series used by ATL; rest and missing days are zero.",
        formula="α = 1 − exp(−1/42); CTL(today) = CTL(previous) + α × (daily load − CTL(previous)).",
        example="Starting from zero, a 100 AU day produces CTL ≈ 2.35 AU.",
        limitations="The 42-day value is an exponential time constant; older load remains with progressively less weight.",
        implementation="performancelab.analysis.performance.ctl · DEFAULT_CTL_DAYS = 42",
    ),
    GuideEntry(
        "Form (TSB)", ("form", "freshness", "TSB"), "Training load",
        "The balance between chronic and acute load.",
        "Positive and negative values describe the calculated balance between "
        "longer-term load and recent fatigue. Context and trend matter more than one value.",
        inputs="CTL and ATL calculated for the same point in time, both in AU.",
        formula="TSB = CTL − ATL.",
        example="After the first 100 AU day from zero: 2.35 − 13.31 ≈ −10.96 AU.",
        limitations="A positive value does not by itself prove readiness, and a negative value does not diagnose excessive fatigue.",
        implementation="performancelab.analysis.performance.tsb · training_stress_balance",
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
            if entry.inputs:
                st.markdown(f"**Inputs and units:** {entry.inputs}")
            if entry.formula:
                st.markdown(f"**Formula used:** `{entry.formula}`")
            if entry.example:
                st.markdown(f"**Example:** {entry.example}")
            if entry.limitations:
                st.markdown(f"**Limitations:** {entry.limitations}")
            if entry.implementation:
                st.caption(f"Verified against: {entry.implementation}")
            else:
                st.caption("Formula and coefficients still require implementation verification.")
