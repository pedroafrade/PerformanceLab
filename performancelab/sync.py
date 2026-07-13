"""
PerformanceLab v1.1

sync.py

Sincronização temporal entre dois sensores.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .sensor import Sensor


# ==========================================================
# Synchronizer
# ==========================================================

@dataclass
class Synchronizer:

    reference: Sensor
    target: Sensor

    max_shift: int = 30

    # =====================================================

    @property
    def reference_hr(self):

        return self.reference.data[
            ["timestamp", "hr"]
        ].copy()

    # =====================================================

    @property
    def target_hr(self):

        return self.target.data[
            ["timestamp", "hr"]
        ].copy()

    # =====================================================

    @property
    def lags(self):

        return range(
            -self.max_shift,
            self.max_shift + 1
        )

    # =====================================================

    @property
    def results(self):

        """
        Tabela com todas as correlações
        testadas.
        """

        rows = []

        ref = self.reference_hr.copy()

        tgt = self.target_hr.copy()

        for lag in self.lags:

            shifted = tgt.copy()

            shifted["timestamp"] = (

                shifted["timestamp"]

                + pd.Timedelta(seconds=lag)

            )

            merged = pd.merge(

                ref,

                shifted,

                on="timestamp",

                suffixes=(

                    "_reference",

                    "_target"

                )

            )

            merged = merged.dropna()

            if len(merged) < 10:

                continue

            corr = merged[
                "hr_reference"
            ].corr(

                merged[
                    "hr_target"
                ]
            )

            rows.append({

                "lag": lag,

                "corr": corr,

                "samples": len(merged)

            })

        df = pd.DataFrame(rows)

        df.sort_values(

            "corr",

            ascending=False,

            inplace=True

        )

        df.reset_index(

            drop=True,

            inplace=True

        )

        return df

    # =====================================================

    @property
    def best_shift(self):

        return int(

            self.results.iloc[0]["lag"]

        )

    # =====================================================

    @property
    def correlation(self):

        return float(

            self.results.iloc[0]["corr"]

        )

    # =====================================================

    @property
    def samples(self):

        return int(

            self.results.iloc[0]["samples"]

        )    
        
    # =====================================================

    @property
    def aligned_data(self):

        """
        Dados alinhados utilizando o melhor shift.
        """

        ref = self.reference_hr.copy()

        tgt = self.target_hr.copy()

        tgt["timestamp"] = (
            tgt["timestamp"]
            + pd.Timedelta(seconds=self.best_shift)
        )

        merged = pd.merge(

            ref,

            tgt,

            on="timestamp",

            suffixes=(
                "_reference",
                "_target"
            )

        )

        merged = merged.dropna().copy()

        merged["difference"] = (

            merged["hr_reference"]

            - merged["hr_target"]

        )

        return merged

    # =====================================================

    def compare(self):

        """
        Cria um objeto Comparison
        utilizando este sincronizador.
        """

        from .comparison import Comparison

        return Comparison(self)

    # =====================================================

    def summary(self):

        print()

        print("=" * 45)
        print("SYNCHRONIZER")
        print("=" * 45)

        print(
            f"Reference : {self.reference.manufacturer} {self.reference.model}"
        )

        print(
            f"Target    : {self.target.manufacturer} {self.target.model}"
        )

        print()

        print(
            f"Best shift : {self.best_shift:+d} s"
        )

        print(
            f"Correlation: {self.correlation:.4f}"
        )

        print(
            f"Samples    : {self.samples}"
        )

        print("=" * 45)

    # =====================================================

    def __len__(self):

        return self.samples

    # =====================================================

    def __repr__(self):

        return (

            f"Synchronizer("

            f"shift={self.best_shift:+d}s, "

            f"corr={self.correlation:.4f}, "

            f"samples={self.samples}"

            f")"

        )