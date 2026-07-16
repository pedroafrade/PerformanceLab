"""
PerformanceLab

History

Container for an athlete's workouts.
"""

from dataclasses import dataclass, field
from datetime import date, datetime, time

from performancelab.workout import Workout


@dataclass
class History:

    workouts: list[Workout] = field(default_factory=list)

    # ======================================================

    def add(self, workout: Workout):

        self.workouts.append(workout)

        self._sort()

    # ======================================================

    def remove(self, workout: Workout):

        if workout in self.workouts:

            self.workouts.remove(workout)

    # ======================================================

    def clear(self):

        self.workouts.clear()

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