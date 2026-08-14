"""
PerformanceLab

Historical development summary presenter.
"""

from __future__ import annotations

from .development_models import (
    DevelopmentSummaryCardData,
    DevelopmentTrendMetricData,
    DevelopmentTrendsData,
)


class DevelopmentSummaryPresenter:
    """
    Formats historical trend metrics for the four summary
    cards displayed at the top of Development.
    """

    def __init__(
        self,
        trends: DevelopmentTrendsData,
    ) -> None:

        self.trends = trends

    @staticmethod
    def _trend_label(
        metric: DevelopmentTrendMetricData,
    ) -> str:
        """
        Describes direction without assuming that every
        increase is beneficial.
        """

        if metric.current_value is None:

            return "No current data"

        if metric.previous_value is None:

            return "No prior comparison"

        change = (
            metric.percentage_change
        )

        if change is None:

            return "Change unavailable"

        if change > 0:

            return f"↑ {abs(change):.1f}%"

        if change < 0:

            return f"↓ {abs(change):.1f}%"

        return "→ 0.0%"

    @staticmethod
    def _sample_context(
        metric: DevelopmentTrendMetricData,
        *,
        sample_name: str,
    ) -> str:

        samples = (
            metric.current_samples
        )

        label = (
            sample_name
            if samples == 1
            else f"{sample_name}s"
        )

        return (
            f"{samples} {label}"
            f" · latest {metric.window_days} days"
        )

    @staticmethod
    def _minutes_value(
        metric: DevelopmentTrendMetricData,
    ) -> str:

        if metric.current_value is None:

            return "—"

        return (
            f"{metric.current_value:.1f} "
            "min/day"
        )

    @staticmethod
    def _pace_value(
        metric: DevelopmentTrendMetricData,
    ) -> str:

        if metric.current_value is None:

            return "—"

        total_seconds = round(
            metric.current_value
            * 60
        )

        minutes, seconds = divmod(
            total_seconds,
            60,
        )

        return (
            f"{minutes}:{seconds:02d} "
            "min/km"
        )

    @staticmethod
    def _calories_value(
        metric: DevelopmentTrendMetricData,
    ) -> str:

        if metric.current_value is None:

            return "—"

        return (
            f"{metric.current_value:.0f} "
            "active kcal/day"
        )

    @staticmethod
    def _vo2max_value(
        metric: DevelopmentTrendMetricData,
    ) -> str:

        if metric.current_value is None:

            return "—"

        return (
            f"{metric.current_value:.1f} "
            "ml/kg/min"
        )

    def build(
        self,
    ) -> tuple[
        DevelopmentSummaryCardData,
        ...,
    ]:

        minutes = (
            self.trends
            .exercise_minutes_per_day
        )
        pace = (
            self.trends
            .running_pace_per_kilometre
        )
        calories = (
            self.trends
            .active_calories_per_day
        )
        vo2max = self.trends.vo2max

        return (
            DevelopmentSummaryCardData(
                key="exercise-time",
                icon="◷",
                label="Exercise time/day",
                value=(
                    self._minutes_value(
                        minutes
                    )
                ),
                trend=(
                    self._trend_label(
                        minutes
                    )
                ),
                context=(
                    self._sample_context(
                        minutes,
                        sample_name="activity",
                    )
                ),
            ),
            DevelopmentSummaryCardData(
                key="running-pace",
                icon="≈",
                label="Running pace",
                value=(
                    self._pace_value(
                        pace
                    )
                ),
                trend=(
                    self._trend_label(
                        pace
                    )
                ),
                context=(
                    self._sample_context(
                        pace,
                        sample_name="run",
                    )
                ),
            ),
            DevelopmentSummaryCardData(
                key="active-calories",
                icon="◉",
                label="Active calories/day",
                value=(
                    self._calories_value(
                        calories
                    )
                ),
                trend=(
                    self._trend_label(
                        calories
                    )
                ),
                context=(
                    self._sample_context(
                        calories,
                        sample_name="activity",
                    )
                ),
            ),
            DevelopmentSummaryCardData(
                key="vo2max",
                icon="O₂",
                label="VO₂max",
                value=(
                    self._vo2max_value(
                        vo2max
                    )
                ),
                trend=(
                    self._trend_label(
                        vo2max
                    )
                ),
                context=(
                    self._sample_context(
                        vo2max,
                        sample_name="observation",
                    )
                ),
            ),
        )