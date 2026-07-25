from dataclasses import dataclass

from .context import CoachContext


@dataclass(frozen=True)
class CoachAnalysis:

    phase: str

    strategy: str

    warnings: tuple[str, ...]

    summary: str


class CoachAnalyzer:

    def __init__(
        self,
        context: CoachContext,
    ):

        self.context = context

    # ======================================================

    def analyze(self) -> CoachAnalysis:

        warnings = []

        phase = self._phase()

        strategy = self._strategy(phase)

        if self.context.tsb < -20:

            warnings.append(
                "High accumulated fatigue."
            )

        summary = self._summary(phase)

        return CoachAnalysis(

            phase=phase,

            strategy=strategy,

            warnings=tuple(warnings),

            summary=summary,
        )

    # ======================================================

    def _phase(self) -> str:
        """
        Determines the athlete's current coaching phase.

        A race completed during the previous seven days takes
        priority over the next event cycle.
        """

        days_since_event = (
            self.context.days_since_event
        )

        if (
            days_since_event is not None
            and 0 <= days_since_event <= 7
        ):
            return "Regeneration"

        days = self.context.days_until_event

        if days is None:
            return "Maintenance"

        if days < 0:
            return "Regeneration"

        if days <= 7:
            return "Race"

        if days <= 14:
            return "Taper"

        if days <= 42:
            return "Peak"

        if days <= 84:
            return "Build"

        return "Base"
    # ======================================================

    def _strategy(
        self,
        phase: str,
    ):

        if self.context.tsb < -20:

            return "RegenerationStrategy"

        return f"{phase}Strategy"

    # ======================================================

    def _summary(
        self,
        phase: str,
    ):

        event = self.context.next_event

        if event is None:

            return (
                "No upcoming event. "
                "Focus on general fitness."
            )

        return (
            f"{phase} phase for "
            f"{event.event.name}."
        )