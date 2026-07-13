"""
PerformanceLab

Environment

Environmental conditions of a workout.
"""

from dataclasses import dataclass


@dataclass
class Environment:

    temperature: float | None = None

    humidity: float | None = None

    wind_speed: float | None = None

    elevation_gain: float | None = None

    terrain: str = ""

    weather: str = ""

    def __repr__(self):

        return (
            f"Environment("
            f"temperature={self.temperature}, "
            f"terrain='{self.terrain}')"
        )