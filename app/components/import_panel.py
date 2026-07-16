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

def show_import_panel(athlete):

    """
    Displays the activity import panel.
    """

    st.divider()

    st.header("Import activity")

    uploaded_file = st.file_uploader(

        "Choose activity file",

        type=[

            "gpx",

            "fit",

        ],

    )

    if st.button(

        "Import",

        use_container_width=True,

    ):

        if uploaded_file is None:

            st.warning(

                "Please choose a GPX or FIT file."

            )

            return

        try:

            filename = (

                uploaded_file.name.lower()

            )

            if filename.endswith(".gpx"):

                importer = GPXImporter()

            elif filename.endswith(".fit"):

                importer = FITImporter()

            else:

                raise ValueError(

                    "Unsupported file format."

                )

            workout = importer.read(

                uploaded_file

            )

            athlete.history.add(

                workout

            )

            st.success(

                "Workout imported successfully."

            )

            st.rerun()

        except Exception as error:

            st.error(

                str(error)

            )