from gzip import compress

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

    new_file = SimpleNamespace(
        name="new.fit"
    )

    existing_file = SimpleNamespace(
        name="existing.fit"
    )

    failed_file = SimpleNamespace(
        name="failed.fit"
    )

    def fake_import(
        uploaded_file,
        athlete,
        strava_titles=None,
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

def test_prepares_compressed_fit_upload():

    uploaded_file = SimpleNamespace(
        name="strava_activity.fit.gz",
        getvalue=lambda: compress(
            b"FIT activity data"
        ),
    )

    source, extension = (
        import_panel._prepare_uploaded_file(
            uploaded_file
        )
    )

    assert extension == "fit"
    assert source.name == (
        "strava_activity.fit"
    )
    assert source.read() == (
        b"FIT activity data"
    )

def test_reads_strava_activity_titles():

    csv_file = SimpleNamespace(
        name="activities.csv",
        getvalue=lambda: (
            (
                '"Activity Name","Filename"\n'
                '"Morning Run",'
                '"activities/20284257187.fit.gz"\n'
            ).encode("utf-8")
        ),
    )

    titles = (
        import_panel._read_strava_titles(
            [csv_file]
        )
    )

    assert titles == {
        "20284257187.fit.gz": (
            "Morning Run"
        )
    }


def test_uses_strava_activity_title():

    uploaded_file = SimpleNamespace(
        name="20284257187.fit.gz",
    )

    title = import_panel._activity_title(
        uploaded_file,
        {
            "20284257187.fit.gz": (
                "Morning Run"
            ),
        },
    )

    assert title == "Morning Run"