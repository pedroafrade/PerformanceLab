from dataclasses import dataclass, field

from .context import CoachContext
from .analyzer import CoachAnalysis


@dataclass(frozen=True)
class CoachRecommendation:

    context: CoachContext

    analysis: CoachAnalysis

    strategy: str

    summary: str

    warnings: tuple[str, ...] = field(default_factory=tuple)