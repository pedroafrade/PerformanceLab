 """
PerformanceLab

History
-------

Histórico de sessões de um atleta.
"""

from dataclasses import dataclass, field
from datetime import timedelta

import pandas as pd


@dataclass
class History:

    athlete: object

    workouts: list = field(default_factory=list)

    # ======================================================

    def add(self, workout):

    self.workouts.append(workout)

    self.workouts.sort(
        key=lambda w: w.date if w.date is not None else pd.Timestamp.min
    )

    return self

    # ======================================================

    def remove(self, index):

        self.workouts.pop(index)

    # ======================================================

    def clear(self):

        self.workouts.clear()

    # ======================================================

    @property
    def dataframe(self):

        rows = []

        for workout in self.workouts:

            rows.append(

            {

            "date": workout.date,

            "sport": workout.sport,

            "duration": workout.duration,

            "terrain": workout.terrain,

            "rpe": workout.rpe,

        }

    )

    return pd.DataFrame(rows)

    # ======================================================

    @property
    def first_workout(self):

        if not self.workouts:

            return None

        return self.workouts[0]

    # ======================================================

    @property
    def last_workout(self):

        if not self.workouts:

            return None

        return self.workouts[-1]

    # ======================================================

    @property
    def total_duration(self):

        total = timedelta()

        for workout in self.workouts:

            total += workout.duration

        return total

    # ======================================================

    @property
    def sports(self):

        return sorted(

    {

        w.sport

        for w in self.workouts

        if w.sport is not None

    }

)

    # ======================================================

    def summary(self):

        print()

        print("=" * 45)

        print("ATHLETE HISTORY")

        print("=" * 45)

        print(f"Athlete : {self.athlete.name}")

        print(f"Workouts: {len(self.workouts)}")

        print(f"Sports  : {', '.join(self.sports)}")

        print(f"Duration: {self.total_duration}")

        if self.first_workout:

            print()

            print(f"First   : {self.first_workout.date}")

            print(f"Last    : {self.last_workout.date}")

        print("=" * 45)

    # ======================================================

    def __len__(self):

        return len(self.workouts)

    # ======================================================

    def __getitem__(self, item):

        return self.workouts[item]

    # ======================================================

    def __iter__(self):

        return iter(self.workouts)

    # ======================================================

    def __repr__(self):

        return (

            f"History("

            f"{len(self.workouts)} workouts)"

        )