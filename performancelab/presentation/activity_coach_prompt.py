"""
PerformanceLab

Deterministic Training Coach prompt contract.
"""

from dataclasses import (
    fields,
    is_dataclass,
)
from datetime import (
    date,
    datetime,
    timedelta,
)
from enum import Enum

from .activity_coach_models import (
    ActivityCoachAssessmentData,
)


ACTIVITY_COACH_PROMPT_VERSION = (
    "activity-coach-v5"
)

ACTIVITY_COACH_NARRATIVE_STRUCTURE = (
    (
        "Open with the most important practical "
        "conclusion about the session."
    ),
    (
        "Prioritize the athlete's explicitly recorded "
        "subjective response when it materially changes "
        "the interpretation."
    ),
    (
        "Interpret cardiovascular and mechanical demand "
        "in the context of session type, terrain, elevation, "
        "environment, and recoveries when those data exist."
    ),
    (
        "Explain how the session relates to recent training, "
        "the current plan phase, and the target event."
    ),
    (
        "State what should be monitored next only when the "
        "available evidence supports a useful observation."
    ),
    (
        "Make the next-training recommendation conditional "
        "on the athlete's response and consistent with the "
        "existing plan."
    ),
    (
        "Finish with a brief, balanced overall assessment "
        "of progress and relevant caution."
    ),
)

ACTIVITY_COACH_PROMPT_RULES = (
    (
        "Use only information explicitly present "
        "in the payload."
    ),
    (
        "Separate measured facts, deterministic "
        "signals, prudent interpretation, "
        "recommendations, and data limitations."
    ),
    (
        "Write in natural, direct English addressed "
        "to the athlete, with the calm and supportive "
        "tone of an experienced endurance coach."
    ),
    (
        "Lead with the practical meaning of the "
        "session. Do not turn the interpretation into "
        "an exhaustive technical report."
    ),
    (
        "Follow narrative_structure as a natural flow "
        "across prudent_interpretation and recommendations. "
        "Do not print the structure instructions or use "
        "their wording as literal section headings."
    ),
    (
        "Format prudent_interpretation as three to five "
        "short paragraphs separated by a blank line. Each "
        "paragraph should contain one to three sentences "
        "and develop one clear coaching idea."
    ),
    (
        "Use the first interpretation paragraph for the "
        "main practical conclusion and the most important "
        "supporting evidence."
    ),
    (
        "Use separate interpretation paragraphs for the "
        "athlete-reported response, session demand, recent "
        "training context, or event relevance only when "
        "the corresponding data are available."
    ),
    (
        "Format recommendations as one to three short "
        "paragraphs separated by a blank line. Keep each "
        "conditional decision together with the evidence "
        "or athlete response that should trigger it."
    ),
    (
        "Do not produce one continuous block of text. "
        "Use two newline characters between paragraphs."
    ),
    (
        "Do not add Markdown headings inside "
        "prudent_interpretation or recommendations because "
        "the user interface already labels the sections."
    ),
    (
        "Omit any narrative topic that lacks supporting "
        "data instead of filling it with generic advice."
    ),
    (
        "Present subjective notes as information reported "
        "by the athlete. Do not convert an athlete report "
        "into a diagnosis or independently verified fact."
    ),
    (
        "When heart rate, power, pace, terrain, elevation, "
        "or environment interact, explain the context and "
        "uncertainty instead of attributing a single cause."
    ),
    (
        "Relate the session to the target event only when "
        "event data are available and the comparison is "
        "meaningful."
    ),
    (
        "Recommendations must respect the existing plan. "
        "Do not invent a replacement schedule when the "
        "payload does not contain enough future-plan data."
    ),
    (
        "Mention only measurements that materially "
        "support the interpretation and round numbers "
        "to athlete-friendly precision."
    ),
    (
        "Express durations naturally in minutes or "
        "hours. Never present raw durations in seconds "
        "when a readable unit can be used."
    ),
    (
        "Never expose internal field names, enum "
        "values, signal codes, or implementation "
        "terminology to the athlete."
    ),
    (
        "Translate deterministic signals into plain "
        "language without weakening or extending "
        "their factual meaning."
    ),
    (
        "Avoid rigid or alarmist instructions. Prefer "
        "proportionate language such as consider, "
        "prioritize, monitor, or reassess when the "
        "evidence does not justify certainty."
    ),
    (
        "Do not add generic recovery, hydration, "
        "nutrition, injury, or medical advice unless "
        "it is directly relevant to evidence present "
        "in the payload."
    ),
    (
        "Never invent symptoms, pain, injuries, "
        "sleep quality, muscle condition, athlete "
        "feelings, or any unrecorded observation."
    ),
    (
        "Do not infer an exact heart-rate zone or "
        "a specific physiological cause from heart "
        "rate alone."
    ),
    (
        "Treat missing data as unavailable, not as "
        "evidence that the value was normal."
    ),
    (
        "Use current readiness, recovery, and load "
        "state only when state_is_current is true."
    ),
    (
        "Keep recommendations prudent and limited "
        "to the evidence in the payload."
    ),
)


