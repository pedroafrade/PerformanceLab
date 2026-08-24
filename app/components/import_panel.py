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
) -> tuple[int, int, int]:
    """
    Parse files and send valid workouts to the use case.

    Returns added, updated and failed counts.
    """

    strava_titles = (
        _read_strava_titles(
            uploaded_files
        )
    )

    workouts = []
    failed_count = 0

    for uploaded_file in uploaded_files:

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

            failed_count += 1
            continue

        workouts.append(
            workout
        )

    if not workouts:

        return (
            0,
            0,
            failed_count,
        )

    result = on_import_activities(
        tuple(
            workouts
        )
    )

    return (
        result.added_count,
        result.updated_count,
        failed_count,
    )


def show_import_panel(
    athlete,
    *,
    on_import_activities,
    key_prefix: str = "activity",
) -> None:
    """
    Display the activity file import panel.
    """

    uploader_version_key = (
        f"{key_prefix}_file_uploader_version"
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

        (
            added_count,
            updated_count,
            failed_count,
        ) = _import_uploaded_files(
            uploaded_files,
            athlete,
            on_import_activities,
        )

    except Exception:

        st.error(
            "Import failed before the athlete "
            "could be updated."
        )

        return

    st.session_state.persisted_notice = (
        f"Import complete: "
        f"{added_count} added, "
        f"{updated_count} updated, "
        f"{failed_count} failed."
    )

    st.session_state[
        uploader_version_key
    ] = uploader_version + 1

    st.rerun()