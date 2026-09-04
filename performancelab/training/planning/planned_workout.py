"""
PerformanceLab

Planned Workout

Represents one planned workout.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
import re


_LEGACY_CONTINUOUS_RUN_STEP = re.compile(
    r"(?P<label>(?:Easy|Long) aerobic run"
    r"(?: on (?:mountainous|hilly|rolling) terrain)?) "
    r"\d+ min"
)
_LEGACY_WARM_UP_STEP = re.compile(r"Warm up \d+ min")
_LEGACY_COOL_DOWN_STEP = re.compile(r"Cool down \d+ min")


@dataclass(frozen=True)
class PlannedWorkout:
    """
    Represents one planned workout.
    """

    scheduled_at: datetime

    sport: str | None = None
    title: str | None = None

    duration: timedelta | None = None
    distance: float | None = None
    elevation_gain: float | None = None

    description: str | None = None
    prescription_summary: str | None = None
    intensity: str | None = None
    objective: str | None = None

    structure: tuple[str, ...] = ()
    equipment: tuple[str, ...] = ()

    phase: str | None = None
    
    # ======================================================

    @property
    def day(self):

        return self.scheduled_at.date()

    # ======================================================

    @property
    def is_rest(self):

        return (
            self.sport is None
            and self.title is None
            and self.duration is None
            and self.distance is None
        )

    # ======================================================

    @property
    def presentation_structure(self) -> tuple[str, ...]:
        """
        Returns a display-safe structure for planned sessions.

        Older generated Easy Runs and Long Runs stored their
        opening and closing periods as separate timed steps.
        They remain unchanged in storage, while presentation
        shows the factual total as one continuous run.
        """

        structure = tuple(
            str(step).strip()
            for step in self.structure
            if str(step).strip()
        )

        if (
            self.duration is None
            or "running" not in str(
                self.sport or ""
            ).strip().lower()
        ):
            return structure

        main_matches = tuple(
            (index, match)
            for index, step in enumerate(structure)
            if (
                match := _LEGACY_CONTINUOUS_RUN_STEP.fullmatch(
                    step
                )
            )
        )

        has_warm_up = any(
            _LEGACY_WARM_UP_STEP.fullmatch(step)
            for step in structure
        )
        has_cool_down = any(
            _LEGACY_COOL_DOWN_STEP.fullmatch(step)
            for step in structure
        )

        if (
            len(main_matches) != 1
            or not has_warm_up
            or not has_cool_down
        ):
            return structure

        main_index, main_match = main_matches[0]
        total_minutes = round(
            self.duration.total_seconds() / 60
        )

        return tuple(
            (
                f"{main_match.group('label')} "
                f"{total_minutes} min"
                if index == main_index
                else step
            )
            for index, step in enumerate(structure)
            if (
                not _LEGACY_WARM_UP_STEP.fullmatch(step)
                and not _LEGACY_COOL_DOWN_STEP.fullmatch(step)
            )
        )

    # ======================================================

    def __repr__(self):

        return (
            "PlannedWorkout("
            f"{self.scheduled_at.isoformat()}, "
            f"sport={self.sport!r}, "
            f"title={self.title!r})"
        )
