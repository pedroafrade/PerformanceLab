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
