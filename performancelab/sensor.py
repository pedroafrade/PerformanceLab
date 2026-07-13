"""
PerformanceLab v1.0

sensor.py

Classe base para qualquer sensor utilizado numa sessão
de treino.
"""

from dataclasses import dataclass, field

import pandas as pd


@dataclass
class Sensor:

    manufacturer: str
    model: str
    data: pd.DataFrame

    metadata: dict = field(default_factory=dict)

    # =====================================================

    @property
    def start_time(self):

        return self.data["timestamp"].min()

    # =====================================================

    @property
    def end_time(self):

        return self.data["timestamp"].max()

    # =====================================================

    @property
    def duration(self):

        return self.end_time - self.start_time

    # =====================================================

    @property
    def samples(self):

        return len(self.data)

    # =====================================================

    @property
    def columns(self):

        return list(self.data.columns)

    # =====================================================

    @property
    def sampling_rate(self):

        """
        Frequência média de amostragem (Hz).
        """

        if self.samples < 2:
            return 0

        seconds = self.duration.total_seconds()

        if seconds <= 0:
            return 0

        return (self.samples - 1) / seconds

    # =====================================================

    def summary(self):

        print()

        print("=" * 45)
        print("SENSOR")
        print("=" * 45)

        print(f"Fabricante : {self.manufacturer}")
        print(f"Modelo     : {self.model}")

        print(f"Amostras   : {self.samples}")

        print(f"Início     : {self.start_time}")
        print(f"Fim        : {self.end_time}")

        print(f"Duração    : {self.duration}")

        print(f"Amostragem : {self.sampling_rate:.2f} Hz")

        print()

        print("Campos:")

        for column in self.columns:
            print(f"  • {column}")

        print("=" * 45)

    # =====================================================

    def head(self, n=5):

        return self.data.head(n)

    # =====================================================

    def tail(self, n=5):

        return self.data.tail(n)

    # =====================================================

    def __len__(self):

        return self.samples

    # =====================================================

    def __repr__(self):

        return (
            f"Sensor("
            f"{self.manufacturer} {self.model}, "
            f"samples={self.samples})"
        )