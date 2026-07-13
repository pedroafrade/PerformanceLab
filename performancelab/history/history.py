"""
PerformanceLab

History

Collection of workouts belonging to an athlete.
"""

from dataclasses import dataclass, field
from datetime import datetime

import pandas as pd

from ..workout import Workout


@dataclass
class History:

    athlete: object | None = None

    workouts: list[Workout] = field(default_factory=list)

    # ======================================================

    def add(self, workout: Workout):

        self.workouts.append(workout)

        self.workouts.sort(
            key=lambda w: w.date or datetime.min
        )

        return workout

    # ======================================================

    def remove(self, workout: Workout):

        self.workouts.remove(workout)

    # ======================================================

    def clear(self):

        self.workouts.clear()

    # ======================================================

    def first(self, n: int = 1):

        if n == 1:
            return self.workouts[0] if self.workouts else None

        return self.workouts[:n]

    # ======================================================

    def last(self, n: int = 1):

        if n == 1:
            return self.workouts[-1] if self.workouts else None

        return self.workouts[-n:]

    # ======================================================

    def sport(self, name: str):

        return [

            workout

            for workout in self.workouts

            if workout.sport == name

        ]

    # ======================================================

    def between(self, start, end):

        return [

            workout

            for workout in self.workouts

            if workout.date is not None
            and start <= workout.date <= end

        ]

    # ======================================================

    @property
    def dataframe(self):

        rows = []

        for workout in self.workouts:

            rows.append({

                "date": workout.info.date,

                "sport": workout.info.sport,

                "terrain": workout.environment.terrain,

                "temperature": workout.environment.temperature,

                "rpe": workout.feedback.rpe,

            })

        return pd.DataFrame(rows)

    # ======================================================

    @property
    def sports(self):

        return sorted({

            workout.sport

            for workout in self.workouts

            if workout.sport is not None

        })

    # ======================================================

    def summary(self):

        print()

        print("=" * 50)

        print("History")

        print("=" * 50)

        if self.athlete is not None:

            print(f"Athlete : {self.athlete.name}")

        print(f"Workouts: {len(self)}")

        print(f"Sports  : {', '.join(self.sports)}")

        print("=" * 50)

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

        return f"History({len(self)} workouts)"