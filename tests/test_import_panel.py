from gzip import (
    compress,
)
from types import (
    SimpleNamespace,
)

import app.components.import_panel as import_panel

from performancelab import (
    Workout,
)
def minimal_fit_content():
    """
    Return a structurally valid empty FIT file for adapter tests.
    """

    header = bytearray(
        12
    )

    header[0] = 12

    header[
        4:8
    ] = (
        0
    ).to_bytes(
        4,
        byteorder="little",
    )

    header[
        8:12
    ] = b".FIT"

    return bytes(
        header
    )

def test_uses_athlete_profile_for_rpe(
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
        import_panel
        ._estimate_imported_workout_rpe(
            workout,
            athlete,
        )
    )

    assert estimate == 6.0
    assert calls["workout"] is workout
    assert calls["max_hr"] == 190
    assert calls["resting_hr"] == 50


def test_parses_fit_without_changing_athlete(
    monkeypatch,
):

    parsed_workout = Workout(
        workout_id="parsed-workout"
    )

    calls = {}

    class FakeFITImporter:

        def read(
            self,
            source,
        ):

            calls[
                "source"
            ] = source

            assert (
                source.closed
                is False
            )

            return parsed_workout

    monkeypatch.setattr(
        import_panel,
        "FITImporter",
        FakeFITImporter,
    )

    monkeypatch.setattr(
        import_panel,
        "_estimate_imported_workout_rpe",
        lambda workout, athlete: None,
    )

    uploaded_file = SimpleNamespace(
        name="morning.fit",
        getvalue=minimal_fit_content,
    )

    athlete = SimpleNamespace(
        history=object(),
    )

    result = (
        import_panel._import_uploaded_file(
            uploaded_file,
            athlete,
        )
    )

    assert result is parsed_workout
    assert (
        parsed_workout.info.title
        == "morning"
    )
    assert (
        calls[
            "source"
        ].closed
        is True
    )

def test_imports_valid_files_through_callback(
    monkeypatch,
):

    first_file = SimpleNamespace(
        name="first.fit"
    )
    second_file = SimpleNamespace(
        name="second.fit"
    )
    failed_file = SimpleNamespace(
        name="failed.fit"
    )

    first_workout = object()
    second_workout = object()

    def fake_import(
        uploaded_file,
        athlete,
        strava_titles=None,
    ):

        if uploaded_file is first_file:
            return first_workout

        if uploaded_file is second_file:
            return second_workout

        raise ValueError(
            "Invalid activity"
        )

    monkeypatch.setattr(
        import_panel,
        "_import_uploaded_file",
        fake_import,
    )

    calls = {}

    def on_import_activities(
        workouts,
    ):

        calls["workouts"] = workouts

        return SimpleNamespace(
            added_count=1,
            updated_count=1,
        )

    counts = (
        import_panel._import_uploaded_files(
            [
                first_file,
                second_file,
                failed_file,
            ],
            SimpleNamespace(),
            on_import_activities,
        )
    )

    assert counts == (
        1,
        1,
        1,
    )

    assert calls["workouts"] == (
        first_workout,
        second_workout,
    )


def test_no_valid_files_do_not_call_use_case(
    monkeypatch,
):

    failed_file = SimpleNamespace(
        name="failed.fit"
    )

    monkeypatch.setattr(
        import_panel,
        "_import_uploaded_file",
        lambda *args, **kwargs: (
            (_ for _ in ())
            .throw(
                ValueError(
                    "Invalid activity"
                )
            )
        ),
    )

    calls = {
        "count": 0,
    }

    def on_import_activities(
        workouts,
    ):

        calls["count"] += 1

    counts = (
        import_panel._import_uploaded_files(
            [
                failed_file,
            ],
            SimpleNamespace(),
            on_import_activities,
        )
    )

    assert counts == (
        0,
        0,
        1,
    )
    assert calls["count"] == 0


def test_skips_strava_csv_as_activity(
    monkeypatch,
):

    csv_file = SimpleNamespace(
        name="activities.csv",
        getvalue=lambda: (
            (
                '"Nome da atividade",'
                '"Nome do ficheiro"\n'
            ).encode(
                "utf-8"
            )
        ),
    )

    calls = {
        "count": 0,
    }

    def on_import_activities(
        workouts,
    ):

        calls["count"] += 1

    counts = (
        import_panel._import_uploaded_files(
            [
                csv_file,
            ],
            SimpleNamespace(),
            on_import_activities,
        )
    )

    assert counts == (
        0,
        0,
        0,
    )
    assert calls["count"] == 0


def test_imports_compressed_fit_in_memory(
    monkeypatch,
):

    fit_content = (
        minimal_fit_content()
    )

    parsed_workout = Workout(
        workout_id=(
            "compressed-workout"
        )
    )

    calls = {}

    class FakeFITImporter:

        def read(
            self,
            source,
        ):

            calls[
                "source"
            ] = source

            calls[
                "name"
            ] = source.name

            calls[
                "content"
            ] = source.read()

            return parsed_workout

    monkeypatch.setattr(
        import_panel,
        "FITImporter",
        FakeFITImporter,
    )

    monkeypatch.setattr(
        import_panel,
        "_estimate_imported_workout_rpe",
        lambda workout, athlete: None,
    )

    uploaded_file = SimpleNamespace(
        name="strava_activity.fit.gz",
        getvalue=lambda: compress(
            fit_content
        ),
    )

    result = (
        import_panel._import_uploaded_file(
            uploaded_file,
            SimpleNamespace(),
        )
    )

    assert result is parsed_workout

    assert (
        calls[
            "name"
        ]
        == "strava_activity.fit"
    )

    assert (
        calls[
            "content"
        ]
        == fit_content
    )

    assert (
        calls[
            "source"
        ].closed
        is True
    )


def test_reads_strava_activity_titles():

    csv_file = SimpleNamespace(
        name="activities.csv",
        getvalue=lambda: (
            (
                '"Nome da atividade",'
                '"Nome do ficheiro"\n'
                '"T68- 6x20 + Z2 (pt 2)",'
                '"activities\\20284257187.fit.gz"\n'
            ).encode(
                "utf-8"
            )
        ),
    )

    titles = (
        import_panel._read_strava_titles(
            [
                csv_file,
            ]
        )
    )

    assert titles == {
        "20284257187.fit.gz": (
            "T68- 6x20 + Z2 (pt 2)"
        )
    }


def test_repairs_imported_strava_title():

    uploaded_file = SimpleNamespace(
        name="activity.fit",
    )

    title = (
        import_panel._activity_title(
            uploaded_file,
            {
                "activity.fit": (
                    "T75_RecuperaÃ§Ã£o"
                ),
            },
        )
    )

    assert title == (
        "T75_Recuperação"
    )