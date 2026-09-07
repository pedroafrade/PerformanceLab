"""
PerformanceLab

Workout stimulus classification.

Distinguishes training load from the specific training
stimulus represented by a planned or completed workout.
"""

from enum import Enum


class WorkoutStimulus(str, Enum):
    """
    Explicit physiological or event-specific workout focus.
    """

    EASY = "easy"
    LONG = "long"
    THRESHOLD = "threshold"
    TEMPO = "tempo"
    HILLS = "hills"
    VO2MAX = "vo2max"
    SPEED = "speed"
    RECOVERY = "recovery"
    RACE = "race"
    UNKNOWN = "unknown"


FOCUS_STIMULI = {
    "threshold": WorkoutStimulus.THRESHOLD,
    "lt2": WorkoutStimulus.THRESHOLD,
    "tempo": WorkoutStimulus.TEMPO,
    "hills": WorkoutStimulus.HILLS,
    "hill": WorkoutStimulus.HILLS,
    "vo2max": WorkoutStimulus.VO2MAX,
    "vo₂max": WorkoutStimulus.VO2MAX,
    "speed": WorkoutStimulus.SPEED,
}

PURPOSE_STIMULI = {
    "easy": WorkoutStimulus.EASY,
    "long": WorkoutStimulus.LONG,
    "recovery": WorkoutStimulus.RECOVERY,
    "race": WorkoutStimulus.RACE,
}

TEXT_STIMULI = (
    (
        (
            "hill rep",
            "hill session",
            "hill run",
            "uphill rep",
            "uphill interval",
        ),
        WorkoutStimulus.HILLS,
    ),
    (
        (
            "lt2",
            "threshold",
        ),
        WorkoutStimulus.THRESHOLD,
    ),
    (
        (
            "tempo",
        ),
        WorkoutStimulus.TEMPO,
    ),
    (
        (
            "vo2",
            "vo₂",
        ),
        WorkoutStimulus.VO2MAX,
    ),
    (
        (
            "speed",
            "sprint",
        ),
        WorkoutStimulus.SPEED,
    ),
    (
        (
            "long run",
            "long session",
            "long ride",
        ),
        WorkoutStimulus.LONG,
    ),
    (
        (
            "recovery",
            "regeneration",
        ),
        WorkoutStimulus.RECOVERY,
    ),
    (
        (
            "easy run",
            "easy session",
            "easy ride",
            "easy swim",
        ),
        WorkoutStimulus.EASY,
    ),
    (
        (
            "race",
        ),
        WorkoutStimulus.RACE,
    ),
)


def _normalised_text(*values) -> str:
    """
    Combines optional descriptive fields for conservative
    explicit-text classification.
    """

    return " ".join(
        str(value).strip().lower()
        for value in values
        if str(value or "").strip()
    )


def _stimulus_from_text(
    text: str,
) -> WorkoutStimulus:
    """
    Returns a stimulus only when an explicit marker exists.
    """

    for markers, stimulus in TEXT_STIMULI:

        if any(
            marker in text
            for marker in markers
        ):
            return stimulus

    return WorkoutStimulus.UNKNOWN


def planned_workout_stimulus(
    workout,
) -> WorkoutStimulus:
    """
    Classifies a planned workout.

    Structured focus has priority, followed by purpose.
    Text is retained only for compatibility with older plans.
    """

    focus = str(
        getattr(
            workout,
            "focus",
            None,
        )
        or ""
    ).strip().lower()

    if focus in FOCUS_STIMULI:
        return FOCUS_STIMULI[focus]

    purpose = str(
        getattr(
            workout,
            "purpose",
            None,
        )
        or ""
    ).strip().lower()

    if purpose in PURPOSE_STIMULI:
        return PURPOSE_STIMULI[
            purpose
        ]

    return _stimulus_from_text(
        _normalised_text(
            getattr(
                workout,
                "title",
                None,
            ),
            getattr(
                workout,
                "objective",
                None,
            ),
            getattr(
                workout,
                "prescription_summary",
                None,
            ),
        )
    )


def completed_workout_stimulus(
    workout,
) -> WorkoutStimulus:
    """
    Classifies a completed workout from explicit descriptive
    information.

    RPE alone is deliberately insufficient to claim Hill,
    Tempo or LT2 stimulus.
    """

    if workout is None:
        return WorkoutStimulus.UNKNOWN

    info = getattr(
        workout,
        "info",
        None,
    )

    return _stimulus_from_text(
        _normalised_text(
            getattr(
                info,
                "title",
                None,
            ),
            getattr(
                info,
                "description",
                None,
            ),
            getattr(
                workout,
                "title",
                None,
            ),
            getattr(
                workout,
                "description",
                None,
            ),
        )
    )


def stimuli_are_equivalent(
    planned: WorkoutStimulus,
    completed: WorkoutStimulus,
) -> bool | None:
    """
    Compares known stimuli.

    None means that the completed activity does not contain
    enough explicit information for a reliable comparison.
    """

    if not isinstance(
        planned,
        WorkoutStimulus,
    ):
        raise TypeError(
            "planned must be a WorkoutStimulus."
        )

    if not isinstance(
        completed,
        WorkoutStimulus,
    ):
        raise TypeError(
            "completed must be a WorkoutStimulus."
        )

    if (
        planned is WorkoutStimulus.UNKNOWN
        or completed is WorkoutStimulus.UNKNOWN
    ):
        return None

    return planned is completed