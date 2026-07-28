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

def test_import_panel_merges_workout_into_history():

    workout = object()
    stored_workout = object()

    calls = {}

    class FakeHistory:

        def merge(
            self,
            received_workout,
        ):

            calls["workout"] = (
                received_workout
            )

            return (
                stored_workout,
                False,
            )

    athlete = SimpleNamespace(
        history=FakeHistory(),
    )

    added = (
        import_panel._store_imported_workout(
            workout,
            athlete,
        )
    )

    assert calls["workout"] is workout
    assert added is False

def test_imports_multiple_files_and_counts_results(
    monkeypatch,
):

    new_file = object()
    existing_file = object()
    failed_file = object()

    def fake_import(
        uploaded_file,
        athlete,
    ):

        if uploaded_file is new_file:
            return True

        if uploaded_file is existing_file:
            return False

        raise ValueError(
            "Invalid activity"
        )

    monkeypatch.setattr(
        import_panel,
        "_import_uploaded_file",
        fake_import,
    )

    counts = (
        import_panel._import_uploaded_files(
            [
                new_file,
                existing_file,
                failed_file,
            ],
            SimpleNamespace(),
        )
    )

    assert counts == (
        1,
        1,
        1,
    )