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
    """

    uploaded_file = st.file_uploader(
        "Choose activity file",
        type=[
            "gpx",
            "fit",
        ],
        key="activity_file_uploader",
    )

    if not st.button(
        "Import",
        use_container_width=True,
        key="import_activity_button",
    ):

        return

    if uploaded_file is None:

        st.warning(
            "Please choose a GPX or FIT file."
        )

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

        st.session_state.notice = (
            "Workout imported successfully."
        )

        st.rerun()

    except Exception as error:

        st.error(
            str(error)
        )