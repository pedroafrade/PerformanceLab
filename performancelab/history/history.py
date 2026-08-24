"""
PerformanceLab

History

Container for an athlete's workouts.
"""

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta

from performancelab.workout import Workout

from collections.abc import Callable


MATCHING_TIME_TOLERANCE = timedelta(
    minutes=5
)

MATCHING_DURATION_TOLERANCE = timedelta(
    minutes=1
)

MATCHING_DISTANCE_TOLERANCE_KM = 0.1

@dataclass(
    frozen=True
)
class WorkoutMergeResult:
    """
    Factual result of merging one completed workout.
    """

    workout: Workout
    status: str

    def __post_init__(
        self,
    ) -> None:

        if self.status not in (
            "imported",
            "updated",
            "duplicate",
        ):

            raise ValueError(
                "Workout merge status must be "
                "imported, updated or duplicate."
            )

@dataclass
class History:

    workouts: list[Workout] = field(default_factory=list)

    on_change: Callable[[], None] | None = field(
        default=None,
        repr=False,
        compare=False,
    )

    def _notify_change(self) -> None:

        if self.on_change is not None:

            self.on_change()

    # ======================================================

    def add(self, workout: Workout):

        self.workouts.append(workout)

        self._sort()

    # ======================================================
    
    def find_matching(
        self,
        workout: Workout,
    ) -> Workout | None:
        """
        Finds an existing workout representing the same activity.
        """

        for existing in self.workouts:

            if self._workouts_match(
                existing,
                workout,
            ):

                return existing

        return None

    # ======================================================

    def merge_with_result(
        self,
        workout: Workout,
    ) -> WorkoutMergeResult:
        """
        Add, enrich or recognize a duplicate workout.
        """

        existing = self.find_matching(
            workout
        )

        if existing is None:

            self.add(
                workout
            )

            return WorkoutMergeResult(
                workout=workout,
                status="imported",
            )

        changed = False

        if (
            self._is_placeholder_title(
                existing.info.title
            )
            and not self._is_placeholder_title(
                workout.info.title
            )
        ):

            existing.info.title = (
                workout.info.title
            )

            changed = True

        if (
            workout.feedback.estimated_rpe
            is not None
            and (
                existing
                .feedback
                .estimated_rpe
                != workout
                .feedback
                .estimated_rpe
            )
        ):

            existing.feedback.estimated_rpe = (
                workout.feedback.estimated_rpe
            )

            changed = True

        for name, sensor in workout.sensors:

            existing_sensor = (
                existing.sensors.get(
                    name
                )
            )

            if not self._values_equal(
                existing_sensor,
                sensor,
            ):

                changed = True

            existing.sensors.add(
                name,
                sensor,
            )

        self._notify_change()

        return WorkoutMergeResult(
            workout=existing,
            status=(
                "updated"
                if changed
                else "duplicate"
            ),
        )

    def merge(
        self,
        workout: Workout,
    ) -> tuple[Workout, bool]:
        """
        Preserve the existing merge contract.

        New callers that require a factual status should use
        merge_with_result().
        """

        result = self.merge_with_result(
            workout
        )

        return (
            result.workout,
            result.status
            == "imported",
        )

    @staticmethod
    def _values_equal(
        first,
        second,
    ) -> bool:
        """
        Compare sensor values without assuming a specific type.
        """

        try:

            return bool(
                first
                == second
            )

        except (
            TypeError,
            ValueError,
        ):

            return False

    # ======================================================
    @staticmethod
    def _is_placeholder_title(
        value,
    ) -> bool:
        """
        Identifies an empty or numeric activity title.
        """

        title = str(
            value or ""
        ).strip()

        return (
            not title
            or title.isdigit()
        )

    # ======================================================
    @classmethod
    def _workouts_match(
        cls,
        existing: Workout,
        candidate: Workout,
    ) -> bool:
        """
        Compares the identifying information of two workouts.
        """

        if (
            existing.date is None
            or candidate.date is None
        ):
            return False

        if (
            str(existing.sport or "").lower()
            != str(candidate.sport or "").lower()
        ):
            return False

        existing_date = cls._sortable_date(
            existing.date
        )

        candidate_date = cls._sortable_date(
            candidate.date
        )

        if (
            isinstance(existing.date, datetime)
            and isinstance(candidate.date, datetime)
        ):

            if (
                abs(existing_date - candidate_date)
                > MATCHING_TIME_TOLERANCE
            ):
                return False

        elif existing_date.date() != candidate_date.date():
            return False

        if (
            existing.duration is None
            or candidate.duration is None
        ):
            return False

        if (
            abs(
                existing.duration
                - candidate.duration
            )
            > MATCHING_DURATION_TOLERANCE
        ):
            return False

        if (
            existing.distance is None
            or candidate.distance is None
        ):
            return False

        return (
            abs(
                existing.distance
                - candidate.distance
            )
            <= MATCHING_DISTANCE_TOLERANCE_KM
        )

    # ======================================================

    def remove(self, workout: Workout):

        if workout in self.workouts:

            self.workouts.remove(workout)

            self._notify_change()

    # ======================================================

    def remove_many(
        self,
        workouts,
    ) -> int:
        """
        Removes multiple workouts and notifies once.

        Returns the number of removed workouts.
        """

        removed_count = 0

        for workout in list(workouts):

            if workout not in self.workouts:
                continue

            self.workouts.remove(workout)
            removed_count += 1

        if removed_count:

            self._notify_change()

        return removed_count

    # ======================================================

    def clear(self):

        self.workouts.clear()

        self._notify_change()

    # ======================================================

    @staticmethod
    def _sortable_date(value):

        if value is None:

            return datetime.max

        if isinstance(value, datetime):

            return value.replace(tzinfo=None)

        if isinstance(value, date):

            return datetime.combine(
                value,
                time.min,
            )

        raise TypeError(
            "Workout date must be a date, datetime or None."
        )

    # ======================================================

    def _sort(self):

        self.workouts.sort(
            key=lambda workout: self._sortable_date(
                workout.date
            )
        )

        self._notify_change()

    # ======================================================

    @property
    def sports(self):

        sports = {

            workout.sport

            for workout in self.workouts

            if workout.sport

        }

        return sorted(sports)

    # ======================================================

    @property
    def first(self):

        if not self.workouts:

            return None

        return self.workouts[0]

    # ======================================================

    @property
    def last(self):

        if not self.workouts:

            return None

        return self.workouts[-1]

    # ======================================================

    def __len__(self):

        return len(self.workouts)

    # ======================================================

    def __iter__(self):

        return iter(self.workouts)

    # ======================================================

    def __getitem__(self, index):

        return self.workouts[index]

    # ======================================================

    def __contains__(self, workout):

        return workout in self.workouts

    # ======================================================

    def __repr__(self):

        return (
            f"History("
            f"{len(self.workouts)} workouts)"
        )