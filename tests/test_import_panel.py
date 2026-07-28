from types import SimpleNamespace

import app.components.import_panel as import_panel


def test_import_panel_uses_athlete_profile_for_rpe(
    monkeypatch,
):

    calls = {}

    def fake_estimator(
        workout,
        *,
        max_hr,
        resting_hr,
    ):

        calls["workout"] = workout
        calls["max_hr"] = max_hr
        calls["resting_hr"] = resting_hr

        return 6.0

    monkeypatch.setattr(
        import_panel,
        "estimate_workout_rpe",
        fake_estimator,
    )

    workout = object()

    athlete = SimpleNamespace(
        max_hr=190,
        resting_hr=50,
    )

    estimate = (
        import_panel._estimate_imported_workout_rpe(
            workout,
            athlete,
        )
    )

    assert estimate == 6.0
    assert calls["workout"] is workout
    assert calls["max_hr"] == 190
    assert calls["resting_hr"] == 50