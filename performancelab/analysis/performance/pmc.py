"""
PerformanceLab

Performance Management Chart

Combines CTL, ATL and TSB curves calculated from
chronological daily training loads.
"""

from dataclasses import dataclass, field

from .atl import atl_curve
from .ctl import ctl_curve
from .tsb import training_stress_balance


@dataclass
class PerformanceManagementChart:

    daily_loads: list[float] = field(

        default_factory=list,

    )

    ctl_days: int = 42

    atl_days: int = 7

    # ======================================================

    @property
    def ctl(self):

        return ctl_curve(

            self.daily_loads,

            days=self.ctl_days,

        )

    # ======================================================

    @property
    def atl(self):

        return atl_curve(

            self.daily_loads,

            days=self.atl_days,

        )

    # ======================================================

    @property
    def tsb(self):

        return [

            training_stress_balance(

                ctl_value,

                atl_value,

            )

            for ctl_value, atl_value in zip(

                self.ctl,

                self.atl,

            )

        ]

    # ======================================================

    @property
    def current_ctl(self):

        values = self.ctl

        if not values:

            return 0.0

        return values[-1]

    # ======================================================

    @property
    def current_atl(self):

        values = self.atl

        if not values:

            return 0.0

        return values[-1]

    # ======================================================

    @property
    def current_tsb(self):

        values = self.tsb

        if not values:

            return 0.0

        return values[-1]
    # ======================================================

    @property
    def history_days(self) -> int:
        """
        Returns the number of calendar days represented
        in the load series.
        """

        return len(
            self.daily_loads
        )

    # ======================================================

    @property
    def has_data(self) -> bool:
        """
        Returns whether the chart contains load history.
        """

        return self.history_days > 0

    # ======================================================

    @property
    def has_complete_atl_window(self) -> bool:
        """
        Returns whether the acute-load window is complete.
        """

        return (
            self.history_days
            >= self.atl_days
        )

    # ======================================================

    @property
    def has_complete_ctl_window(self) -> bool:
        """
        Returns whether the chronic-load window is complete.
        """

        return (
            self.history_days
            >= self.ctl_days
        )
    
    # ======================================================

    @property
    def fitness(self):

        return self.current_ctl

    # ======================================================

    @property
    def fatigue(self):

        return self.current_atl

    # ======================================================

    @property
    def form(self):

        return self.current_tsb

    # ======================================================

    def __len__(self):

        return len(self.daily_loads)

    # ======================================================

    def __repr__(self):

        return (

            f"PerformanceManagementChart("

            f"{len(self.daily_loads)} days)"

        )