"""
PerformanceLab

History

Container for an athlete's workouts.
"""

from dataclasses import dataclass, field

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

    def _sort(self):

        self.workouts.sort(

            key=lambda workout: (

                workout.date is None,

                workout.date,

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