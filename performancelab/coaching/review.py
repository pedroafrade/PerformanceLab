"""
PerformanceLab

Plan Review

Domain models used to describe the quality of an athlete's
training plan after generation or manual adjustment.
"""

from dataclasses import dataclass, field
from enum import Enum

from ..training.config.availability import Weekday


class ReviewSeverity(str, Enum):
    """
    Severity of an individual review finding.
    """

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class ReviewCategory(str, Enum):
    """
    Area of the training plan affected by a finding.
    """

    AVAILABILITY = "availability"
    CONSTRAINT = "constraint"
    PREFERENCE = "preference"
    RECOVERY = "recovery"
    INTENSITY = "intensity"
    VOLUME = "volume"
    CONSISTENCY = "consistency"
    SCHEDULING = "scheduling"


@dataclass(frozen=True)
class ReviewFinding:
    """
    Describes one issue, observation or suggestion found
    while reviewing a training plan.
    """

    code: str

    message: str

    severity: ReviewSeverity

    category: ReviewCategory

    day: Weekday | None = None

    suggestion: str | None = None

    # ======================================================

    def __post_init__(self) -> None:

        code = self.code.strip()
        message = self.message.strip()

        if not code:

            raise ValueError(
                "Review finding code cannot be empty."
            )

        if not message:

            raise ValueError(
                "Review finding message cannot be empty."
            )

        normalized_day = (
            None
            if self.day is None
            else Weekday(self.day)
        )

        suggestion = (
            self.suggestion.strip()
            if self.suggestion
            else None
        )

        object.__setattr__(
            self,
            "code",
            code,
        )

        object.__setattr__(
            self,
            "message",
            message,
        )

        object.__setattr__(
            self,
            "day",
            normalized_day,
        )

        object.__setattr__(
            self,
            "suggestion",
            suggestion,
        )


@dataclass(frozen=True)
class PlanReview:
    """
    Represents the complete review of a training plan.

    Scores use a scale from 0 to 100, where a higher score
    indicates a better result.
    """

    score: int

    consistency_score: int

    recovery_score: int

    availability_score: int

    constraint_score: int

    findings: tuple[ReviewFinding, ...] = field(
        default_factory=tuple,
    )

    summary: str = ""

    # ======================================================

    def __post_init__(self) -> None:

        for name, value in (
            ("score", self.score),
            (
                "consistency_score",
                self.consistency_score,
            ),
            (
                "recovery_score",
                self.recovery_score,
            ),
            (
                "availability_score",
                self.availability_score,
            ),
            (
                "constraint_score",
                self.constraint_score,
            ),
        ):

            if not 0 <= value <= 100:

                raise ValueError(
                    f"{name} must be between 0 and 100."
                )

        normalized_findings = tuple(
            self.findings,
        )

        if not all(
            isinstance(finding, ReviewFinding)
            for finding in normalized_findings
        ):

            raise TypeError(
                "All findings must be ReviewFinding "
                "instances."
            )

        object.__setattr__(
            self,
            "findings",
            normalized_findings,
        )

        object.__setattr__(
            self,
            "summary",
            self.summary.strip(),
        )

    # ======================================================

    @property
    def valid(self) -> bool:
        """
        Returns False when at least one error is present.

        Warnings do not invalidate a plan because the athlete
        remains free to accept them.
        """

        return not any(
            finding.severity is ReviewSeverity.ERROR
            for finding in self.findings
        )

    # ======================================================

    @property
    def errors(self) -> tuple[ReviewFinding, ...]:
        """
        Returns findings that invalidate the plan.
        """

        return self.findings_by_severity(
            ReviewSeverity.ERROR,
        )

    # ======================================================

    @property
    def warnings(self) -> tuple[ReviewFinding, ...]:
        """
        Returns coaching warnings that do not invalidate the
        plan.
        """

        return self.findings_by_severity(
            ReviewSeverity.WARNING,
        )

    # ======================================================

    @property
    def information(self) -> tuple[ReviewFinding, ...]:
        """
        Returns informational observations.
        """

        return self.findings_by_severity(
            ReviewSeverity.INFO,
        )

    # ======================================================

    def findings_by_severity(
        self,
        severity: ReviewSeverity,
    ) -> tuple[ReviewFinding, ...]:
        """
        Filters review findings by severity.
        """

        return tuple(
            finding
            for finding in self.findings
            if finding.severity is severity
        )

    # ======================================================

    def findings_by_category(
        self,
        category: ReviewCategory,
    ) -> tuple[ReviewFinding, ...]:
        """
        Filters review findings by category.
        """

        return tuple(
            finding
            for finding in self.findings
            if finding.category is category
        )