"""
PerformanceLab

Workout object.

Represents a complete training workout, combining
sensor data with contextual information.
"""


class Workout:

    # =====================================================

    def __init__(
        self,
        athlete,
        session,
        objective=None,
        terrain=None,
        weather=None,
        temperature=None,
        rpe=None,
        notes=None,
        equipment=None,
        tags=None,
        metadata=None
    ):

        self.athlete = athlete

        self.session = session

        self.objective = objective

        self.terrain = terrain

        self.weather = weather

        self.temperature = temperature

        self.rpe = rpe

        self.notes = notes

        self.equipment = equipment

        self.tags = tags or []

        self.metadata = metadata or {}

    # =====================================================

    @property
    def sport(self):

        return self.session.sport

    # =====================================================

    @property
    def date(self):

        return getattr(self.session, "date", None)

    # =====================================================

    @property
    def distance(self):

        return getattr(self.session, "distance", None)

    # =====================================================

    @property
    def duration(self):

        return getattr(self.session, "duration", None)

    # =====================================================

    @property
    def avg_hr(self):

        return getattr(self.session, "avg_hr", None)

    # =====================================================

    @property
    def max_hr(self):

        return getattr(self.session, "max_hr", None)

    # =====================================================

    def summary(self):

        print()

        print("=" * 50)

        print("Workout Summary")

        print("=" * 50)

        print(f"Athlete     : {self.athlete.name}")
        print(f"Sport       : {self.sport}")
        print(f"Date        : {self.date}")
        print(f"Distance    : {self.distance}")
        print(f"Duration    : {self.duration}")
        print(f"Average HR  : {self.avg_hr}")
        print(f"Maximum HR  : {self.max_hr}")
        print(f"Objective   : {self.objective}")
        print(f"Terrain     : {self.terrain}")
        print(f"Weather     : {self.weather}")
        print(f"Temperature : {self.temperature}")
        print(f"RPE         : {self.rpe}")

        if self.notes:
            print(f"Notes       : {self.notes}")

        print()

    # =====================================================

    def __repr__(self):

        athlete = getattr(self.athlete, "name", "Unknown")

        sport = self.sport or "Unknown"

        return f"Workout({athlete}, {sport})"