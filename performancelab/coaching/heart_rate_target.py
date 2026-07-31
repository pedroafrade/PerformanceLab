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

    threshold_range: (
        tuple[float, float] | None
    ) = None

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

        if self.threshold_range is not None:

            if (
                not isinstance(
                    self.threshold_range,
                    tuple,
                )
                or len(
                    self.threshold_range
                ) != 2
            ):

                raise TypeError(
                    "threshold_range must be a "
                    "two-value tuple or None."
                )

            lower_ratio, upper_ratio = (
                self.threshold_range
            )

            if (
                not isinstance(
                    lower_ratio,
                    (int, float),
                )
                or not isinstance(
                    upper_ratio,
                    (int, float),
                )
            ):

                raise TypeError(
                    "threshold_range values must "
                    "be numeric."
                )

            if (
                lower_ratio <= 0
                or upper_ratio < lower_ratio
            ):

                raise ValueError(
                    "Invalid threshold heart-rate "
                    "range."
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
                zone_names=(
                    "Z3",
                    "Z4",
                ),
                threshold_range=(
                    0.95,
                    0.99,
                ),
            )

        if normalized_focus == "threshold":

            return HeartRateTarget(
                zone_names=(
                    "Z4",
                ),
                threshold_range=(
                    1.00,
                    1.02,
                ),
            )

        if normalized_focus in {
            "hills",
            "speed",
        }:

            return HeartRateTarget(
                ("Z4",)
            )

        if normalized_focus == "vo2max":

            return HeartRateTarget(
                ("Z5",)
            )

        return HeartRateTarget(
            ("Z4",)
        )

    return None