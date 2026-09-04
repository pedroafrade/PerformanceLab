"""
Tests for the shared current-state summary.
"""

from datetime import datetime

from app.components.current_state_summary import (
    CurrentStateSummaryData,
    current_state_summary_html,
)


def test_builds_current_state_summary():

    summary = CurrentStateSummaryData(
        recovery_score=19.0,
        recovery_balance=19.1,
        recovery_status=(
            "Recovery needed"
        ),
        chronic_load=247.0,
        acute_load=329.9,
        load_status="High load",
        form=-30.9,
        recovery_recommendation=(
            "Prioritise recovery before training."
        ),
        recovery_reference_time=datetime(
            2026,
            8,
            13,
            23,
            7,
        ),
        hours_since_last_workout=34.0,
        recovery_is_time_aware=True,
    )

    result = current_state_summary_html(
        summary
    )

    assert (
        "Estimated recovery"
        in result
    )
    assert "Chronic load" in result
    assert "Form" in result
    assert "Acute load" in result

    assert "19" in result
    assert "247" in result
    assert "-30.9" in result
    assert "330" in result

    assert "Balance +19.1" in result
    assert (
        "34 h since last session"
        in result
    )
    assert "Updated 23:07" in result

    compact_result = current_state_summary_html(
        summary,
        compact=True,
    )
    assert "current-state-grid-compact" in compact_result
    assert 'role="progressbar"' in compact_result
    assert 'aria-valuenow="19"' in compact_result
    assert "width:19.0%" in compact_result
    assert "Prioritise recovery before training." in compact_result
