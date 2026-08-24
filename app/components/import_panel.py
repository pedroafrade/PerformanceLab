"""
PerformanceLab

Import Panel Component.
"""

from csv import (
    DictReader,
)

from io import (
    StringIO,
)

import streamlit as st

from performancelab.importers import (
    FITImporter,
    GPXImporter,
)
from performancelab.upload_processing import (
    open_activity_upload,
)
from performancelab.upload_results import (
    ActivityFileImportResult,
    ActivityUploadBatchResult,
)
from performancelab.upload_validation import (
    validate_activity_upload_content,
)
from performancelab.text import (
    repair_mojibake,
)
from performancelab.workout import (
    estimate_workout_rpe,
)


def _estimate_imported_workout_rpe(
    workout,
    athlete,
) -> float | None:
    """
    Apply automatic RPE estimation using the athlete profile.
    """

    return estimate_workout_rpe(
        workout,
        max_hr=getattr(
            athlete,
            "max_hr",
            None,
        ),
        resting_hr=getattr(
            athlete,
            "resting_hr",
            None,
        ),
    )

def _normalized_file_name(
    value,
) -> str:
    """
    Return only the normalized file name.
    """

    return (
        str(
            value
            or ""
        )
        .replace(
            "\\",
            "/",
        )
        .rsplit(
            "/",
            1,
        )[-1]
        .strip()
        .lower()
    )


def _read_strava_titles(
    uploaded_files,
) -> dict[str, str]:
    """
    Read activity titles from Strava's activities.csv.
    """

    titles = {}

    for uploaded_file in uploaded_files:

        if (
            uploaded_file.name.lower()
            != "activities.csv"
        ):
            continue

        validated_upload = (
            validate_activity_upload_content(
                uploaded_file.name,
                uploaded_file.getvalue(),
            )
        )

        content = (
            validated_upload
            .content
            .decode(
                "utf-8-sig"
            )
        )

        rows = DictReader(
            StringIO(
                content
            )
        )

        for row in rows:

            file_name = next(
                (
                    candidate
                    for candidate in (
                        _normalized_file_name(
                            value
                        )
                        for value
                        in row.values()
                    )
                    if candidate.endswith(
                        (
                            ".fit",
                            ".fit.gz",
                            ".gpx",
                            ".gpx.gz",
                        )
                    )
                ),
                "",
            )

            title = str(
                row.get(
                    "Activity Name"
                )
                or row.get(
                    "Nome da atividade"
                )
                or ""
            ).strip()

            if file_name and title:

                titles[
                    file_name
                ] = title

    return titles


def _activity_title(
    uploaded_file,
    strava_titles,
) -> str:
    """
    Return the Strava title or a file-name fallback.
    """

    normalized_name = (
        _normalized_file_name(
            uploaded_file.name
        )
    )

    strava_title = (
        strava_titles.get(
            normalized_name
        )
    )

    if strava_title:

        return repair_mojibake(
            strava_title
        )

    file_name = (
        uploaded_file.name
    )

    if file_name.lower().endswith(
        ".fit.gz"
    ):

        file_name = (
            file_name[:-3]
        )

    return repair_mojibake(
        file_name.rsplit(
            ".",
            1,
        )[0]
    )


def _import_uploaded_file(
    uploaded_file,
    athlete,
    strava_titles=None,
):
    """
    Parse one validated in-memory file into a Workout.

    The temporary in-memory stream is closed immediately after
    the importer finishes, including when parsing fails.
    """

    with open_activity_upload(
        uploaded_file.name,
        uploaded_file.getvalue(),
    ) as (
        source,
        extension,
    ):

        if extension == "gpx":

            importer = GPXImporter()

        elif extension == "fit":

            importer = FITImporter()

        else:

            raise ValueError(
                "Unsupported file format."
            )

        workout = importer.read(
            source
        )

    if extension == "fit":

        workout.info.title = (
            _activity_title(
                uploaded_file,
                strava_titles or {},
            )
        )

        _estimate_imported_workout_rpe(
            workout,
            athlete,
        )

    return workout


