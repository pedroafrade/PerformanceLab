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

THRESHOLD_TEMPLATE = WorkoutTemplate(
    purpose=SessionPurpose.INTENSITY,
    title="Threshold Session",
    objective=(
        "Develop sustainable speed and threshold capacity."
    ),
    intensity="Moderately hard",
    description=(
        "Complete the main efforts at a controlled, "
        "sustainable intensity. The effort should be "
        "demanding without becoming maximal."
    ),
    structure=(
        "Progressive warm-up",
        "Technique drills",
        "Controlled threshold intervals",
        "Short recovery intervals",
        "Easy cool-down",
    ),
)

VO2MAX_TEMPLATE = WorkoutTemplate(
    purpose=SessionPurpose.INTENSITY,
    title="VO₂max Session",
    objective=(
        "Develop aerobic power and tolerance to high-intensity effort."
    ),
    intensity="Very hard",
    description=(
        "Complete short to medium-duration intervals at a strong, "
        "controlled intensity. Recover sufficiently to preserve "
        "quality across all repetitions."
    ),
    structure=(
        "Progressive warm-up",
        "Technique drills",
        "VO₂max intervals",
        "Recovery intervals",
        "Easy cool-down",
    ),
)

TEMPO_TEMPLATE = WorkoutTemplate(
    purpose=SessionPurpose.INTENSITY,
    title="Tempo Session",
    objective=(
        "Improve sustained aerobic performance at a comfortably "
        "hard pace."
    ),
    intensity="Hard",
    description=(
        "Maintain a steady, controlled effort for an extended "
        "period without significant pace fluctuations."
    ),
    structure=(
        "Progressive warm-up",
        "Running drills",
        "Continuous tempo effort",
        "Easy cool-down",
    ),
)

HILLS_TEMPLATE = WorkoutTemplate(
    purpose=SessionPurpose.INTENSITY,
    title="Hill Session",
    objective=(
        "Develop strength, running economy, and the ability to "
        "sustain controlled effort on climbs."
    ),
    intensity="Hard",
    description=(
        "Complete repeated uphill efforts with strong posture, "
        "controlled technique, and sufficient recovery to preserve "
        "quality across all repetitions."
    ),
    structure=(
        "Progressive warm-up",
        "Running drills",
        "Uphill repetitions",
        "Easy downhill recovery",
        "Easy cool-down",
    ),
)

SPEED_TEMPLATE = WorkoutTemplate(
    purpose=SessionPurpose.INTENSITY,
    title="Speed Session",
    objective=(
        "Develop running speed, neuromuscular coordination, "
        "and efficient movement at high intensity."
    ),
    intensity="Very hard",
    description=(
        "Complete short, fast repetitions with full control and "
        "sufficient recovery. Prioritize technique and movement "
        "quality over accumulated fatigue."
    ),
    structure=(
        "Progressive warm-up",
        "Running drills",
        "Short fast repetitions",
        "Full recovery between repetitions",
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

_FOCUSED_TEMPLATES = {
    (
        SessionPurpose.INTENSITY,
        "threshold",
    ): THRESHOLD_TEMPLATE,

    (
        SessionPurpose.INTENSITY,
        "vo2max",
    ): VO2MAX_TEMPLATE,

    (
        SessionPurpose.INTENSITY,
        "tempo",
    ): TEMPO_TEMPLATE,

    (
        SessionPurpose.INTENSITY,
        "hills",
    ): HILLS_TEMPLATE,

    (
        SessionPurpose.INTENSITY,
        "speed",
    ): SPEED_TEMPLATE,

}


DEFAULT_WORKOUT_TEMPLATES: Mapping[
    SessionPurpose,
    WorkoutTemplate,
] = MappingProxyType(
    _DEFAULT_TEMPLATES
)

def _normalize_focus(
    focus: str | None,
) -> str | None:

    if focus is None:
        return None

    if not isinstance(
        focus,
        str,
    ):
        raise TypeError(
            "focus must be a string or None"
        )

    normalized = focus.strip().casefold()

    if not normalized:
        raise ValueError(
            "focus cannot be empty"
        )

    return normalized

def template_for(
    purpose: SessionPurpose,
    *,
    focus: str | None = None,
) -> WorkoutTemplate:
    """
    Returns the most specific template available.

    A focused template is preferred when one exists.
    Otherwise, the default template for the session
    purpose is returned.
    """

    if not isinstance(
        purpose,
        SessionPurpose,
    ):
        raise TypeError(
            "purpose must be a SessionPurpose"
        )

    normalized_focus = _normalize_focus(
        focus
    )

    if normalized_focus is not None:

        focused_template = _FOCUSED_TEMPLATES.get(
            (
                purpose,
                normalized_focus,
            )
        )

        if focused_template is not None:
            return focused_template

    try:

        return DEFAULT_WORKOUT_TEMPLATES[
            purpose
        ]

    except KeyError as error:

        raise ValueError(
            f"No workout template exists for "
            f"{purpose.value!r}"
        ) from error