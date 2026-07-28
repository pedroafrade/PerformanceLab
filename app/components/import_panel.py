"""
PerformanceLab

Import Panel Component.
"""

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
# Import panel
# ======================================================

def show_import_panel(
    athlete,
    *,
    key_prefix: str = "activity",
) -> None:
    """
    Displays the activity file import panel.

    The selected file is imported automatically.
    """

    uploaded_file = st.file_uploader(
        "Choose activity file",
        type=[
            "gpx",
            "fit",
        ],
        key=f"{key_prefix}_file_uploader",
    )

    if uploaded_file is None:

        return

    file_token = (
        uploaded_file.name,
        uploaded_file.size,
    )

    if (
        st.session_state.get(
            f"{key_prefix}_imported_file_token"
        )
        == file_token
    ):

        return

    try:

        extension = (
            uploaded_file.name
            .rsplit(".", 1)[-1]
            .lower()
        )

        if extension == "gpx":

            importer = GPXImporter()

        elif extension == "fit":

            importer = FITImporter()

        else:

            st.error(
                "Unsupported file format."
            )

            return

        workout = importer.read(
            uploaded_file
        )

        if extension == "fit":

            file_title = (
                uploaded_file.name
                .rsplit(".", 1)[0]
            )

            workout.info.title = file_title

            _estimate_imported_workout_rpe(
                workout,
                athlete,
            )

        added = _store_imported_workout(
            workout,
            athlete,
        )

        st.session_state[
            f"{key_prefix}_imported_file_token"
        ] = file_token

        st.session_state.notice = (
            "Workout imported successfully."
            if added
            else "Existing workout updated."
        )

        st.rerun()

    except Exception as error:

        st.error(
            str(error)
        )