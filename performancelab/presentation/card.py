"""
PerformanceLab

Sensor Card Presentation

Prepares workout sensor data for presentation cards.
"""

from dataclasses import dataclass, field

from performancelab import Workout

from .chart import (
    sensor_series,
    sensor_summary,
)


# ======================================================
# Sensor Card
# ======================================================

@dataclass(frozen=True)
class SensorCard:

    sensor_name: str

    title: str

    unit: str = ""

    samples: int = 0

    average: float | None = None

    minimum: float | None = None

    maximum: float | None = None

    series: list[dict] = field(
        default_factory=list
    )

    # ======================================================

    @property
    def available(self) -> bool:

        return self.samples > 0

    # ======================================================

    @property
    def chart_data(self) -> list[dict]:

        """
        Returns presentation-ready chart rows.

        Each row contains:

            elapsed_seconds
            elapsed_minutes
            value
            time
        """

        return [

            {
                "elapsed_seconds": (
                    sample["elapsed_seconds"]
                ),

                "elapsed_minutes": (
                    sample["elapsed_seconds"]
                    / 60
                ),

                "value": sample["value"],

                "time": sample["time"],
            }

            for sample in self.series

        ]

    # ======================================================

    def format_value(
        self,
        value: float | None,
        decimals: int = 0,
    ) -> str:

        if value is None:

            return "—"

        formatted = f"{value:.{decimals}f}"

        if not self.unit:

            return formatted

        return f"{formatted} {self.unit}"

    # ======================================================

    @property
    def average_label(self) -> str:

        return self.format_value(
            self.average
        )

    # ======================================================

    @property
    def minimum_label(self) -> str:

        return self.format_value(
            self.minimum
        )

    # ======================================================

    @property
    def maximum_label(self) -> str:

        return self.format_value(
            self.maximum
        )

    # ======================================================

    def __repr__(self):

        return (

            f"SensorCard("

            f"sensor='{self.sensor_name}', "

            f"samples={self.samples})"

        )


# ======================================================
# Sensor Card Builder
# ======================================================

def sensor_card(
    workout: Workout,
    sensor_name: str,
    title: str,
    unit: str = "",
) -> SensorCard:

    series = sensor_series(
        workout,
        sensor_name,
    )

    summary = sensor_summary(
        workout,
        sensor_name,
    )

    return SensorCard(

        sensor_name=sensor_name,

        title=title,

        unit=unit,

        samples=summary["samples"],

        average=summary["average"],

        minimum=summary["minimum"],

        maximum=summary["maximum"],

        series=series,

    )


# ======================================================
# Standard Sensor Cards
# ======================================================

def heart_rate_card(
    workout: Workout,
) -> SensorCard:

    return sensor_card(

        workout=workout,

        sensor_name="heart_rate",

        title="Heart rate",

        unit="bpm",

    )


# ======================================================

def power_card(
    workout: Workout,
) -> SensorCard:

    return sensor_card(

        workout=workout,

        sensor_name="power",

        title="Power",

        unit="W",

    )


# ======================================================

def cadence_card(
    workout: Workout,
) -> SensorCard:

    return sensor_card(

        workout=workout,

        sensor_name="cadence",

        title="Cadence",

        unit="rpm",

    )