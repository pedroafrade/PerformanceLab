"""
PerformanceLab v1.0

plots.py

Visualização gráfica das comparações entre sensores.
"""

import matplotlib.pyplot as plt
import numpy as np


class ComparisonPlotter:

    def __init__(self, comparison):

        self.comparison = comparison

    # =====================================================

    def timeseries(self):

        df = self.comparison.data

        plt.figure(figsize=(15, 6))

        plt.plot(
            df["timestamp"],
            df["hr_reference"],
            label="Reference",
            linewidth=2
        )

        plt.plot(
            df["timestamp"],
            df["hr_target"],
            label="Target",
            linewidth=2
        )

        plt.xlabel("Time")

        plt.ylabel("Heart Rate (bpm)")

        plt.title("Heart Rate Time Series")

        plt.grid(True)

        plt.legend()

        plt.tight_layout()

        plt.show()

    # =====================================================

    def scatter(self):

        df = self.comparison.data

        plt.figure(figsize=(6, 6))

        plt.scatter(
            df["hr_reference"],
            df["hr_target"],
            s=8,
            alpha=0.6
        )

        minimum = min(
            df["hr_reference"].min(),
            df["hr_target"].min()
        )

        maximum = max(
            df["hr_reference"].max(),
            df["hr_target"].max()
        )

        plt.plot(
            [minimum, maximum],
            [minimum, maximum],
            "--"
        )

        plt.xlabel("Reference (bpm)")

        plt.ylabel("Target (bpm)")

        plt.title("Reference vs Target")

        plt.grid(True)

        plt.tight_layout()

        plt.show()

    # =====================================================

    def bland_altman(self):

        df = self.comparison.data

        mean = (
            df["hr_reference"] +
            df["hr_target"]
        ) / 2

        diff = df["difference"]

        bias = diff.mean()

        std = diff.std()

        upper = bias + 1.96 * std

        lower = bias - 1.96 * std

        plt.figure(figsize=(8, 6))

        plt.scatter(
            mean,
            diff,
            s=8,
            alpha=0.5
        )

        plt.axhline(
            bias,
            linestyle="-",
            label=f"Bias = {bias:.2f}"
        )

        plt.axhline(
            upper,
            linestyle="--",
            label="+1.96 SD"
        )

        plt.axhline(
            lower,
            linestyle="--",
            label="-1.96 SD"
        )

        plt.xlabel("Mean HR (bpm)")

        plt.ylabel("Difference (bpm)")

        plt.title("Bland–Altman Plot")

        plt.grid(True)

        plt.legend()

        plt.tight_layout()

        plt.show()

    # =====================================================

    def error_histogram(self):

        df = self.comparison.data

        plt.figure(figsize=(8, 5))

        plt.hist(
            df["difference"],
            bins=30
        )

        plt.xlabel("Error (bpm)")

        plt.ylabel("Frequency")

        plt.title("Error Distribution")

        plt.grid(True)

        plt.tight_layout()

        plt.show()
