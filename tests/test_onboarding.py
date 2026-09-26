"""Regression coverage for first-login athlete onboarding."""

from pathlib import Path

import pytest

from performancelab import Athlete
from performancelab.storage.json import athlete_from_dict, athlete_to_dict


ROOT = Path(__file__).resolve().parents[1]


def test_old_athlete_snapshots_do_not_require_onboarding():
    athlete = Athlete(name="Existing athlete")
    payload = athlete_to_dict(athlete)
    payload["athlete"].pop("onboarding_completed")
    payload["athlete"].pop("onboarding_step")

    restored = athlete_from_dict(payload)

    assert restored.onboarding_completed is None
    assert restored.onboarding_step == 1


def test_pending_onboarding_round_trips_with_athlete_snapshot():
    athlete = Athlete(
        name="New athlete",
        onboarding_completed=False,
        onboarding_step=4,
    )

    restored = athlete_from_dict(athlete_to_dict(athlete))

    assert restored.onboarding_completed is False
    assert restored.onboarding_step == 4


def test_onboarding_step_is_validated():
    with pytest.raises(ValueError, match="between 1 and 5"):
        Athlete(onboarding_step=6)


def test_streamlit_flow_precedes_dashboard_rendering():
    source = (ROOT / "app" / "app.py").read_text(encoding="utf-8")

    onboarding = 'if athlete.onboarding_completed is False:'
    dashboard = 'if page == "dashboard":'

    assert onboarding in source
    assert "show_onboarding_dialog(" in source
    assert source.index(onboarding) < source.index(dashboard)


def test_onboarding_reuses_existing_event_and_import_components():
    source = (
        ROOT / "app" / "components" / "onboarding.py"
    ).read_text(encoding="utf-8")

    assert "EventEntry(" in source
    assert "Event(" in source
    assert "show_import_panel(" in source
    assert "on_import_activities=on_import_activities" in source
    assert '"Skip setup"' in source
    assert '"Finish setup"' in source
