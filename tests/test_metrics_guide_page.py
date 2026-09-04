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
