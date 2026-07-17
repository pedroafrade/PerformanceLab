"""
PerformanceLab

Import Panel Component.
"""

import streamlit as st

from performancelab.importers import (
    FITImporter,
    GPXImporter,
)


# ======================================================
# Import panel
# ======================================================

def show_import_panel(
    athlete,
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
        key="activity_file_uploader",
    )

    if uploaded_file is None:

        return

    file_token = (
        uploaded_file.name,
        uploaded_file.size,
    )

    if (
        st.session_state.get(
            "imported_activity_file_token"
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

        athlete.history.add(
            workout
        )

        st.session_state[
            "imported_activity_file_token"
        ] = file_token

        st.session_state.notice = (
            "Workout imported successfully."
        )

        st.rerun()

    except Exception as error:

        st.error(
            str(error)
        )