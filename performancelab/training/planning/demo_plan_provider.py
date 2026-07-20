"""
PerformanceLab

Demo Plan Provider

Provides a small set of planned workouts used to validate
the planning pipeline and dashboard presentation.
"""

from datetime import date, datetime, time, timedelta

from .weekly_plan import PlannedWorkout


class DemoPlanProvider:
    """Provides demo planned workouts."""

    def workouts(self):

        today = date.today()

        monday = today - timedelta(days=today.weekday())

        return [
            PlannedWorkout(
                scheduled_at=datetime.combine(
                    monday,
                    time(hour=18),
                ),
                sport="Running",
                title="Easy Run",
                duration=timedelta(minutes=45),
                description="Easy aerobic run",
            ),
            PlannedWorkout(
                scheduled_at=datetime.combine(
                    monday + timedelta(days=2),
                    time(hour=18),
                ),
                sport="Running",
                title="Intervals",
                duration=timedelta(minutes=60),
                description="6 × 800 m",
            ),
            PlannedWorkout(
                scheduled_at=datetime.combine(
                    monday + timedelta(days=5),
                    time(hour=8),
                ),
                sport="Running",
                title="Long Run",
                duration=timedelta(minutes=90),
                description="Long endurance run",
            ),
        ]