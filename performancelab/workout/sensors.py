"""
PerformanceLab

SensorCollection

Container for all sensors recorded during a workout.
"""

from dataclasses import dataclass, field


@dataclass
class SensorCollection:

    sensors: dict[str, object] = field(default_factory=dict)

    # ======================================================

    def add(self, name: str, sensor: object):

        self.sensors[name] = sensor

    # ======================================================

    def remove(self, name: str):

        self.sensors.pop(name, None)

    # ======================================================

    def clear(self):

        self.sensors.clear()

    # ======================================================

    def get(self, name: str):

        return self.sensors.get(name)

    # ======================================================

    @property
    def names(self):

        return sorted(self.sensors.keys())

    # ======================================================

    def __contains__(self, name):

        return name in self.sensors

    # ======================================================

    def __len__(self):

        return len(self.sensors)

    # ======================================================

    def __iter__(self):

        return iter(self.sensors.items())

    # ======================================================

    def __repr__(self):

        return (
            f"SensorCollection("
            f"{len(self.sensors)} sensors)"
        )