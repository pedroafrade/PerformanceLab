from dataclasses import dataclass
from datetime import date

from performancelab.athlete import Athlete


@dataclass(frozen=True)
class CoachContext:

    athlete: Athlete

    today: date

    ctl: float

    atl: float

    tsb: float

    next_event: object | None

    days_until_event: int | None

    sports: tuple[str, ...]

    average_rpe: float | None

    training_plan: object

    @classmethod
    def from_athlete(
        cls,
        athlete: Athlete,
        today: date | None = None,
    ):

        analytics = athlete.analytics

        return cls(

            athlete=athlete,

            today=today or date.today(),

            ctl=analytics.ctl,

            atl=analytics.atl,

            tsb=analytics.tsb,

            next_event=analytics.next_event,

            days_until_event=analytics.days_until_next_event,

            sports=tuple(analytics.sports),

            average_rpe=analytics.average_rpe,

            training_plan=analytics.training_plan,
        )