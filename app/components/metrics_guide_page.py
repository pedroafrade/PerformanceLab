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
    period: str = ""
    interpretation: str = ""
    calculation_type: str = "Deterministic"


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
        period="All calendar days, with a 7-day exponential time constant.",
        interpretation="Higher ATL means more recent calculated load.",
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
        period="All calendar days, with a 42-day exponential time constant.",
        interpretation="CTL is accumulated-load context rather than measured fitness.",
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
        period="The same reference instant used for ATL and CTL.",
        interpretation="Negative means recent calculated load exceeds chronic load.",
    ),
    GuideEntry(
        "RPE", ("effort", "perceived exertion"), "Activities",
        "The athlete's rating of how hard a session felt.",
        "The displayed value is rounded to a whole unit in Activities, while the "
        "stored precision remains available to calculations.",
        inputs="Duration in minutes and athlete-entered effective RPE.",
        formula="Completed session load = duration in minutes × effective RPE.",
        example="A 60-minute activity at effective RPE 5 contributes 300 AU.",
        limitations="RPE is subjective; missing duration or RPE means load cannot be calculated.",
        implementation="performancelab.training.load.workout_load",
        period="Per completed activity.",
        interpretation="Use trends and session context rather than an isolated value.",
    ),
    GuideEntry(
        "Planned session load", ("planned load", "session RPE", "AU"), "Plans",
        "An estimate of future session load from duration and planned intensity.",
        "Semantic intensity maps to estimated RPE; running elevation adds a conservative multiplier.",
        inputs="Duration in minutes, semantic intensity, sport and elevation gain in metres.",
        formula="minutes × planned RPE × elevation factor; running adds 5% per 100 m, capped at 30%.",
        example="60 min Easy (RPE 3) with 200 m running gain = 198 AU.",
        limitations="It is a pre-session estimate and ignores sessions without recognised intensity or duration.",
        implementation="performancelab.training.load.planned_workout_load · PLANNED_INTENSITY_RPE",
        period="Per planned session; weekly load sums estimable sessions.",
        interpretation="Use for comparing plan changes, not as a physiological measurement.",
    ),
    GuideEntry(
        "Plan Builder safeguards", ("35%", "20%", "blocked", "caution"), "Plans",
        "Deterministic checks applied to the complete edited draft before saving.",
        "The assessment checks weekly load, demanding-session recovery, long-run spacing and race taper.",
        inputs="Baseline and revised sessions, dates, estimated AU and current date.",
        formula="Block >35% and at least +100 AU; caution >20% and at least +50 AU. New weeks block at 150 AU and caution at 75 AU.",
        example="634 → 879 AU is +245 AU and +38.6%, so the weekly-load rule blocks the draft.",
        limitations="Conservative product rules, not medical guarantees; races are excluded from weekly-load comparison.",
        implementation="performancelab.training.planning.plan_builder_assessment.assess_plan_builder_change",
        period="Each complete draft, grouped into Monday–Sunday weeks.",
        interpretation="A block prevents persistence; a caution alone does not.",
    ),
    GuideEntry(
        "Typical Week", ("habit", "routine", "six months"), "Plans",
        "A descriptive view of recurring completed-session days and start hours.",
        "It reports observed habits locally and does not prescribe or move sessions.",
        inputs="Completed-session title, sport, date and start hour.",
        formula="At least 3 observations; modal weekday must contain at least 40% of them.",
        example="NRTV on Wednesday in 7 of 7 matches appears at Wednesday's modal hour.",
        limitations="Sparse or changing routines may not appear; frequency does not prove safety.",
        implementation="app.components.plan_page._typical_week",
        period="Rolling 183 days ending on the reference day.",
        interpretation="A preference signal, separate from the safety assessment.",
    ),
    GuideEntry(
        "Estimated recovery", ("recovery", "readiness"), "Recovery",
        "A calculated indication of readiness based on available training data.",
        "It supports training decisions but is not a diagnosis or a medical assessment. "
        "Missing or older inputs reduce what can safely be concluded.",
        inputs="ATL and CTL at the same reference instant.",
        formula="Recovery score = max(0, min(CTL − ATL + 50, 100)).",
        example="CTL 40 and ATL 55 gives TSB −15 and recovery score 35.",
        limitations="A bounded load-derived estimate; it does not include every cause of fatigue or diagnose illness.",
        implementation="performancelab.analysis.time_aware_load.TimeAwareTrainingLoad.recovery_score",
        period="Current reference instant using available load history.",
        interpretation="Read with load timing, symptoms and the athlete's own judgement.",
    ),
    GuideEntry(
        "Training-plan phases", ("base", "peak", "taper", "regeneration"), "Plans",
        "Blocks that organise how training emphasis changes toward an objective.",
        "Objectives, events, availability, recent execution and constraints can influence "
        "phase content. Training Coach text does not itself change the plan.",
        inputs="Plan horizon, events, phase dates, sessions and constraints.",
        limitations="Phase labels summarise intent and do not guarantee adaptation or outcomes.",
        implementation="Deterministic plan/domain objects; Training Coach supplies explanation only.",
        period="Across the active plan horizon.",
        interpretation="Read the phase with its sessions, load and event context.",
        calculation_type="Mixed: deterministic plan + Coach explanation",
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
            st.caption(f"Type: {entry.calculation_type}")
            st.write(entry.details)
            if entry.inputs:
                st.markdown(f"**Inputs and units:** {entry.inputs}")
            if entry.formula:
                st.markdown(f"**Formula used:** `{entry.formula}`")
            if entry.period:
                st.markdown(f"**Period/window:** {entry.period}")
            if entry.example:
                st.markdown(f"**Example:** {entry.example}")
            if entry.limitations:
                st.markdown(f"**Limitations:** {entry.limitations}")
            if entry.interpretation:
                st.markdown(f"**Interpretation:** {entry.interpretation}")
            if entry.implementation:
                st.caption(f"Verified against: {entry.implementation}")
            else:
                st.caption("Formula and coefficients still require implementation verification.")
