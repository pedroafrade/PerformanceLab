"""
PerformanceLab

Classe principal da biblioteca.
"""

from PerformanceLab.readers import (
    read_apple_gpx,
    read_polar_csv
)

from PerformanceLab.session import TrainingSession
from PerformanceLab.sync import Synchronizer


class PerformanceLab:

    # ==========================================================
    # Constructor
    # ==========================================================

    def __init__(self):

        self.athlete = None

        self.session = None

        self.sync = None

        self.comparison = None

    # ==========================================================
    # Load data
    # ==========================================================

    def load(

        self,

        athlete,

        apple=None,

        polar=None,

        sport=None

    ):

        self.athlete = athlete

        if sport is None:

            if athlete.sports:

                sport = athlete.sports[0]

            else:

                sport = "Unknown"

        self.session = TrainingSession(

            athlete=athlete,

            sport=sport

        )

        # ---------------- Apple ----------------

        if apple is not None:

            apple_sensor = read_apple_gpx(apple)

            self.session.add_sensor(apple_sensor)

        # ---------------- Polar ----------------

        if polar is not None:

            polar_sensor = read_polar_csv(polar)

            self.session.add_sensor(polar_sensor)

        return self

    # ==========================================================
    # Synchronize
    # ==========================================================

    def synchronize(self):

        if self.session is None:

            raise RuntimeError(
                "No training session loaded."
            )

        if len(self.session.sensors) < 2:

            raise RuntimeError(
                "At least two sensors are required."
            )

        self.sync = Synchronizer(

            reference=self.session.reference_sensor,

            target=self.session.target_sensor

        )

        return self.sync

    # ==========================================================
    # Compare
    # ==========================================================

    def compare(self):

        if self.sync is None:

            self.synchronize()

        self.comparison = self.sync.compare()

        return self.comparison

    # ==========================================================
    # Summary
    # ==========================================================

    def summary(self):

        print()

        print("=" * 50)

        print("PERFORMANCELAB")

        print("=" * 50)

        if self.athlete is not None:

            print(f"Athlete : {self.athlete.name}")

        if self.session is not None:

            print(f"Sport   : {self.session.sport}")

            print(f"Sensors : {len(self.session)}")

        print("=" * 50)

        if self.session is not None:

            self.session.summary()

        if self.sync is not None:

            self.sync.summary()

        if self.comparison is not None:

            self.comparison.summary()

    # ==========================================================
    # Properties
    # ==========================================================

    @property
    def apple(self):

        if self.session is None:

            return None

        return self.session.sensors.get("Apple Watch")

    @property
    def polar(self):

        if self.session is None:

            return None

        return self.session.sensors.get("Verity Sense")

    # ==========================================================
    # Representation
    # ==========================================================

    def __repr__(self):

        if self.session is None:

            return "PerformanceLab(empty)"

        return (

            f"PerformanceLab("
            f"athlete='{self.athlete.name}', "
            f"sensors={len(self.session)})"

        )