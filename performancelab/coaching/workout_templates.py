"""
PerformanceLab

Workout Templates

Default reusable workout templates.
"""

from types import MappingProxyType
from typing import Mapping

from .session_purpose import SessionPurpose
from .workout_template import WorkoutTemplate


RECOVERY_TEMPLATE = WorkoutTemplate(
    purpose=SessionPurpose.RECOVERY,
    title="Recovery Session",
    objective="Promote recovery through light movement.",
    intensity="Very easy",
    description=(
        "Keep the effort relaxed and comfortable. "
        "The session should reduce fatigue rather than "
        "create additional training stress."
    ),
    structure=(
        "Easy warm-up",
        "Relaxed continuous movement",
        "Gentle cool-down",
    ),
)


EASY_TEMPLATE = WorkoutTemplate(
    purpose=SessionPurpose.EASY,
    title="Easy Aerobic Session",
    objective="Develop aerobic endurance.",
    intensity="Easy",
    description=(
        "Maintain a controlled conversational effort "
        "throughout the session."
    ),
    structure=(
        "Easy warm-up",
        "Continuous aerobic training",
        "Easy cool-down",
    ),
)


INTENSITY_TEMPLATE = WorkoutTemplate(
    purpose=SessionPurpose.INTENSITY,
    title="Quality Session",
    objective=(
        "Develop aerobic power and sustainable speed."
    ),
    intensity="Hard",
    description=(
        "Complete the work intervals with controlled "
        "intensity. Recover sufficiently between efforts "
        "to preserve execution quality."
    ),
    structure=(
        "Progressive warm-up",
        "Technique drills",
        "Main work intervals",
        "Recovery intervals",
        "Easy cool-down",
    ),
)


LONG_TEMPLATE = WorkoutTemplate(
    purpose=SessionPurpose.LONG,
    title="Long Aerobic Session",
    objective=(
        "Develop endurance and resistance to prolonged effort."
    ),
    intensity="Easy to moderate",
    description=(
        "Keep the first part conservative and maintain "
        "a sustainable effort throughout the session."
    ),
    structure=(
        "Easy opening section",
        "Sustained aerobic training",
        "Controlled final section",
        "Easy cool-down",
    ),
)


RACE_TEMPLATE = WorkoutTemplate(
    purpose=SessionPurpose.RACE,
    title="Race",
    objective="Execute the planned competition.",
    intensity="Race effort",
    description=(
        "Follow the event strategy and adjust effort "
        "according to conditions and athlete feedback."
    ),
    structure=(
        "Pre-race preparation",
        "Competition",
        "Post-race cool-down",
    ),
)


REST_TEMPLATE = WorkoutTemplate(
    purpose=SessionPurpose.REST,
    title="Rest Day",
    objective="Support physical and mental recovery.",
    intensity="None",
    description=(
        "No structured training is planned for this day."
    ),
)

CROSS_TRAINING_TEMPLATE = WorkoutTemplate(
    purpose=SessionPurpose.CROSS_TRAINING,
    title="Cross-Training Session",
    objective=(
        "Develop aerobic fitness while reducing "
        "sport-specific mechanical stress."
    ),
    intensity="Easy to moderate",
    description=(
        "Use a complementary activity such as cycling, "
        "swimming, elliptical training, or another "
        "low-impact aerobic modality."
    ),
    structure=(
        "Easy warm-up",
        "Continuous aerobic cross-training",
        "Easy cool-down",
    ),
)

_DEFAULT_TEMPLATES = {
    SessionPurpose.REST: REST_TEMPLATE,
    SessionPurpose.RECOVERY: RECOVERY_TEMPLATE,
    SessionPurpose.EASY: EASY_TEMPLATE,
    SessionPurpose.INTENSITY: INTENSITY_TEMPLATE,
    SessionPurpose.LONG: LONG_TEMPLATE,
    SessionPurpose.RACE: RACE_TEMPLATE,
    SessionPurpose.CROSS_TRAINING: CROSS_TRAINING_TEMPLATE,
}


DEFAULT_WORKOUT_TEMPLATES: Mapping[
    SessionPurpose,
    WorkoutTemplate,
] = MappingProxyType(
    _DEFAULT_TEMPLATES
)


def template_for(
    purpose: SessionPurpose,
) -> WorkoutTemplate:
    """
    Returns the default template for a session purpose.
    """

    if not isinstance(
        purpose,
        SessionPurpose,
    ):

        raise TypeError(
            "purpose must be a SessionPurpose"
        )

    try:

        return DEFAULT_WORKOUT_TEMPLATES[
            purpose
        ]

    except KeyError as error:

        raise ValueError(
            f"No workout template exists for "
            f"{purpose.value!r}"
        ) from error