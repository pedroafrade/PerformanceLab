from app.components.metrics_guide_page import (
    GUIDE_ENTRIES,
    filter_guide_entries,
)


def test_initial_guide_has_unique_named_entries_across_core_categories():
    names = [entry.name for entry in GUIDE_ENTRIES]
    assert len(names) == len(set(names))
    assert {entry.category for entry in GUIDE_ENTRIES} >= {
        "Training load", "Activities", "Recovery", "Plans"
    }


def test_search_matches_names_aliases_and_summaries_case_insensitively():
    assert [entry.name for entry in filter_guide_entries("atl")] == ["Acute load (ATL)"]
    assert [entry.name for entry in filter_guide_entries("FRESHNESS")] == ["Form (TSB)"]
    assert [entry.name for entry in filter_guide_entries("athlete's rating")] == ["RPE"]


def test_category_and_query_filters_are_combined():
    assert filter_guide_entries("load", "Activities") == ()
    assert len(filter_guide_entries("", "Training load")) == 3


def test_no_entry_claims_to_be_medical_advice():
    recovery = next(entry for entry in GUIDE_ENTRIES if entry.name == "Estimated recovery")
    assert "not a diagnosis" in recovery.details


def test_load_entries_document_verified_constants_and_formulae():
    by_name = {entry.name: entry for entry in GUIDE_ENTRIES}
    assert "exp(−1/7)" in by_name["Acute load (ATL)"].formula
    assert "DEFAULT_ATL_DAYS = 7" in by_name["Acute load (ATL)"].implementation
    assert "exp(−1/42)" in by_name["Chronic load (CTL)"].formula
    assert "DEFAULT_CTL_DAYS = 42" in by_name["Chronic load (CTL)"].implementation
    assert by_name["Form (TSB)"].formula == "TSB = CTL − ATL."


def test_documented_one_day_examples_match_the_real_calculations():
    from performancelab.analysis.performance.atl import atl
    from performancelab.analysis.performance.ctl import ctl
    from performancelab.analysis.performance.tsb import tsb

    acute = atl([100])
    chronic = ctl([100])
    balance = tsb(chronic, acute)
    assert round(acute, 2) == 13.31
    assert round(chronic, 2) == 2.35
    assert round(balance, 2) == -10.96


def test_planned_load_example_matches_the_real_calculation():
    from datetime import datetime, timedelta

    from performancelab.training.load import planned_workout_load
    from performancelab.training.planning import PlannedWorkout

    workout = PlannedWorkout(
        scheduled_at=datetime(2026, 9, 20, 9), sport="Running",
        title="Easy Run", duration=timedelta(minutes=60),
        intensity="Easy", elevation_gain=200,
    )
    entry = next(item for item in GUIDE_ENTRIES if item.name == "Planned session load")
    assert round(planned_workout_load(workout), 2) == 198.0
    assert "198 AU" in entry.example


def test_every_implemented_entry_documents_a_complete_contract():
    for entry in GUIDE_ENTRIES:
        if entry.implementation:
            assert entry.inputs
            assert entry.period
            assert entry.interpretation
            assert entry.limitations


def test_guide_separates_rules_from_coach_explanation():
    plan = next(item for item in GUIDE_ENTRIES if item.name == "Training-plan phases")
    safeguards = next(item for item in GUIDE_ENTRIES if item.name == "Plan Builder safeguards")
    assert plan.calculation_type == "Mixed: deterministic plan + Coach explanation"
    assert safeguards.calculation_type == "Deterministic"
