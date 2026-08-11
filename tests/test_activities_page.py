"""
Tests for the Activities page.
"""

from datetime import date, timedelta

from app.components.activities_page import (
    _activity_coach_material,
    _activity_rows,
    _activity_row_label,
    _analysis_available,
    _compact_activity_metrics_html,
    _format_load,
    _outcome_filter_value,
    _outcome_label,
    _period_start_date,
    _total_duration,
    _workout_for_activity,
    show_activities_page,

)
from performancelab.presentation import (
    ActivityListItemData,
    ActivitiesPresenter,
)

from performancelab import (
    Athlete,
    Workout,
)


def create_activity(
    *,
    workout_id: str,
    workout_date: date,
    title: str,
    sport: str,
    distance: float | None,
    duration: timedelta | None,
    elevation_gain: float | None,
    rpe: float | None,
) -> ActivityListItemData:

    return ActivityListItemData(
        workout_id=workout_id,
        workout_date=workout_date,
        title=title,
        sport=sport,
        distance=distance,
        duration=duration,
        elevation_gain=elevation_gain,
        rpe=rpe,
    )


def test_show_activities_page_exists():

    assert callable(
        show_activities_page
    )


def test_builds_activity_table_rows():

    activity = create_activity(
        workout_id="activity-1",
        workout_date=date(
            2026,
            8,
            2,
        ),
        title="Volta da Ericeira",
        sport="Cycling",
        distance=50.3,
        duration=timedelta(
            hours=2,
            minutes=32,
        ),
        elevation_gain=980,
        rpe=7.5,
    )

    rows = _activity_rows(
        (
            activity,
        )
    )

    assert rows == [
        {
            "Date": "2026-08-02",
            "Activity": (
                "Volta da Ericeira"
            ),
            "Sport": "Cycling",
            "Analysis": "—",
            "Distance": "50.30 km",
            "Duration": "2h 32m",
            "Elevation": "980 m",
            "RPE": 7.5,
            "Plan result": "Not assessed",
            "Planned": "—",
        }
    ]


def test_displays_missing_values_as_dash():

    activity = create_activity(
        workout_id="activity-2",
        workout_date=date(
            2026,
            8,
            1,
        ),
        title="Manual activity",
        sport="Other",
        distance=None,
        duration=None,
        elevation_gain=None,
        rpe=None,
    )

    row = _activity_rows(
        (
            activity,
        )
    )[0]

    assert row["Distance"] == "—"
    assert row["Duration"] == "—"
    assert row["Elevation"] == "—"
    assert row["RPE"] == "—"


def test_calculates_total_activity_duration():

    first = create_activity(
        workout_id="activity-1",
        workout_date=date(
            2026,
            8,
            1,
        ),
        title="Run",
        sport="Running",
        distance=10,
        duration=timedelta(
            hours=1,
        ),
        elevation_gain=100,
        rpe=5,
    )

    second = create_activity(
        workout_id="activity-2",
        workout_date=date(
            2026,
            8,
            2,
        ),
        title="Ride",
        sport="Cycling",
        distance=40,
        duration=timedelta(
            hours=2,
            minutes=30,
        ),
        elevation_gain=500,
        rpe=6,
    )

    assert _total_duration(
        (
            first,
            second,
        )
    ) == timedelta(
        hours=3,
        minutes=30,
    )



def test_last_thirty_days_start_date():

    assert _period_start_date(
        "Last 30 days",
        reference_day=date(
            2026,
            8,
            3,
        ),
    ) == date(
        2026,
        7,
        5,
    )


def test_this_year_start_date():

    assert _period_start_date(
        "This year",
        reference_day=date(
            2026,
            8,
            3,
        ),
    ) == date(
        2026,
        1,
        1,
    )


def test_all_time_has_no_start_date():

    assert (
        _period_start_date(
            "All time",
            reference_day=date(
                2026,
                8,
                3,
            ),
        )
        is None
    )



def test_resolves_domain_workout_from_activity():

    from performancelab.history import (
        History,
    )
    from performancelab.workout import (
        Workout,
    )

    workout = Workout()

    activity = create_activity(
        workout_id=workout.workout_id,
        workout_date=date(
            2026,
            8,
            2,
        ),
        title="Selected activity",
        sport="Running",
        distance=10,
        duration=timedelta(
            hours=1,
        ),
        elevation_gain=100,
        rpe=5,
    )

    result = _workout_for_activity(
        History(
            workouts=[
                workout,
            ]
        ),
        activity,
    )

    assert result is workout


