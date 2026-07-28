"""
PerformanceLab

Import Panel Component.
"""
from gzip import decompress
from io import BytesIO

import streamlit as st

from performancelab.importers import (
    FITImporter,
    GPXImporter,
)

from performancelab.workout import (
    estimate_workout_rpe,
)

# ======================================================

def _estimate_imported_workout_rpe(
    workout,
    athlete,
) -> float | None:
    """
    Applies automatic RPE estimation using the athlete profile.
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
# ======================================================

def _store_imported_workout(
    workout,
    athlete,
) -> bool:
    """
    Stores a new workout or enriches an existing one.

    Returns whether a new workout was added.
    """

    _, added = athlete.history.merge(
        workout
    )

    return added

# ======================================================

def _prepare_uploaded_file(
    uploaded_file,
):
    """
    Prepares an uploaded activity for its importer.

    Strava FIT files may be compressed as .fit.gz.
    """

    file_name = uploaded_file.name.lower()

    if file_name.endswith(".fit.gz"):

        source = BytesIO(
            decompress(
                uploaded_file.getvalue()
            )
        )

        source.name = (
            uploaded_file.name[:-3]
        )

        return source, "fit"

    extension = (
        file_name
        .rsplit(".", 1)[-1]
    )

    return uploaded_file, extension
# ======================================================

def _import_uploaded_file(
    uploaded_file,
    athlete,
) -> bool:
    """
    Imports one uploaded activity.

    Returns whether a new workout was added.
    """

    source, extension = (
        _prepare_uploaded_file(
            uploaded_file
        )
    )

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

        file_name = uploaded_file.name

        if file_name.lower().endswith(
            ".fit.gz"
        ):

            file_name = file_name[:-3]

        workout.info.title = (
            file_name
            .rsplit(".", 1)[0]
        )

        _estimate_imported_workout_rpe(
            workout,
            athlete,
        )

    return _store_imported_workout(
        workout,
        athlete,
    )

# ======================================================

def _import_uploaded_files(
    uploaded_files,
    athlete,
) -> tuple[int, int, int]:
    """
    Imports multiple activities.

    Returns added, updated and failed counts.
    """

    added_count = 0
    updated_count = 0
    failed_count = 0

    for uploaded_file in uploaded_files:

        try:

            added = _import_uploaded_file(
                uploaded_file,
                athlete,
            )

        except Exception:

            failed_count += 1

            continue

        if added:
            added_count += 1

        else:
            updated_count += 1

    return (
        added_count,
        updated_count,
        failed_count,
    )
# ======================================================
# Import panel
# ======================================================

def show_import_panel(
    athlete,
    *,
    key_prefix: str = "activity",
) -> None:
    """
    Displays the activity file import panel.

    Multiple selected files are imported together.
    """

    uploaded_files = st.file_uploader(
        "Choose activity files",
        type=[
            "gpx",
            "fit",
            "gz",
        ],
        accept_multiple_files=True,
        key=f"{key_prefix}_file_uploader",
    )

    if not uploaded_files:

        return

    file_token = tuple(
        sorted(
            (
                uploaded_file.name,
                uploaded_file.size,
            )
            for uploaded_file
            in uploaded_files
        )
    )

    if (
        st.session_state.get(
            f"{key_prefix}_imported_file_token"
        )
        == file_token
    ):

        return

    (
        added_count,
        updated_count,
        failed_count,
    ) = _import_uploaded_files(
        uploaded_files,
        athlete,
    )

    st.session_state[
        f"{key_prefix}_imported_file_token"
    ] = file_token

    st.session_state.notice = (
        f"Import complete: "
        f"{added_count} added, "
        f"{updated_count} updated, "
        f"{failed_count} failed."
    )

    st.rerun()