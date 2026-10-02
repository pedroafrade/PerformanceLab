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

        sensor = self.sensors.get(name)

        # Kept as a local import so this domain container remains independent
        # of any particular repository implementation.
        from performancelab.storage.compressed_sensor import (
            CompressedSensor,
        )

        if isinstance(sensor, CompressedSensor):
            return sensor.read()

        return sensor

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

        return iter(
            (
                name,
                self.get(name),
            )
            for name in self.sensors
        )

    # ======================================================

    def __repr__(self):

        return (
            f"SensorCollection("
            f"{len(self.sensors)} sensors)"
        )