ACTIVITY_COACH_OUTPUT_SECTIONS = (
    "measured_facts",
    "deterministic_signals",
    "prudent_interpretation",
    "recommendations",
    "data_limitations",
)


def _serializable_value(
    value,
):
    """
    Converts assessment values into JSON-compatible data.
    """

    if value is None:
        return None

    if isinstance(
        value,
        Enum,
    ):
        return value.value

    if isinstance(
        value,
        datetime,
    ):
        return value.isoformat()

    if isinstance(
        value,
        date,
    ):
        return value.isoformat()

    if isinstance(
        value,
        timedelta,
    ):
        return value.total_seconds()

    if is_dataclass(
        value
    ):
        return {
            field.name: _serializable_value(
                getattr(
                    value,
                    field.name,
                )
            )
            for field in fields(
                value
            )
        }

    if isinstance(
        value,
        dict,
    ):
        return {
            str(key): _serializable_value(
                item
            )
            for key, item in value.items()
        }

    if isinstance(
        value,
        (
            tuple,
            list,
        ),
    ):
        return [
            _serializable_value(
                item
            )
            for item in value
        ]

    return value


def _without_missing_values(
    value,
):
    """
    Remove unavailable values and empty structures.
    """

    if isinstance(
        value,
        dict,
    ):

        cleaned = {}

        for key, item in value.items():

            cleaned_item = (
                _without_missing_values(
                    item
                )
            )

            if cleaned_item is not None:

                cleaned[
                    key
                ] = cleaned_item

        return (
            cleaned
            if cleaned
            else None
        )

    if isinstance(
        value,
        list,
    ):

        cleaned = [
            cleaned_item
            for item in value
            if (
                cleaned_item
                := _without_missing_values(
                    item
                )
            )
            is not None
        ]

        return (
            cleaned
            if cleaned
            else None
        )

    return value


def _minimized_assessment_data(
    assessment_data,
) -> dict[str, object]:
    """
    Remove identifiers, free labels and duplicated values.
    """

    context = assessment_data.get(
        "context",
        {},
    )

    activity = context.get(
        "activity",
        {},
    )

    for field_name in (
        "workout_id",
        "workout_date",
        "title",
        "rpe",
        "load_difference",
    ):

        activity.pop(
            field_name,
            None,
        )

    recent_training = context.get(
        "recent_training",
        {},
    )

    recent_training.pop(
        "previous_title",
        None,
    )

    event = context.get(
        "event",
        {},
    )

    event.pop(
        "name",
        None,
    )

    minimized = (
        _without_missing_values(
            assessment_data
        )
    )

    if not isinstance(
        minimized,
        dict,
    ):

        raise ValueError(
            "Activity Coach assessment cannot be empty."
        )

    return minimized


def build_activity_coach_prompt_payload(
    assessment: ActivityCoachAssessmentData,
) -> dict[str, object]:
    """
    Builds the versioned, JSON-serializable model payload.

    This function defines the contract only. It does not call
    a language model or generate coaching text.
    """

    assessment_data = (
        _minimized_assessment_data(
            _serializable_value(
                assessment
            )
        )
    )

    return {
        "contract_version": (
            ACTIVITY_COACH_PROMPT_VERSION
        ),
        "rules": list(
            ACTIVITY_COACH_PROMPT_RULES
        ),
        "narrative_structure": list(
            ACTIVITY_COACH_NARRATIVE_STRUCTURE
        ),
        "required_sections": list(
            ACTIVITY_COACH_OUTPUT_SECTIONS
        ),
        "assessment": assessment_data,
    }