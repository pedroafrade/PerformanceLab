"""
PerformanceLab

athlete.py

Representação de um atleta.
"""

from dataclasses import dataclass, field

from PerformanceLab.history.history import History


@dataclass
class Athlete:

    # =====================================================
    # Dados pessoais
    # =====================================================

    name: str

    birth_year: int

    sex: str

    weight: float

    height: float

    resting_hr: int

    max_hr: int

    threshold_hr: int

    sports: list = field(default_factory=list)

    metadata: dict = field(default_factory=dict)

    # =====================================================

    def __post_init__(self):

        # Cada atleta possui automaticamente um histórico

        self.history = History(self)

    # =====================================================

    @property
    def age(self):

        from datetime import datetime

        return datetime.now().year - self.birth_year

    # =====================================================

    @property
    def bmi(self):

        return self.weight / (self.height ** 2)

    # =====================================================

    @property
    def hr_reserve(self):

        return self.max_hr - self.resting_hr

    # =====================================================

    @property
    def primary_sport(self):

        if len(self.sports):

            return self.sports[0]

        return None

    # =====================================================

    @property
    def n_sessions(self):

        return len(self.history)

    # =====================================================

    def summary(self):

        print()

        print("=" * 45)

        print("ATHLETE")

        print("=" * 45)

        print(f"Nome            : {self.name}")

        print(f"Idade           : {self.age}")

        print(f"Sexo            : {self.sex}")

        print(f"Peso            : {self.weight:.1f} kg")

        print(f"Altura          : {self.height:.2f} m")

        print(f"BMI             : {self.bmi:.1f}")

        print()

        print(f"FC repouso      : {self.resting_hr} bpm")

        print(f"FC máxima       : {self.max_hr} bpm")

        print(f"FC limiar       : {self.threshold_hr} bpm")

        print(f"Reserva FC      : {self.hr_reserve} bpm")

        print()

        print(
            "Modalidades     : "
            + ", ".join(self.sports)
        )

        print(
            f"Sessões         : {self.n_sessions}"
        )

        print("=" * 45)

    # =====================================================

    def __repr__(self):

        return (

            f"Athlete("

            f"{self.name}, "

            f"{self.n_sessions} sessions)"

        )