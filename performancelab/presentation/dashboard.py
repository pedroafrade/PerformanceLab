"""
PerformanceLab

Dashboard Data

Presentation-ready data for user interfaces.
"""


class DashboardData:

    # ======================================================

    def __init__(self, athlete):

        self.athlete = athlete

    # ======================================================
    # Shortcuts
    # ======================================================

    @property
    def analytics(self):

        return self.athlete.analytics

    # ======================================================
    # Athlete
    # ======================================================

    @property
    def athlete_data(self):

        return {

            "name": self.athlete.name,

            "sports": self.analytics.sports,

        }

    # ======================================================
    # Summary
    # ======================================================

    @property
    def summary(self):

        return {

            "workouts": self.analytics.number_of_workouts,

            "training_days": self.analytics.training_days,

            "total_duration": self.analytics.total_duration,

            "average_rpe": self.analytics.average_rpe,

            "ctl": self.analytics.ctl,

            "atl": self.analytics.atl,

            "tsb": self.analytics.tsb,

        }

    # ======================================================
    # Performance
    # ======================================================

    @property
    def performance(self):

        daily_loads = self.analytics.daily_loads

        pmc = self.analytics.pmc

        return {

            "dates": daily_loads.dates,

            "load": daily_loads.loads,

            "ctl": pmc.ctl,

            "atl": pmc.atl,

            "tsb": pmc.tsb,

        }

    # ======================================================
    # Planning
    # ======================================================

    @property
    def planning(self):

        return {

            "next_goal": self.analytics.next_goal,

            "days_until_next_goal": (
                self.analytics.days_until_next_goal
            ),

            "next_event": self.analytics.next_event,

            "days_until_next_event": (
                self.analytics.days_until_next_event
            ),

        }

    # ======================================================
    # Complete Dashboard
    # ======================================================

    def build(self):

        return {

            "athlete": self.athlete_data,

            "summary": self.summary,

            "performance": self.performance,

            "planning": self.planning,

        }

    # ======================================================

    def __repr__(self):

        return (

            f"DashboardData("

            f"athlete='{self.athlete.name}')"

        )