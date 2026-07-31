"""
PerformanceLab

Heart Rate Target

Defines the heart-rate training zones associated with each
coaching session purpose.
"""

from dataclasses import dataclass

from .session_purpose import (
    SessionPurpose,
)


@dataclass(frozen=True, slots=True)
class HeartRateTarget:
    """
    Immutable semantic heart-rate target.

    Zone names are resolved against the athlete's
    HeartRateProfile later in the planning pipeline.
    """

    zone_names: tuple[str, ...]

    def __post_init__(self) -> None:

        normalized_names = tuple(
            str(name)
            .strip()
            .upper()
            for name in self.zone_names
        )

        if not normalized_names:

            raise ValueError(
                "Heart-rate target must contain "
                "at least one zone."
            )

        if any(
            not name
            for name in normalized_names
        ):

            raise ValueError(
                "Heart-rate zone names cannot be empty."
            )

        if (
            len(normalized_names)
            != len(set(normalized_names))
        ):

            raise ValueError(
                "Heart-rate target zones must be unique."
            )

        object.__setattr__(
            self,
            "zone_names",
            normalized_names,
        )

    # ======================================================

    @property
    def primary_zone(self) -> str:

        return self.zone_names[0]

    # ======================================================

    @property
    def label(self) -> str:
        """
        Returns a concise semantic zone label.
        """

        return "–".join(
            self.zone_names
        )


# ======================================================

def heart_rate_target_for(
    purpose: SessionPurpose,
    *,
    focus: str | None = None,
) -> HeartRateTarget | None:
    """
    Returns the semantic heart-rate target for a session.

    Rest and race sessions do not receive a generic target.
    Race targets must be defined by an event-specific
    execution strategy.
    """

    if not isinstance(
        purpose,
        SessionPurpose,
    ):

        raise TypeError(
            "purpose must be a SessionPurpose"
        )

    if purpose in {
        SessionPurpose.REST,
        SessionPurpose.RACE,
    }:

        return None

    if purpose is SessionPurpose.RECOVERY:

        return HeartRateTarget(
            ("Z1",)
        )

    if purpose is SessionPurpose.SHAKEOUT:

        return HeartRateTarget(
            ("Z1", "Z2")
        )

    if purpose in {
        SessionPurpose.EASY,
        SessionPurpose.LONG,
        SessionPurpose.CROSS_TRAINING,
        SessionPurpose.PRE_RACE,
    }:

        return HeartRateTarget(
            ("Z2",)
        )

    if purpose is SessionPurpose.TECHNIQUE:

        return HeartRateTarget(
            ("Z2", "Z3")
        )

    if purpose is SessionPurpose.INTENSITY:

        normalized_focus = str(
            focus or ""
        ).strip().lower()

        if normalized_focus == "tempo":

            return HeartRateTarget(
                ("Z3", "Z4")
            )

        if normalized_focus == "threshold":

            return HeartRateTarget(
                ("Z4",)
            )

        if normalized_focus in {
            "hills",
            "speed",
        }:

            return HeartRateTarget(
                ("Z4", "Z5")
            )

        if normalized_focus == "vo2max":

            return HeartRateTarget(
                ("Z5",)
            )

        return HeartRateTarget(
            ("Z4",)
        )

    return None