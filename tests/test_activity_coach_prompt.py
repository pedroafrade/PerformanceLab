import json

from performancelab import (
    Workout,
)
from performancelab.presentation import (
    ACTIVITY_COACH_PROMPT_VERSION,
    ActivityCoachPresenter,
    ActivityListItemData,
    build_activity_coach_prompt_payload,
)

from datetime import (
    date,
    timedelta,
)


def create_assessment():
    workout = Workout()

    workout.feedback.rpe = 7.0
    workout.feedback.notes = (
        "Felt tired on the final climb."
    )

    workout.sensors.add(
        "heart_rate",
        [
            {
                "value": 160,
            },
            {
                "value": 170,
            },
        ],
    )

    activity = ActivityListItemData(
        workout_id=str(
            workout.workout_id
        ),
        workout_date=date(
            2026,
            8,
            9,
        ),
        sport="Running",
        title="Hill Run",
        distance=11.0,
        duration=timedelta(
            minutes=90
        ),
        elevation_gain=600.0,
        rpe=7.0,
        planned_load=400.0,
        completed_load=630.0,
        load_difference=230.0,
    )

    return ActivityCoachPresenter(
        activity=activity,
        workout=workout,
    ).build()


def test_builds_json_serializable_prompt_payload():

    payload = (
        build_activity_coach_prompt_payload(
            create_assessment()
        )
    )

    serialized = json.dumps(
        payload
    )

    assert serialized
    assert payload[
        "contract_version"
    ] == ACTIVITY_COACH_PROMPT_VERSION

    assert payload[
        "assessment"
    ][
        "context"
    ][
        "feedback"
    ][
        "notes"
    ] == "Felt tired on the final climb."


def test_declares_available_and_missing_data():

    payload = (
        build_activity_coach_prompt_payload(
            create_assessment()
        )
    )

    assert (
        "assessment.context.feedback.notes"
        in payload["available_data"]
    )

    assert (
        "assessment.context.feedback.sleep_quality"
        in payload["missing_data"]
    )

    assert (
        "assessment.context.event.distance"
        in payload["missing_data"]
    )


def test_contract_contains_safety_rules():

    payload = (
        build_activity_coach_prompt_payload(
            create_assessment()
        )
    )

    combined_rules = " ".join(
        payload["rules"]
    ).lower()

    assert "never invent symptoms" in (
        combined_rules
    )
    assert "missing data" in combined_rules
    assert "state_is_current" in (
        combined_rules
    )

    assert payload[
        "required_sections"
    ] == [
        "measured_facts",
        "deterministic_signals",
        "prudent_interpretation",
        "recommendations",
        "data_limitations",
    ]