def _import_uploaded_files(
    uploaded_files,
    athlete,
    on_import_activities,
) -> ActivityUploadBatchResult:
    """
    Parse files and return one factual result per file.

    Technical parser messages are deliberately excluded from
    the result presented to the athlete.
    """

    selected_files = tuple(
        uploaded_files
    )

    file_results = [
        None
        for _ in selected_files
    ]

    strava_titles = {}

    for index, uploaded_file in enumerate(
        selected_files
    ):

        if (
            uploaded_file.name.lower()
            != "activities.csv"
        ):

            continue

        try:

            strava_titles.update(
                _read_strava_titles(
                    (
                        uploaded_file,
                    )
                )
            )

        except Exception:

            file_results[
                index
            ] = ActivityFileImportResult(
                file_name=(
                    uploaded_file.name
                ),
                status="invalid",
                reason=(
                    "The Strava activity index "
                    "could not be read."
                ),
            )

        else:

            file_results[
                index
            ] = ActivityFileImportResult(
                file_name=(
                    uploaded_file.name
                ),
                status="ignored",
                reason=(
                    "Strava activity titles "
                    "were used as metadata."
                ),
            )

    valid_workouts = []
    valid_file_indexes = []

    for index, uploaded_file in enumerate(
        selected_files
    ):

        if (
            uploaded_file.name.lower()
            == "activities.csv"
        ):

            continue

        try:

            workout = (
                _import_uploaded_file(
                    uploaded_file,
                    athlete,
                    strava_titles,
                )
            )

        except Exception:

            file_results[
                index
            ] = ActivityFileImportResult(
                file_name=(
                    uploaded_file.name
                ),
                status="invalid",
                reason=(
                    "The activity file could "
                    "not be imported."
                ),
            )

            continue

        valid_workouts.append(
            workout
        )

        valid_file_indexes.append(
            index
        )

    if valid_workouts:

        import_result = (
            on_import_activities(
                tuple(
                    valid_workouts
                )
            )
        )

        if (
            len(
                import_result.outcomes
            )
            != len(
                valid_workouts
            )
        ):

            raise RuntimeError(
                "Activity import result does not match "
                "the submitted workouts."
            )

        for (
            file_index,
            outcome,
        ) in zip(
            valid_file_indexes,
            import_result.outcomes,
        ):

            file_results[
                file_index
            ] = ActivityFileImportResult(
                file_name=(
                    selected_files[
                        file_index
                    ].name
                ),
                status=outcome.status,
                workout_id=(
                    outcome.workout_id
                ),
            )

    if any(
        result is None
        for result in file_results
    ):

        raise RuntimeError(
            "An activity upload result is missing."
        )

    return ActivityUploadBatchResult(
        files=tuple(
            file_results
        )
    )


def show_import_panel(
    athlete,
    *,
    on_import_activities,
    key_prefix: str = "activity",
) -> None:
    """
    Display the activity file import panel.

    Every completed or failed attempt advances the uploader key,
    allowing Streamlit to release the previous upload objects.
    """

    uploader_version_key = (
        f"{key_prefix}_file_uploader_version"
    )

    upload_error_key = (
        f"{key_prefix}_file_uploader_error"
    )

    pending_error = (
        st.session_state.pop(
            upload_error_key,
            None,
        )
    )

    if pending_error:

        st.error(
            pending_error
        )

    uploader_version = (
        st.session_state.get(
            uploader_version_key,
            0,
        )
    )

    uploaded_files = st.file_uploader(
        "Choose files",
        type=[
            "gpx",
            "fit",
            "gz",
            "csv",
        ],
        accept_multiple_files=True,
        key=(
            f"{key_prefix}_file_uploader_"
            f"{uploader_version}"
        ),
    )

    if not uploaded_files:

        return

    try:

        batch_result = (
            _import_uploaded_files(
                uploaded_files,
                athlete,
                on_import_activities,
            )
        )

    except Exception:

        st.session_state[
            upload_error_key
        ] = (
            "Import failed before the athlete "
            "could be updated."
        )

    else:

        st.session_state[
            "persisted_notice"
        ] = (
            batch_result.notice
        )

    st.session_state[
        uploader_version_key
    ] = uploader_version + 1

    st.rerun()