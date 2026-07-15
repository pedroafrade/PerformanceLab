"""
PerformanceLab

Performance Management Chart
"""

from dataclasses import dataclass, field

from .ctl import ctl_curve
from .atl import atl_curve
from .tsb import tsb_curve


@dataclass
class PerformanceManagementChart:

    loads: list[float] = field(default_factory=list)

    # ======================================================

    @property
    def ctl(self):

        return ctl_curve(self.loads)

    # ======================================================

    @property
    def atl(self):

        return atl_curve(self.loads)

    # ======================================================

    @property
    def tsb(self):

        return tsb_curve(self.loads)

    # ======================================================

    @property
    def current_ctl(self):

        values = self.ctl

        return values[-1] if values else 0.0

    # ======================================================

    @property
    def current_atl(self):

        values = self.atl

        return values[-1] if values else 0.0

    # ======================================================

    @property
    def current_tsb(self):

        values = self.tsb

        return values[-1] if values else 0.0

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

        return len(self.loads)

    # ======================================================

    def __repr__(self):

        return (

            f"PerformanceManagementChart("

            f"{len(self.loads)} loads)"

        )