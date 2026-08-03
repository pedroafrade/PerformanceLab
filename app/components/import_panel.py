"""
PerformanceLab

Import Panel Component.
"""
from datetime import date, datetime
from gzip import decompress
from io import BytesIO

from csv import DictReader
from io import StringIO

import streamlit as st

from performancelab.importers import (
    FITImporter,
    GPXImporter,
)
from performancelab.text import (
    repair_mojibake,
)
from performancelab.training.planning import (
    TrainingPlanReconciler,
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
def _reconcile_training_plan(
    athlete,
    *,
    through_day: date,
) -> None:
    """
    Reconciles the persistent plan after imported
    activities have updated the athlete's history.
    """

    athlete.training_plan = (
        TrainingPlanReconciler().reconcile(
            plan=athlete.training_plan,
            history=athlete.history,
            training_state=(
                athlete.analytics.training_state
            ),
            through_day=through_day,
        )
    )

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

def _normalized_file_name(
    value,
) -> str:
    """
    Returns only the normalized file name.
    """

    return (
        str(value or "")
        .replace("\\", "/")
        .rsplit("/", 1)[-1]
        .strip()
        .lower()
    )


# ======================================================

def _read_strava_titles(
    uploaded_files,
) -> dict[str, str]:
    """
    Reads activity titles from Strava's activities.csv.
    """

    titles = {}

    for uploaded_file in uploaded_files:

        if (
            uploaded_file.name.lower()
            != "activities.csv"
        ):
            continue

        content = (
            uploaded_file.getvalue()
            .decode("utf-8-sig")
        )

        rows = DictReader(
            StringIO(content)
        )

        for row in rows:

            file_name = next(
                (
                    candidate
                    for candidate in (
                        _normalized_file_name(
                            value
                        )
                        for value in row.values()
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
                row.get("Activity Name")
                or row.get(
                    "Nome da atividade"
                )
                or ""
            ).strip()

            if file_name and title:

                titles[file_name] = title

    return titles


# ======================================================

def _activity_title(
    uploaded_file,
    strava_titles,
) -> str:
    """
    Returns the Strava title or a file-name fallback.
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

    file_name = uploaded_file.name

    if file_name.lower().endswith(
        ".fit.gz"
    ):

        file_name = file_name[:-3]

    return repair_mojibake(
        file_name
        .rsplit(".", 1)[0]
    )
# ======================================================

def _import_uploaded_file(
    uploaded_file,
    athlete,
    strava_titles=None,
) -> tuple[bool, date | None]:
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

    added = _store_imported_workout(
        workout,
        athlete,
    )

    workout_day = workout.date

    if isinstance(
        workout_day,
        datetime,
    ):
        workout_day = (
            workout_day.date()
        )

    if not isinstance(
        workout_day,
        date,
    ):
        workout_day = None

    return (
        added,
        workout_day,
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
    strava_titles = (
        _read_strava_titles(
            uploaded_files
        )
    )
    added_count = 0
    updated_count = 0
    failed_count = 0
    imported_days = []

    for uploaded_file in uploaded_files:

        if (
            uploaded_file.name.lower()
            == "activities.csv"
        ):
            continue

        try:

            (
                added,
                workout_day,
            ) = _import_uploaded_file(
                uploaded_file,
                athlete,
                strava_titles,
            )

        except Exception:

            failed_count += 1

            continue
        if workout_day is not None:
            imported_days.append(
                workout_day
            )
        if added:
            added_count += 1

        else:
            updated_count += 1
    if imported_days:
        _reconcile_training_plan(
            athlete,
            through_day=max(
                imported_days
            ),
        )
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


    (
        added_count,
        updated_count,
        failed_count,
    ) = _import_uploaded_files(
        uploaded_files,
        athlete,
    )

    st.session_state.notice = (
        f"Import complete: "
        f"{added_count} added, "
        f"{updated_count} updated, "
        f"{failed_count} failed."
    )

    st.session_state[
        uploader_version_key
    ] = uploader_version + 1

    st.rerun()