def test_returns_none_for_missing_activity():

    from performancelab.history import (
        History,
    )

    activity = create_activity(
        workout_id="missing-workout",
        workout_date=date(
            2026,
            8,
            2,
        ),
        title="Missing activity",
        sport="Running",
        distance=10,
        duration=timedelta(
            hours=1,
        ),
        elevation_gain=100,
        rpe=5,
    )

    result = _workout_for_activity(
        History(),
        activity,
    )

    assert result is None



def test_displays_planned_activity_outcome():

    activity = ActivityListItemData(
        workout_id="activity-3",
        workout_date=date(
            2026,
            8,
            2,
        ),
        title="Volta da Ericeira",
        sport="Cycling",
        distance=50.3,
        duration=timedelta(
            hours=2,
            minutes=32,
        ),
        elevation_gain=980,
        rpe=7.5,
        outcome_status="substitute",
        planned_title="Long Run",
        planned_load=420,
        completed_load=920,
        load_difference=500,
    )

    row = _activity_rows(
        (
            activity,
        )
    )[0]

    assert row["Plan result"] == (
        "Substitute"
    )
    assert row["Planned"] == (
        "Long Run"
    )



def test_formats_activity_load():

    assert _format_load(
        420.4
    ) == "420 AU"


def test_formats_signed_load_difference():

    assert _format_load(
        90,
        signed=True,
    ) == "+90 AU"

    assert _format_load(
        -90,
        signed=True,
    ) == "-90 AU"


def test_formats_missing_activity_load():

    assert _format_load(
        None
    ) == "—"



def test_converts_plan_result_filter():

    assert _outcome_filter_value(
        "Equivalent"
    ) == "equivalent"

    assert _outcome_filter_value(
        "Modified"
    ) == "modified"

    assert _outcome_filter_value(
        "Substitute"
    ) == "substitute"

    assert _outcome_filter_value(
        "Unplanned"
    ) == "unplanned"


def test_all_plan_results_has_no_filter():

    assert (
        _outcome_filter_value(
            "All results"
        )
        is None
    )



def test_formats_activity_outcome_labels():

    assert _outcome_label(
        "outside_plan"
    ) == "Outside Plan"

    assert _outcome_label(
        "unplanned"
    ) == "Unplanned"

    assert _outcome_label(
        "substitute"
    ) == "Substitute"

    assert _outcome_label(
        None
    ) == "Not assessed"


def test_converts_outside_plan_filter():

    assert _outcome_filter_value(
        "Outside plan"
    ) == "outside_plan"

def test_marks_activity_with_route_and_sensors():

    from performancelab.history import (
        History,
    )
    from performancelab.workout import (
        Workout,
    )

    workout = Workout()

    workout.sensors.add(
        "gps",
        [
            {
                "latitude": 38.7,
                "longitude": -9.4,
            },
            {
                "latitude": 38.71,
                "longitude": -9.39,
            },
        ],
    )

    workout.sensors.add(
        "heart_rate",
        [
            {
                "value": 150,
            },
        ],
    )

    activity = create_activity(
        workout_id=workout.workout_id,
        workout_date=date(
            2026,
            8,
            2,
        ),
        title="Trail Run",
        sport="Trail Running",
        distance=10,
        duration=timedelta(
            hours=1,
        ),
        elevation_gain=500,
        rpe=6,
    )

    result = (
        _analysis_available(
            History(
                workouts=[
                    workout
                ]
            ),
            activity,
        )
    )

    assert result == (
        "Route + sensors"
    )


def test_marks_basic_activity_without_sensor_data():

    from performancelab.history import (
        History,
    )
    from performancelab.workout import (
        Workout,
    )

    workout = Workout()

    activity = create_activity(
        workout_id=workout.workout_id,
        workout_date=date(
            2026,
            8,
            2,
        ),
        title="Manual Run",
        sport="Running",
        distance=5,
        duration=timedelta(
            minutes=30,
        ),
        elevation_gain=None,
        rpe=5,
    )

    result = (
        _analysis_available(
            History(
                workouts=[
                    workout
                ]
            ),
            activity,
        )
    )

    assert result == "Basic"


