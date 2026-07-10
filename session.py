"""
PerformanceLab v1.0

session.py

Representação de uma sessão de treino.
"""

from dataclasses import dataclass, field

from PerformanceLab.athlete import Athlete
from PerformanceLab.sensor import SensorData


@dataclass
class TrainingSession:

    athlete: Athlete

    sport: str

    sensors: dict = field(default_factory=dict)

    metadata: dict = field(default_factory=dict)

    # =====================================================

    def add_sensor(self, sensor: SensorData):

        self.sensors[sensor.model] = sensor

    # =====================================================

    @property
    def sensor_names(self):

        return list(self.sensors.keys())

    # =====================================================

    @property
    def number_of_sensors(self):

        return len(self.sensors)

    # =====================================================

    @property
    def start_time(self):

        if not self.sensors:
            return None

        return min(
            sensor.start_time
            for sensor in self.sensors.values()
        )

    # =====================================================

    @property
    def end_time(self):

        if not self.sensors:
            return None

        return max(
            sensor.end_time
            for sensor in self.sensors.values()
        )

    # =====================================================

    @property
    def duration(self):

        if self.start_time is None:
            return None

        return self.end_time - self.start_time

    # =====================================================

    @property
    def reference_sensor(self):

        if self.number_of_sensors == 0:
            return None

        return list(self.sensors.values())[0]

    # =====================================================

    @property
    def target_sensor(self):

        if self.number_of_sensors < 2:
            return None

        return list(self.sensors.values())[1]

    # =====================================================

    def summary(self):

        print()

        print("=" * 45)
        print("TRAINING SESSION")
        print("=" * 45)

        print(f"Atleta      : {self.athlete.name}")

        print(f"Modalidade  : {self.sport}")

        print()

        print("Sensores:")

        for sensor in self.sensors.values():

            print(
                f"  • {sensor.manufacturer} {sensor.model}"
            )

        print()

        print(f"Início      : {self.start_time}")

        print(f"Fim         : {self.end_time}")

        print(f"Duração     : {self.duration}")

        print(f"Nº sensores : {self.number_of_sensors}")

        print("=" * 45)

    # =====================================================

    def __len__(self):

        return self.number_of_sensors

    # =====================================================

    def __repr__(self):

        return (
            f"TrainingSession("
            f"{self.athlete.name}, "
            f"{self.sport}, "
            f"{self.number_of_sensors} sensors)"
        )