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
from performancelab.application import (
    ImportedActivityOutcome,
)
from performancelab.upload_results import (
    ActivityUploadBatchResult,
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

def test_reports_result_for_every_selected_file(
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

    first_workout = SimpleNamespace(
        workout_id="workout-1"
    )
    second_workout = SimpleNamespace(
        workout_id="workout-2"
    )

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

        calls[
            "workouts"
        ] = workouts

        return SimpleNamespace(
            outcomes=(
                ImportedActivityOutcome(
                    workout_id=(
                        "workout-1"
                    ),
                    status="imported",
                ),
                ImportedActivityOutcome(
                    workout_id=(
                        "workout-2"
                    ),
                    status="updated",
                ),
            )
        )

    result = (
        import_panel._import_uploaded_files(
            (
                first_file,
                second_file,
                failed_file,
            ),
            SimpleNamespace(),
            on_import_activities,
        )
    )

    assert isinstance(
        result,
        ActivityUploadBatchResult,
    )

    assert [
        file_result.file_name
        for file_result in result.files
    ] == [
        "first.fit",
        "second.fit",
        "failed.fit",
    ]

    assert [
        file_result.status
        for file_result in result.files
    ] == [
        "imported",
        "updated",
        "invalid",
    ]

    assert calls[
        "workouts"
    ] == (
        first_workout,
        second_workout,
    )


def test_invalid_file_does_not_call_use_case(
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

        calls[
            "count"
        ] += 1

    result = (
        import_panel._import_uploaded_files(
            (
                failed_file,
            ),
            SimpleNamespace(),
            on_import_activities,
        )
    )

    assert (
        result.invalid_count
        == 1
    )

    assert (
        result.files[0].status
        == "invalid"
    )

    assert calls[
        "count"
    ] == 0


def test_reports_strava_csv_as_ignored_metadata():

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

        calls[
            "count"
        ] += 1

    result = (
        import_panel._import_uploaded_files(
            (
                csv_file,
            ),
            SimpleNamespace(),
            on_import_activities,
        )
    )

    assert (
        result.ignored_count
        == 1
    )

    assert (
        result.files[0].status
        == "ignored"
    )

    assert calls[
        "count"
    ] == 0


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

def test_successful_import_resets_uploader(
    monkeypatch,
):

    uploaded_file = SimpleNamespace(
        name="activity.fit"
    )

    state = {}

    calls = {
        "rerun": 0,
    }

    fake_streamlit = SimpleNamespace(
        session_state=state,
        caption=lambda message: None,
        file_uploader=(
            lambda *args, **kwargs: [
                uploaded_file,
            ]
        ),
        error=lambda message: None,
        rerun=lambda: calls.__setitem__(
            "rerun",
            calls[
                "rerun"
            ]
            + 1,
        ),
    )

    monkeypatch.setattr(
        import_panel,
        "st",
        fake_streamlit,
    )

    monkeypatch.setattr(
        import_panel,
        "_import_uploaded_files",
        lambda *args, **kwargs: (
            ActivityUploadBatchResult(
                files=(
                    import_panel
                    .ActivityFileImportResult(
                        file_name="activity.fit",
                        status="imported",
                        workout_id="workout-1",
                    ),
                )
            )
        ),
    )

    import_panel.show_import_panel(
        SimpleNamespace(
            athlete_id="athlete-success"
        ),
        on_import_activities=(
            lambda workouts: None
        ),
        key_prefix="test",
    )

    assert (
        state[
            "test_file_uploader_version"
        ]
        == 1
    )

    assert (
        state[
            "persisted_notice"
        ]
        == (
            "Import complete: "
            "1 imported, "
            "0 updated, "
            "0 duplicate, "
            "0 ignored, "
            "0 invalid."
        )
    )

    assert calls[
        "rerun"
    ] == 1


def test_failed_import_resets_uploader(
    monkeypatch,
):

    uploaded_file = SimpleNamespace(
        name="invalid.fit"
    )

    state = {}

    calls = {
        "rerun": 0,
    }

    fake_streamlit = SimpleNamespace(
        session_state=state,
        caption=lambda message: None,
        file_uploader=(
            lambda *args, **kwargs: [
                uploaded_file,
            ]
        ),
        error=lambda message: None,
        rerun=lambda: calls.__setitem__(
            "rerun",
            calls[
                "rerun"
            ]
            + 1,
        ),
    )

    monkeypatch.setattr(
        import_panel,
        "st",
        fake_streamlit,
    )

    def fail_import(
        *args,
        **kwargs,
    ):

        raise ValueError(
            "Invalid upload batch"
        )

    monkeypatch.setattr(
        import_panel,
        "_import_uploaded_files",
        fail_import,
    )

    import_panel.show_import_panel(
        SimpleNamespace(
            athlete_id="athlete-failure"
        ),
        on_import_activities=(
            lambda workouts: None
        ),
        key_prefix="test",
    )

    assert (
        state[
            "test_file_uploader_version"
        ]
        == 1
    )

    assert (
        state[
            "test_file_uploader_error"
        ]
        == (
            "Import failed before the athlete "
            "could be updated."
        )
    )

    assert (
        "persisted_notice"
        not in state
    )

    assert calls[
        "rerun"
    ] == 1


def test_pending_import_error_is_shown_once(
    monkeypatch,
):

    state = {
        "test_file_uploader_version": 1,
        "test_file_uploader_error": (
            "Import failed before the athlete "
            "could be updated."
        ),
    }

    shown_errors = []

    fake_streamlit = SimpleNamespace(
        session_state=state,
        caption=lambda message: None,
        file_uploader=(
            lambda *args, **kwargs: None
        ),
        error=shown_errors.append,
        rerun=lambda: None,
    )

    monkeypatch.setattr(
        import_panel,
        "st",
        fake_streamlit,
    )

    import_panel.show_import_panel(
        SimpleNamespace(),
        on_import_activities=(
            lambda workouts: None
        ),
        key_prefix="test",
    )

    assert shown_errors == [
        (
            "Import failed before the athlete "
            "could be updated."
        ),
    ]

    assert (
        "test_file_uploader_error"
        not in state
    )

    assert (
        state[
            "test_file_uploader_version"
        ]
        == 1
    )



def test_discloses_activity_file_retention_policy(
    monkeypatch,
):

    shown_captions = []

    fake_streamlit = SimpleNamespace(
        session_state={},
        caption=shown_captions.append,
        file_uploader=(
            lambda *args, **kwargs: None
        ),
        error=lambda message: None,
        rerun=lambda: None,
    )

    monkeypatch.setattr(
        import_panel,
        "st",
        fake_streamlit,
    )

    import_panel.show_import_panel(
        SimpleNamespace(),
        on_import_activities=(
            lambda workouts: None
        ),
        key_prefix="disclosure",
    )

    assert shown_captions == [
        (
            "FIT, FIT.GZ, GPX or Strava "
            "activities.csv · up to 20 files, "
            "20 MB each. Files are processed "
            "in memory and the originals are "
            "not retained."
        ),
    ]