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

        training_state = getattr(
            self.context,
            "training_state",
            None,
        )

        if training_state is not None:

            needs_recovery = (
                training_state.needs_recovery
            )

        else:

            needs_recovery = (
                getattr(
                    self.context,
                    "tsb",
                    0.0,
                )
                < -20
            )

        if needs_recovery:

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
        priority over the next event cycle. Once that recovery
        window ends, the next upcoming event determines the
        primary event determines the normal competitive phase.
        Without an upcoming event, the athlete enters maintenance.
        """

        if self.context.is_post_race:
            return "Regeneration"

        days = getattr(
            self.context,
            "days_until_primary_event",
            None,
        )

        if days is None:

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

        if self.context.is_fatigue_regeneration:

            return "RegenerationStrategy"

        return f"{phase}Strategy"

    # ======================================================

    def _summary(
        self,
        phase: str,
    ):

        event = (
            getattr(
                self.context,
                "primary_event",
                None,
            )
            or self.context.next_event
        )

        if event is None:

            return (
                "No upcoming event. "
                "Focus on general fitness."
            )

        return (
            f"{phase} phase for "
            f"{event.event.name}."
        )