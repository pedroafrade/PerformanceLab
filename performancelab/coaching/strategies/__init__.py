"""
PerformanceLab

Coaching Strategies

Public interface for the available coaching strategies.
"""

from .base import BaseStrategy
from .build import BuildStrategy
from .regeneration import RegenerationStrategy
from .taper import TaperStrategy

from performancelab.coaching.strategies.base import BaseStrategy
from performancelab.coaching.strategies.build import BuildStrategy
from performancelab.coaching.strategies.maintenance import MaintenanceStrategy
from performancelab.coaching.strategies.peak import PeakStrategy
from performancelab.coaching.strategies.race import RaceStrategy
from performancelab.coaching.strategies.regeneration import RegenerationStrategy
from performancelab.coaching.strategies.taper import TaperStrategy

__all__ = [
    "BaseStrategy",
    "BuildStrategy",
    "MaintenanceStrategy",
    "PeakStrategy",
    "RaceStrategy",
    "RegenerationStrategy",
    "TaperStrategy",
]