"""
PerformanceLab v1.0

comparison.py

Comparação entre dois sensores sincronizados.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .sync import Synchronizer


@dataclass
class Comparison:

    synchronizer: Synchronizer


    # -----------------------------

    @property
    def data(self):

        return self.synchronizer.aligned_data

    # -----------------------------

    @property
    def bias(self):

        return self.data["difference"].mean()

    # -----------------------------

    @property
    def mae(self):

        return np.abs(
            self.data["difference"]
        ).mean()

    # -----------------------------

    @property
    def rmse(self):

        return np.sqrt(
            np.mean(
                self.data["difference"]**2
            )
        )

    # -----------------------------

    @property
    def std(self):

        return self.data["difference"].std()

    # -----------------------------

    @property
    def minimum(self):

        return self.data["difference"].min()

    # -----------------------------

    @property
    def maximum(self):

        return self.data["difference"].max()

    # -----------------------------

    @property
    def samples(self):

        return len(self.data)

    # -----------------------------

    @property
    def metrics(self):

        return {

            "samples": self.samples,

            "shift": self.synchronizer.best_shift,

            "correlation": self.synchronizer.correlation,

            "bias": self.bias,

            "mae": self.mae,

            "rmse": self.rmse,

            "std": self.std,

            "min": self.minimum,

            "max": self.maximum

        }

    # -----------------------------

    def summary(self):

        ref = self.synchronizer.reference
        tgt = self.synchronizer.target

        print()

        print("=" * 45)
        print("SENSOR COMPARISON")
        print("=" * 45)

        print(
            f"Reference : {ref.manufacturer} {ref.model}"
        )

        print(
            f"Target    : {tgt.manufacturer} {tgt.model}"
        )

        print()

        print(
            f"Samples   : {self.samples}"
        )

        print(
           f"Signal lag : {self.synchronizer.best_shift:+d} s"
        )

        print(
            f"Correlation: {self.synchronizer.correlation:.4f}"
        )

        print()

        print(
            f"Bias       : {self.bias:.2f} bpm"
        )

        print(
            f"MAE        : {self.mae:.2f} bpm"
        )

        print(
            f"RMSE       : {self.rmse:.2f} bpm"
        )

        print(
            f"STD        : {self.std:.2f} bpm"
        )

        print()

        print(
            f"Min error  : {self.minimum:.1f} bpm"
        )

        print(
            f"Max error  : {self.maximum:.1f} bpm"
        )

        print("=" * 45)

    # -----------------------------

    def __repr__(self):

        return (
            f"Comparison("
            f"corr={self.synchronizer.correlation:.3f}, "
            f"MAE={self.mae:.2f} bpm)"
        )
            # -----------------------------

    @property
    def plot(self):

        return ComparisonPlotter(self)
        
from .plots import ComparisonPlotter