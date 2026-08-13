"""
PerformanceLab

Race Execution Plan

Represents the athlete-specific strategy for executing
a registered competition.
"""

from dataclasses import dataclass
from datetime import timedelta

from performancelab.analysis import (
    NutritionProfile,
)

DEFAULT_CARBOHYDRATE_LOWER_G_PER_HOUR = 30
DEFAULT_CARBOHYDRATE_UPPER_G_PER_HOUR = 60

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
    nutrition_profile=None,
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

    is_long_trail_event = (
        sport == "trail running"
        and isinstance(
            distance,
            (int, float),
        )
        and not isinstance(
            distance,
            bool,
        )
        and distance >= 15
    )

    if is_long_trail_event:

        return _build_long_trail_execution_plan(
            event=event,
            expected_duration=expected_duration,
            heart_rate_profile=(
                heart_rate_profile
            ),
            nutrition_profile=(
                nutrition_profile
            ),
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

def _rounded_carbohydrate_total(
    *,
    grams_per_hour: int,
    duration: timedelta,
) -> int:
    """
    Converts an hourly carbohydrate reference into a
    practical total rounded to five grams.
    """

    hours = (
        duration.total_seconds()
        / 3600
    )

    value = (
        hours
        * grams_per_hour
    )

    return int(
        value / 5
        + 0.5
    ) * 5

def _build_long_trail_execution_plan(
    *,
    event,
    expected_duration: timedelta,
    heart_rate_profile,
    nutrition_profile,
) -> RaceExecutionPlan:
    """
    Builds a duration-based execution strategy for a
    long trail-running event.
    """

    total_minutes = round(
        expected_duration.total_seconds()
        / 60
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
        _long_trail_heart_rate_guidance(
            heart_rate_profile
        )
    )

    pacing = (
        (
            f"First {first_segment_end} min "
            "(0–20%): start conservatively. Run the "
            "comfortable terrain, use purposeful hiking "
            "on steep climbs and avoid gaining time on "
            "technical descents."
            f"{heart_rate_guidance[0]}"
        ),
        (
            f"Minutes {first_segment_end}–"
            f"{second_segment_end} "
            "(20–70%): establish a sustainable rhythm. "
            "Keep climbs aerobic, run efficiently on "
            "faster terrain and protect the legs on "
            "descents."
            f"{heart_rate_guidance[1]}"
        ),
        (
            f"Minutes {second_segment_end}–"
            f"{third_segment_end} "
            "(70–90%): increase effort only if nutrition, "
            "muscular condition and running form remain "
            "stable. Continue hiking steep gradients "
            "before they force excessive effort."
            f"{heart_rate_guidance[2]}"
        ),
        (
            f"Final {final_segment_minutes} min "
            "(90–100%): progressively use the remaining "
            "capacity. Prioritise safe technique and only "
            "push fully when the terrain permits it."
            f"{heart_rate_guidance[3]}"
        ),
    )

    resolved_nutrition_profile = (
        nutrition_profile
        if isinstance(
            nutrition_profile,
            NutritionProfile,
        )
        else NutritionProfile()
    )

    fluid_lower_ml, fluid_upper_ml = (
        resolved_nutrition_profile.fluid_for(
            expected_duration
        )
    )

    fluid_lower_litres = (
        fluid_lower_ml / 1000
    )

    fluid_upper_litres = (
        fluid_upper_ml / 1000
    )

    sodium_lower, sodium_upper = (
        resolved_nutrition_profile.sodium_for(
            expected_duration
        )
    )

    nutrition_is_tested = (
        resolved_nutrition_profile
        .is_athlete_tested
    )

    carbohydrate_per_hour = (
        resolved_nutrition_profile
        .carbohydrate_per_hour
    )

    total_carbohydrate = (
        resolved_nutrition_profile
        .carbohydrate_for(
            expected_duration
        )
    )

    gel_count = max(
        1,
        total_minutes // 30,
    )

    gel_size = (
        resolved_nutrition_profile
        .gel_carbohydrate_grams
    )

    gel_carbohydrate = (
        gel_count * gel_size
    )

    remaining_carbohydrate = max(
        0,
        total_carbohydrate
        - gel_carbohydrate,
    )

    default_carbohydrate_lower = (
        _rounded_carbohydrate_total(
            grams_per_hour=(
                DEFAULT_CARBOHYDRATE_LOWER_G_PER_HOUR
            ),
            duration=expected_duration,
        )
    )

    default_carbohydrate_upper = (
        _rounded_carbohydrate_total(
            grams_per_hour=(
                DEFAULT_CARBOHYDRATE_UPPER_G_PER_HOUR
            ),
            duration=expected_duration,
        )
    )

    hydration = (
        (
            "Start normally hydrated. For the estimated "
            f"duration, plan approximately "
            f"{fluid_lower_litres:.1f}–"
            f"{fluid_upper_litres:.1f} L of fluid, "
            "adjusted for temperature, humidity, thirst "
            "and available aid stations."
        ),
        (
            "Use approximately "
            f"{resolved_nutrition_profile.fluid_lower_ml_per_hour}–"
            f"{resolved_nutrition_profile.fluid_upper_ml_per_hour} "
            "ml/h as an initial "
            "range. Avoid both forced overdrinking and "
            "waiting until substantial thirst develops."
        ),
        (
            f"Use approximately {sodium_lower}–"
            f"{sodium_upper} mg of sodium across the race "
            f"({resolved_nutrition_profile.sodium_lower_mg_per_hour}–"
            f"{resolved_nutrition_profile.sodium_upper_mg_per_hour} "
            "mg/h) as a provisional range. Test "
            "the products and quantities during long runs."
        ),
    )

    if nutrition_is_tested:

        nutrition = (
            (
                "Use the athlete-tested pre-race meal. "
                f"Approximately "
                f"{resolved_nutrition_profile.pre_race_carbohydrate_lower}–"
                f"{resolved_nutrition_profile.pre_race_carbohydrate_upper} "
                "g of carbohydrate in the final hour may "
                "be used as already tolerated."
            ),
            (
                "Use the athlete-tested target of "
                f"{carbohydrate_per_hour} g of carbohydrate "
                "per hour, corresponding to about "
                f"{total_carbohydrate} g across the "
                "estimated race duration."
            ),
            (
                f"One tested implementation may use "
                f"{gel_count} gels of {gel_size} g, "
                "approximately every 30 minutes, providing "
                f"{gel_carbohydrate} g. Obtain the remaining "
                f"approximately {remaining_carbohydrate} g "
                "from the athlete-tested drink or familiar "
                "food."
            ),
            (
                "Begin intake during the first 20–30 minutes. "
                "Use the timing and products already tolerated "
                "during training."
            ),
        )

    else:

        nutrition = (
            (
                "Use a familiar pre-race meal and avoid "
                "introducing new food, supplements or "
                "quantities on race day."
            ),
            (
                "No athlete-tested carbohydrate intake is "
                "recorded. Use 30–60 g of carbohydrate per "
                "hour as a provisional range, beginning near "
                "the lower end unless higher intake has "
                "already been tolerated."
            ),
            (
                "For the estimated duration, this provisional "
                f"range corresponds to approximately "
                f"{default_carbohydrate_lower}–"
                f"{default_carbohydrate_upper} g in total. "
                "Do not assume that 80–90 g/h is tolerated "
                "without progressive practice."
            ),
            (
                "Begin intake during the first 20–30 minutes "
                "and use small, regular doses. Adjust or stop "
                "if gastrointestinal discomfort develops."
            ),
        )

    return RaceExecutionPlan(
        expected_duration=expected_duration,
        pacing=pacing,
        hydration=hydration,
        nutrition=nutrition,
    )


def _long_trail_heart_rate_guidance(
    heart_rate_profile,
) -> tuple[str, str, str, str]:
    """
    Returns conservative heart-rate guidance for a
    long trail-running event.
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

    if zone_3 is not None:

        middle_reference = (
            f"Z3 ({zone_3.lower_bpm}–"
            f"{zone_3.upper_bpm} bpm)"
        )

    else:

        middle_reference = (
            "a controlled aerobic effort"
        )

    return (
        (
            " Heart-rate guide: remain comfortably below "
            f"approximately {opening_reference} bpm "
            "(80% of maximum heart rate), especially on "
            "the opening climbs."
        ),
        (
            " Heart-rate guide: remain mainly in "
            f"{middle_reference}. Brief rises towards LT2 "
            f"({threshold_hr} bpm) are acceptable on climbs "
            "when followed by recovery."
        ),
        (
            " Heart-rate guide: if muscular condition and "
            "nutrition remain stable, allow controlled "
            f"periods around LT2 ({threshold_hr} bpm), "
            "without sustaining this effort on every climb."
        ),
        (
            " Heart-rate guide: effort, terrain safety and "
            "running form take precedence. Heart rate is "
            "observed rather than chased."
        ),
    )