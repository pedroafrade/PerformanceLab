from datetime import date

from performancelab.athlete import Athlete

from .context import CoachContext
from .analyzer import CoachAnalyzer
from .recommendation import CoachRecommendation


class Coach:

    # ======================================================

    def recommend(
        self,
        athlete: Athlete,
        today: date | None = None,
    ) -> CoachRecommendation:

        context = CoachContext.from_athlete(

            athlete,

            today=today,
        )

        analysis = CoachAnalyzer(

            context

        ).analyze()

        return CoachRecommendation(

            context=context,

            analysis=analysis,

            strategy=analysis.strategy,

            summary=analysis.summary,

            warnings=analysis.warnings,
        )