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

    total_minutes = round(
        duration_minutes
    )

    first_segment_end = (
        total_minutes * 20 + 50
    ) // 100

    second_segment_end = (
        total_minutes * 70 + 50
    ) // 100

    third_segment_end = (
        total_minutes * 90 + 50
    ) // 100

    final_segment_minutes = max(
        1,
        total_minutes
        - third_segment_end,
    )

    heart_rate_guidance = (
        _road_10k_heart_rate_guidance(
            heart_rate_profile
        )
    )

    pacing = (
        (
            f"First {first_segment_end} min "
            "(0–20%): start controlled, slightly "
            f"slower than the estimated {pace_text} "
            "average pace."
            f"{heart_rate_guidance[0]}"
        ),
        (
            f"Minutes {first_segment_end}–"
            f"{second_segment_end} "
            "(20–70%): settle into the estimated "
            "average pace while keeping breathing "
            "and running form controlled."
            f"{heart_rate_guidance[1]}"
        ),
        (
            f"Minutes {second_segment_end}–"
            f"{third_segment_end} "
            "(70–90%): increase effort progressively "
            "only if pacing, breathing and running form "
            "remain controlled."
            f"{heart_rate_guidance[2]}"
        ),
        (
            f"Final {final_segment_minutes} min "
            "(90–100%): if still controlled, use the "
            "strongest sustainable effort and build "
            "towards the finish."
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
    Returns conservative athlete-specific heart-rate
    guidance for a high-effort road 10 km.

    Manual zones and LT2 take precedence. Percentages of
    maximum heart rate provide secondary references.
    """

    if heart_rate_profile is None:
        return (
            "",
            "",
            "",
            "",
        )

    max_hr = getattr(
        heart_rate_profile,
        "max_hr",
        None,
    )

    threshold_hr = getattr(
        heart_rate_profile,
        "threshold_hr",
        None,
    )

    zone_method = getattr(
        heart_rate_profile,
        "zone",
        None,
    )

    zone_3 = (
        zone_method("Z3")
        if callable(zone_method)
        else None
    )

    zone_5 = (
        zone_method("Z5")
        if callable(zone_method)
        else None
    )

    if (
        max_hr is None
        or threshold_hr is None
    ):
        return (
            "",
            "",
            "",
            "",
        )

    opening_reference = round(
        max_hr * 0.80
    )

    late_reference = round(
        max_hr * 0.90
    )

    if zone_3 is not None:

        opening_text = (
            " Heart-rate guide: remain in Z3 "
            f"({zone_3.lower_bpm}–"
            f"{zone_3.upper_bpm} bpm), using approximately "
            f"{opening_reference} bpm as a conservative "
            "opening reference rather than a target to chase."
        )

    else:

        opening_text = (
            " Heart-rate guide: use approximately "
            f"{opening_reference} bpm "
            "(80% of maximum heart rate) as a conservative "
            "opening reference."
        )

    threshold_text = (
        " Heart-rate guide: stabilise progressively around "
        f"LT2 ({threshold_hr} bpm). Allow normal cardiac "
        "drift rather than accelerating merely to reach "
        "the number."
    )

    if zone_5 is not None:

        late_text = (
            " Heart-rate guide: if feeling controlled, "
            f"allow heart rate to rise towards approximately "
            f"{late_reference} bpm "
            "(90% of maximum heart rate). Enter low Z5 "
            f"from {zone_5.lower_bpm} bpm only if it occurs "
            "naturally without loss of form."
        )

    else:

        late_text = (
            " Heart-rate guide: if feeling controlled, "
            f"allow heart rate to rise towards approximately "
            f"{late_reference} bpm "
            "(90% of maximum heart rate)."
        )

    final_text = (
        " Heart-rate guide: effort, breathing and running "
        "form now take precedence. Heart rate is observed, "
        "not chased."
    )

    return (
        opening_text,
        threshold_text,
        late_text,
        final_text,
    )