"""
PerformanceLab

Workout Templates

Default reusable workout templates.
"""

from types import MappingProxyType
from typing import Mapping

from .session_purpose import SessionPurpose
from .training_focus import TrainingFocus
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

TECHNIQUE_TEMPLATE = WorkoutTemplate(
    purpose=SessionPurpose.TECHNIQUE,
    title="Technique Session",
    objective=(
        "Develop efficient movement and confidence "
        "on event-specific terrain."
    ),
    intensity="Easy to moderate",
    description=(
        "Keep the overall effort aerobic while practising "
        "controlled climbing and relaxed descending technique."
    ),
    structure=(
        "Easy aerobic warm-up",
        "Controlled climbing technique",
        "Relaxed downhill technique",
        "Easy cool-down",
    ),
)

PRE_RACE_TEMPLATE = WorkoutTemplate(
    purpose=SessionPurpose.PRE_RACE,
    title="Pre-Race Easy Session",
    objective=(
        "Maintain readiness while reducing training "
        "stress before competition."
    ),
    intensity="Easy",
    description=(
        "Run easily on terrain appropriate to the event "
        "and finish with short, relaxed accelerations. "
        "The session should preserve freshness."
    ),
    structure=(
        "Warm up 10 min",
        "Easy aerobic running 10 min",
        (
            "4×20 sec relaxed strides with full "
            "easy recovery"
        ),
        "Cool down 5 min",
    ),
)

SHAKEOUT_TEMPLATE = WorkoutTemplate(
    purpose=SessionPurpose.SHAKEOUT,
    title="Shakeout Session",
    objective=(
        "Activate the body without creating fatigue "
        "before competition."
    ),
    intensity="Very easy",
    description=(
        "Run very easily and finish with a few short, "
        "relaxed accelerations. The session should leave "
        "the athlete feeling fresher, not tired."
    ),
    structure=(
        "Easy running 10 min",
        (
            "4×20 sec relaxed strides with full "
            "easy recovery (5 min block)"
        ),
        "Easy running 5 min",
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
    title="LT2 Session",
    objective="Develop sustainable LT2 capacity.",
    intensity="Moderately hard",
    description=(
        "Complete sustained efforts near LT2 while "
        "maintaining controlled pacing and good technique."
    ),
    structure=(
        "Progressive warm-up",
        "Controlled LT2 intervals",
        "Controlled recoveries",
        "Easy cool-down",
    ),
)


VO2MAX_TEMPLATE = WorkoutTemplate(
    purpose=SessionPurpose.INTENSITY,
    title="VO₂max Session",
    objective="Develop maximal aerobic power.",
    intensity="Very hard",
    description=(
        "Perform short, demanding intervals with enough "
        "recovery to preserve movement quality."
    ),
    structure=(
        "Progressive warm-up",
        "VO₂max intervals",
        "Recovery intervals",
        "Easy cool-down",
    ),
)


TEMPO_TEMPLATE = WorkoutTemplate(
    purpose=SessionPurpose.INTENSITY,
    title="Tempo Session",
    objective="Develop sustained aerobic speed.",
    intensity="Hard",
    description=(
        "Maintain a strong but controlled continuous effort."
    ),
    structure=(
        "Progressive warm-up",
        "Continuous tempo effort",
        "Easy cool-down",
    ),
)


HILLS_TEMPLATE = WorkoutTemplate(
    purpose=SessionPurpose.INTENSITY,
    title="Hill Session",
    objective="Develop strength and power on climbs.",
    intensity="Hard",
    description=(
        "Run or ride the climbs with controlled power and "
        "recover fully enough to maintain good technique."
    ),
    structure=(
        "Progressive warm-up",
        "Uphill repetitions",
        "Easy downhill recovery",
        "Easy cool-down",
    ),
)


SPEED_TEMPLATE = WorkoutTemplate(
    purpose=SessionPurpose.INTENSITY,
    title="Speed Session",
    objective="Develop speed and neuromuscular efficiency.",
    intensity="Very hard",
    description=(
        "Perform short fast repetitions with complete or "
        "near-complete recovery."
    ),
    structure=(
        "Progressive warm-up",
        "Technique drills",
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
    SessionPurpose.TECHNIQUE: TECHNIQUE_TEMPLATE,
    SessionPurpose.PRE_RACE: PRE_RACE_TEMPLATE,
    SessionPurpose.SHAKEOUT: SHAKEOUT_TEMPLATE,
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


_FOCUSED_TEMPLATES = {
    (
        SessionPurpose.INTENSITY,
        TrainingFocus.THRESHOLD,
    ): THRESHOLD_TEMPLATE,
    (
        SessionPurpose.INTENSITY,
        TrainingFocus.VO2MAX,
    ): VO2MAX_TEMPLATE,
    (
        SessionPurpose.INTENSITY,
        TrainingFocus.TEMPO,
    ): TEMPO_TEMPLATE,
    (
        SessionPurpose.INTENSITY,
        TrainingFocus.HILLS,
    ): HILLS_TEMPLATE,
    (
        SessionPurpose.INTENSITY,
        TrainingFocus.SPEED,
    ): SPEED_TEMPLATE,
}


FOCUSED_WORKOUT_TEMPLATES: Mapping[
    tuple[SessionPurpose, TrainingFocus],
    WorkoutTemplate,
] = MappingProxyType(
    _FOCUSED_TEMPLATES
)


def _normalize_focus(
    focus: str | TrainingFocus | None,
) -> TrainingFocus | None:
    if focus is None:
        return None

    if isinstance(
        focus,
        TrainingFocus,
    ):
        return focus

    if not isinstance(
        focus,
        str,
    ):
        raise TypeError(
            "focus must be a string or TrainingFocus"
        )

    normalized_focus = focus.strip().lower()

    if not normalized_focus:
        raise ValueError(
            "focus must not be empty"
        )

    try:
        return TrainingFocus(
            normalized_focus
        )
    except ValueError:
        return None


def template_for(
    purpose: SessionPurpose,
    *,
    focus: str | TrainingFocus | None = None,
) -> WorkoutTemplate:
    """
    Returns a focus-specific template when available.

    Otherwise, returns the default template for the session purpose.
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
        focused_template = FOCUSED_WORKOUT_TEMPLATES.get(
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
