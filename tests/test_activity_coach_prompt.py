import json

from performancelab import (
    Workout,
)
from performancelab.presentation import (
    ACTIVITY_COACH_PROMPT_VERSION,
    ActivityCoachFeedbackData,
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

    assert ACTIVITY_COACH_PROMPT_VERSION == (
        "activity-coach-v5"
    )

    assert payload[
        "assessment"
    ][
        "context"
    ][
        "feedback"
    ][
        "notes"
    ] == "Felt tired on the final climb."

def test_omits_duplicated_data_inventories():

    payload = (
        build_activity_coach_prompt_payload(
            create_assessment()
        )
    )

    assert (
        "available_data"
        not in payload
    )

    assert (
        "missing_data"
        not in payload
    )

def test_minimizes_personal_activity_context():

    assessment = create_assessment()

    payload = (
        build_activity_coach_prompt_payload(
            assessment
        )
    )

    activity = payload[
        "assessment"
    ][
        "context"
    ][
        "activity"
    ]

    assert (
        "workout_id"
        not in activity
    )

    assert (
        "workout_date"
        not in activity
    )

    assert (
        "title"
        not in activity
    )

    assert (
        "rpe"
        not in activity
    )

    assert (
        "load_difference"
        not in activity
    )

    feedback = payload[
        "assessment"
    ][
        "context"
    ][
        "feedback"
    ]

    assert feedback[
        "rpe"
    ] == 7.0

    assert feedback[
        "notes"
    ] == (
        "Felt tired on the final climb."
    )

    assert (
        "sleep_quality"
        not in feedback
    )

    serialized = json.dumps(
        payload
    )

    assert (
        assessment
        .context
        .activity
        .workout_id
        not in serialized
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
    assert "natural, direct english" in (
        combined_rules
    )
    assert "internal field names" in (
        combined_rules
    )
    assert "raw durations in seconds" in (
        combined_rules
    )
    assert "rigid or alarmist" in (
        combined_rules
    )
    assert "directly relevant" in (
        combined_rules
    )
    assert "narrative_structure" in (
        combined_rules
    )
    assert "reported by the athlete" in (
        combined_rules
    )
    assert "single cause" in (
        combined_rules
    )
    assert "existing plan" in (
        combined_rules
    )
    assert "three to five short paragraphs" in (
        combined_rules
    )
    assert "one to three short paragraphs" in (
        combined_rules
    )
    assert "two newline characters" in (
        combined_rules
    )
    assert "one clear coaching idea" in (
        combined_rules
    )
    assert "do not add markdown headings" in (
        combined_rules
    )
    
    narrative_structure = payload[
        "narrative_structure"
    ]

    assert len(
        narrative_structure
    ) == 7

    combined_structure = " ".join(
        narrative_structure
    ).lower()

    assert "practical conclusion" in (
        combined_structure
    )
    assert "subjective response" in (
        combined_structure
    )
    assert "target event" in (
        combined_structure
    )
    assert "conditional" in (
        combined_structure
    )
    assert "balanced overall assessment" in (
        combined_structure
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

def test_exports_activity_coach_feedback_data():

    feedback = ActivityCoachFeedbackData(
        rpe=7.0,
    )

    assert feedback.rpe == 7.0