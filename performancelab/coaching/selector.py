"""
PerformanceLab

Strategy Selector

Maps a coaching analysis to the appropriate coaching strategy.
"""

from performancelab.coaching.analyzer import CoachAnalysis
from performancelab.coaching.strategy import CoachStrategy

from performancelab.coaching.strategies import (
    BaseStrategy,
    BuildStrategy,
    MaintenanceStrategy,
    PeakStrategy,
    RaceStrategy,
    RegenerationStrategy,
    TaperStrategy,
)


class StrategySelector:
    """
    Selects the appropriate coaching strategy.

    The selector converts a CoachAnalysis into a concrete
    CoachStrategy implementation.
    """

    # ======================================================

    def select(
        self,
        analysis: CoachAnalysis,
    ) -> CoachStrategy:

        if analysis.strategy == "RegenerationStrategy":

            return RegenerationStrategy()

        match analysis.phase:

            case "Maintenance":
                return MaintenanceStrategy()

            case "Base":
                return BaseStrategy()

            case "Build":
                return BuildStrategy()

            case "Peak":
                return PeakStrategy()

            case "Taper":
                return TaperStrategy()

            case "Race":
                return RaceStrategy()

            case "Regeneration":
                return RegenerationStrategy()

        raise ValueError(
            f"Unsupported coaching phase: {analysis.phase}"
        )