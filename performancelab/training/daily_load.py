"""
PerformanceLab

Daily Training Load

Builds chronological daily training-load series from a History.
"""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

from performancelab.history import History

from .load import workout_load


# ======================================================
# Daily Load Entry
# ======================================================

@dataclass(frozen=True)
class DailyLoad:

    date: date

    load: float = 0.0


# ======================================================
# Daily Load Series
# ======================================================

@dataclass
class DailyLoadSeries:

    entries: list[DailyLoad] = field(default_factory=list)

    # ======================================================

    @property
    def dates(self):

        return [

            entry.date

            for entry in self.entries

        ]

    # ======================================================

    @property
    def loads(self):

        return [

            entry.load

            for entry in self.entries

        ]

    # ======================================================

    @property
    def total_load(self):

        return sum(self.loads)

    # ======================================================

    def __len__(self):

        return len(self.entries)

    # ======================================================

    def __iter__(self):

        return iter(self.entries)

    # ======================================================

    def __getitem__(self, index):

        return self.entries[index]

    # ======================================================

    def __repr__(self):

        return (

            f"DailyLoadSeries("

            f"{len(self.entries)} days)"

        )


# ======================================================
# Daily Load Builder
# ======================================================

class DailyLoadBuilder:

    # ======================================================

    def __init__(self, history: History):

        self.history = history

    # ======================================================

    @staticmethod
    def _calendar_date(value):

        if isinstance(value, datetime):

            return value.date()

        return value

    # ======================================================

    def build(
        self,
        start_date: date | datetime | None = None,
        end_date: date | datetime | None = None,
    ) -> DailyLoadSeries:

        daily_totals = {}

        for workout in self.history:

            if workout.date is None:

                continue

            workout_date = self._calendar_date(

                workout.date

            )

            value = workout_load(workout)

            if value is None:

                continue

            daily_totals[workout_date] = (

                daily_totals.get(

                    workout_date,

                    0.0,

                )

                + value

            )

        start = self._calendar_date(start_date)
        end = self._calendar_date(end_date)

        if start is None:

            if not daily_totals:

                return DailyLoadSeries()

            start = min(daily_totals)

        if end is None:

            if not daily_totals:

                return DailyLoadSeries()

            end = max(daily_totals)

        if start > end:

            raise ValueError(

                "start_date cannot be after end_date"

            )

        entries = []

        current = start

        while current <= end:

            entries.append(

                DailyLoad(

                    date=current,

                    load=daily_totals.get(

                        current,

                        0.0,

                    ),

                )

            )

            current += timedelta(days=1)

        return DailyLoadSeries(entries)

    # ======================================================

    def __repr__(self):

        return (

            f"DailyLoadBuilder("

            f"{len(self.history)} workouts)"

        )