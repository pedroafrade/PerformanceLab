"""
PerformanceLab

Race Execution Plan

Represents the athlete-specific strategy for executing
a registered competition.
"""

from dataclasses import dataclass
from datetime import timedelta


@dataclass(frozen=True)
class RaceExecutionPlan:
    """
    Immutable race-day execution guidance.

    The plan contains competition pacing, hydration and
    nutrition guidance. Training-week organisation remains
    the responsibility of RaceStrategy.
    """

    expected_duration: timedelta

    pacing: tuple[str, ...]
    hydration: tuple[str, ...]
    nutrition: tuple[str, ...]

    # ======================================================

    @property
    def guidance(self) -> tuple[str, ...]:
        """
        Returns all race guidance in presentation order.
        """

        return (
            *self.pacing,
            *self.hydration,
            *self.nutrition,
        )


def build_race_execution_plan(
    *,
    event,
    expected_duration: timedelta | None,
    heart_rate_profile=None,
) -> RaceExecutionPlan | None:
    """
    Builds an event-specific race execution plan.

    Road-running events between 8 and 12 kilometres receive
    a 10 km pacing strategy. Unsupported events return None
    until an appropriate strategy is implemented.
    """

    if (
        event is None
        or expected_duration is None
        or expected_duration.total_seconds() <= 0
    ):
        return None

    sport = str(
        getattr(
            event,
            "sport",
            "",
        )
        or ""
    ).strip().lower()

    distance = getattr(
        event,
        "distance",
        None,
    )

    is_road_10k_event = (
        sport == "road running"
        and isinstance(
            distance,
            (int, float),
        )
        and not isinstance(
            distance,
            bool,
        )
        and 8 <= distance <= 12
    )

    if not is_road_10k_event:
        return None

    duration_minutes = (
        expected_duration.total_seconds()
        / 60
    )

    target_pace = (
        duration_minutes
        / float(distance)
    )

    pace_minutes = int(
        target_pace
    )

    pace_seconds = round(
        (
            target_pace
            - pace_minutes
        )
        * 60
    )

    if pace_seconds == 60:
        pace_minutes += 1
        pace_seconds = 0

    pace_text = (
        f"{pace_minutes}:"
        f"{pace_seconds:02d}/km"
    )

    heart_rate_guidance = (
        _road_10k_heart_rate_guidance(
            heart_rate_profile
        )
    )

    pacing = (
        (
            "First 2 km: start controlled, slightly "
            f"slower than the estimated {pace_text} "
            "average pace."
            f"{heart_rate_guidance[0]}"
        ),
        (
            "Km 3–7: settle into the estimated average "
            "effort; maintain control on climbs and avoid "
            "chasing exact pace."
            f"{heart_rate_guidance[1]}"
        ),
        (
            "Km 8–9: increase effort progressively if "
            "breathing and running form remain controlled."
            f"{heart_rate_guidance[2]}"
        ),
        (
            "Final kilometre: use the strongest sustainable "
            "effort and build towards the finish."
            f"{heart_rate_guidance[3]}"
        ),
    )

    hydration = (
        (
            "Arrive normally hydrated; take a small drink "
            "before the start if conditions require it."
        ),
        (
            "During the race, drink only if needed because "
            "of heat, thirst or unusually demanding conditions."
        ),
    )

    nutrition = (
        (
            "Use a familiar pre-race meal and avoid trying "
            "new food or supplements."
        ),
        (
            "In-race carbohydrate is normally unnecessary "
            "for an expected duration below 60 minutes."
        ),
    )

    return RaceExecutionPlan(
        expected_duration=expected_duration,
        pacing=pacing,
        hydration=hydration,
        nutrition=nutrition,
    )

def _road_10k_heart_rate_guidance(
    heart_rate_profile,
) -> tuple[str, str, str, str]:
    """
    Returns athlete-specific heart-rate guidance for a
    high-effort road 10 km.

    Missing or incomplete profiles preserve the existing
    pace-only strategy.
    """

    if heart_rate_profile is None:
        return (
            "",
            "",
            "",
            "",
        )

    zone_method = getattr(
        heart_rate_profile,
        "zone",
        None,
    )

    if not callable(zone_method):
        return (
            "",
            "",
            "",
            "",
        )

    zone_4 = zone_method("Z4")
    zone_5 = zone_method("Z5")

    if (
        zone_4 is None
        or zone_5 is None
    ):
        return (
            "",
            "",
            "",
            "",
        )

    upper_z4_start = (
        zone_4.lower_bpm
        + (
            zone_4.upper_bpm
            - zone_4.lower_bpm
        )
        // 2
    )

    low_z5_upper = min(
        zone_5.upper_bpm,
        zone_5.lower_bpm + 5,
    )

    return (
        (
            " Heart-rate guide: remain in Z4 "
            f"({zone_4.lower_bpm}–"
            f"{zone_4.upper_bpm} bpm)."
        ),
        (
            " Heart-rate guide: use upper Z4 "
            f"({upper_z4_start}–"
            f"{zone_4.upper_bpm} bpm)."
        ),
        (
            " Heart-rate guide: progress into low Z5 "
            f"({zone_5.lower_bpm}–"
            f"{low_z5_upper} bpm)."
        ),
        (
            " Heart-rate guide: progress through Z5 from "
            f"{zone_5.lower_bpm} bpm without chasing "
            "maximum heart rate."
        ),
    )