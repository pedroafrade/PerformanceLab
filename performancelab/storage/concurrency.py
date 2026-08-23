"""
PerformanceLab

Persistence concurrency errors.
"""


class ConcurrentAthleteUpdateError(
    RuntimeError
):
    """
    Raised when an outdated athlete version is saved.
    """

    def __init__(
        self,
        athlete_id: str,
        *,
        expected_version: int | None,
        actual_version: int,
    ) -> None:

        self.athlete_id = athlete_id
        self.expected_version = (
            expected_version
        )
        self.actual_version = (
            actual_version
        )

        expected_description = (
            str(expected_version)
            if expected_version is not None
            else "unknown"
        )

        super().__init__(
            "Athlete was changed by another operation. "
            f"Athlete: {athlete_id}. "
            f"Expected version: {expected_description}. "
            f"Current version: {actual_version}."
        )