def test_builds_compact_activity_row_label():

    activity = create_activity(
        workout_id="activity-1",
        workout_date=date(
            2026,
            8,
            9,
        ),
        title="Hill Run",
        sport="Running",
        distance=11.58,
        duration=timedelta(
            hours=1,
            minutes=42,
        ),
        elevation_gain=630,
        rpe=7.7,
    )

    label = (
        _activity_row_label(
            activity
        )
    )

    assert "·" not in label
    assert len(
        label
    ) == 113

    assert label.index(
        "2026-08-09"
    ) == 0

    assert label.index(
        "Running"
    ) == 12

    assert label.index(
        "Hill Run"
    ) == 27

    assert label.index(
        "11.58 km"
    ) == 60

    assert label.index(
        "1h 42m"
    ) == 72

    assert label.index(
        "630 m"
    ) == 83

    assert label.index(
        "RPE 7.7"
    ) == 90

    assert label.index(
        "Not assessed"
    ) == 99

def test_truncates_long_activity_row_title():

    activity = create_activity(
        workout_id="activity-long-title",
        workout_date=date(
            2026,
            8,
            9,
        ),
        title=(
            "A very long activity title that "
            "must not displace later fields"
        ),
        sport="Running",
        distance=10,
        duration=timedelta(
            hours=1
        ),
        elevation_gain=200,
        rpe=6,
    )

    label = (
        _activity_row_label(
            activity
        )
    )

    assert "…" in label
    assert len(
        label
    ) == 113

    assert label.index(
        "10.00 km"
    ) == 60

    assert label.index(
        "1h 00m"
    ) == 72

def test_builds_unified_activity_metrics():

    from performancelab.workout import (
        Workout,
    )

    activity = ActivityListItemData(
        workout_id="activity-metrics",
        workout_date=date(
            2026,
            8,
            7,
        ),
        sport="Cycling",
        title="Cycling activity",
        distance=50.3,
        duration=timedelta(
            hours=2,
            minutes=32,
        ),
        elevation_gain=980,
        rpe=7.5,
        outcome_status=(
            "outside_plan"
        ),
        planned_load=None,
        completed_load=1140,
        load_difference=None,
    )

    workout = Workout()
    workout.info.sport = "Cycling"
    workout.info.distance = 50.3
    workout.info.duration = timedelta(
        hours=2,
        minutes=32,
    )
    workout.info.elevation_gain = 980
    workout.feedback.rpe = 7.5

    html = (
        _compact_activity_metrics_html(
            activity=activity,
            workout=workout,
        )
    )

    assert "Distance" in html
    assert "Duration" in html
    assert "Elevation" in html
    assert "RPE" in html
    assert "HR avg / max" in html
    assert "Power avg / max" in html
    assert "Cadence avg / max" in html
    assert "Planned load" in html
    assert "Completed load" in html
    assert "1140 AU" in html
    assert "Air temperature" in html
    assert "Humidity" in html
    assert "Terrain" in html
    assert "Plan result" in html
    assert "Outside Plan" in html



def test_builds_coach_payload_without_generation():

    athlete = Athlete(
        name="Pedro",
        threshold_hr=177,
    )

    workout = Workout()
    workout.info.date = date(
        2026,
        8,
        9,
    )
    workout.info.sport = "Running"
    workout.info.title = "Hill Run"
    workout.info.distance = 11.0
    workout.info.duration = timedelta(
        minutes=90
    )
    workout.info.elevation_gain = 600.0
    workout.feedback.rpe = 7.0
    workout.feedback.notes = (
        "Mild stiffness at the start, then no pain."
    )
    athlete.history.add(
        workout
    )

    activity = ActivitiesPresenter(
        athlete.history,
        training_plan=(
            athlete.training_plan
        ),
        reference_day=date(
            2026,
            8,
            9,
        ),
    ).build()[0]

    (
        payload,
        stored,
    ) = _activity_coach_material(
        activity=activity,
        workout=workout,
        athlete=athlete,
    )

    assert payload[
        "contract_version"
    ] == "activity-coach-v4"

    assert payload[
        "assessment"
    ][
        "context"
    ][
        "activity"
    ][
        "title"
    ] == "Hill Run"
    
    assert payload[
        "assessment"
    ][
        "context"
    ][
        "feedback"
    ][
        "notes"
    ] == (
        "Mild stiffness at the start, then no pain."
    )
    
    assert stored is None
    assert len(
        athlete.activity_coach_interpretations
    ) == 0