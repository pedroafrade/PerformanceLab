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
    "activity-coach-v2"
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


def _data_paths(
    value,
    *,
    prefix: str,
    missing: bool,
) -> tuple[str, ...]:
    """
    Lists available or missing leaf fields deterministically.
    """

    paths: list[str] = []

    if isinstance(
        value,
        dict,
    ):
        for key, item in value.items():
            child_prefix = (
                f"{prefix}.{key}"
                if prefix
                else str(key)
            )

            paths.extend(
                _data_paths(
                    item,
                    prefix=child_prefix,
                    missing=missing,
                )
            )

        return tuple(
            paths
        )

    if isinstance(
        value,
        list,
    ):
        for index, item in enumerate(
            value
        ):
            paths.extend(
                _data_paths(
                    item,
                    prefix=(
                        f"{prefix}[{index}]"
                    ),
                    missing=missing,
                )
            )

        return tuple(
            paths
        )

    if (
        value is None
    ) is missing:
        paths.append(
            prefix
        )

    return tuple(
        paths
    )


def build_activity_coach_prompt_payload(
    assessment: ActivityCoachAssessmentData,
) -> dict[str, object]:
    """
    Builds the versioned, JSON-serializable model payload.

    This function defines the contract only. It does not call
    a language model or generate coaching text.
    """

    assessment_data = _serializable_value(
        assessment
    )

    return {
        "contract_version": (
            ACTIVITY_COACH_PROMPT_VERSION
        ),
        "rules": list(
            ACTIVITY_COACH_PROMPT_RULES
        ),
        "required_sections": list(
            ACTIVITY_COACH_OUTPUT_SECTIONS
        ),
        "assessment": assessment_data,
        "available_data": list(
            _data_paths(
                assessment_data,
                prefix="assessment",
                missing=False,
            )
        ),
        "missing_data": list(
            _data_paths(
                assessment_data,
                prefix="assessment",
                missing=True,
            )
        ),
    }