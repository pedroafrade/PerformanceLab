"""
PerformanceLab

Storage Panel Component.
"""

import json

import streamlit as st

from performancelab.storage import (
    athlete_from_dict,
    athlete_to_dict,
)


# ======================================================
# Storage panel
# ======================================================

def show_storage_panel(
    athlete,
):

    """
    Displays athlete import/export controls.

    Returns
    -------
    Athlete
        Current athlete or imported athlete.
    """

    st.header("Athlete")

    uploaded = st.file_uploader(

        "Import athlete",

        type=["json"],

    )

    if uploaded is not None:

        try:

            imported_athlete = athlete_from_dict(

                json.loads(

                    uploaded.read().decode(

                        "utf-8"

                    )

                )

            )

            st.success(

                "Athlete imported."

            )

            return imported_athlete

        except Exception as error:

            st.error(

                str(error)

            )

    st.download_button(

        "Export athlete",

        data=json.dumps(

            athlete_to_dict(

                athlete

            ),

            indent=4,

        ),

        file_name="athlete.json",

        mime="application/json",

        use_container_width=True,

    )

    return athlete