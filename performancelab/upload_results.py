"""
PerformanceLab

Immutable factual results for activity upload batches.
"""

from dataclasses import (
    dataclass,
)
from typing import (
    Literal,
)


ActivityFileImportStatus = Literal[
    "imported",
    "updated",
    "duplicate",
    "ignored",
    "invalid",
]


@dataclass(
    frozen=True
)
class ActivityFileImportResult:
    """
    Factual result for one selected upload file.
    """

    file_name: str
    status: ActivityFileImportStatus
    workout_id: str | None = None
    reason: str | None = None

    def __post_init__(
        self,
    ) -> None:

        if not isinstance(
            self.file_name,
            str,
        ) or not self.file_name.strip():

            raise ValueError(
                "Activity file name cannot be empty."
            )

        if self.status not in (
            "imported",
            "updated",
            "duplicate",
            "ignored",
            "invalid",
        ):

            raise ValueError(
                "Unsupported activity file result status."
            )

        normalized_workout_id = (
            self.workout_id.strip()
            if isinstance(
                self.workout_id,
                str,
            )
            and self.workout_id.strip()
            else None
        )

        if (
            self.workout_id is not None
            and not isinstance(
                self.workout_id,
                str,
            )
        ):

            raise TypeError(
                "workout_id must be a string or None."
            )

        if (
            self.status
            in (
                "imported",
                "updated",
                "duplicate",
            )
            and normalized_workout_id
            is None
        ):

            raise ValueError(
                "A processed activity result must have "
                "a workout_id."
            )

        object.__setattr__(
            self,
            "file_name",
            self.file_name.strip(),
        )

        object.__setattr__(
            self,
            "workout_id",
            normalized_workout_id,
        )


@dataclass(
    frozen=True
)
class ActivityUploadBatchResult:
    """
    Ordered factual results for one upload selection.
    """

    files: tuple[
        ActivityFileImportResult,
        ...,
    ]

    def __post_init__(
        self,
    ) -> None:

        if not isinstance(
            self.files,
            tuple,
        ):

            raise TypeError(
                "Upload batch files must be a tuple."
            )

        if not all(
            isinstance(
                result,
                ActivityFileImportResult,
            )
            for result in self.files
        ):

            raise TypeError(
                "Upload batch contains an invalid result."
            )

    def count(
        self,
        status: ActivityFileImportStatus,
    ) -> int:
        """
        Count files with one factual result.
        """

        return sum(
            1
            for result in self.files
            if result.status == status
        )

    @property
    def imported_count(
        self,
    ) -> int:

        return self.count(
            "imported"
        )

    @property
    def updated_count(
        self,
    ) -> int:

        return self.count(
            "updated"
        )

    @property
    def duplicate_count(
        self,
    ) -> int:

        return self.count(
            "duplicate"
        )

    @property
    def ignored_count(
        self,
    ) -> int:

        return self.count(
            "ignored"
        )

    @property
    def invalid_count(
        self,
    ) -> int:

        return self.count(
            "invalid"
        )

    @property
    def notice(
        self,
    ) -> str:
        """
        Return the compact user-facing batch summary.
        """

        return (
            "Import complete: "
            f"{self.imported_count} imported, "
            f"{self.updated_count} updated, "
            f"{self.duplicate_count} duplicate, "
            f"{self.ignored_count} ignored, "
            f"{self.invalid_count} invalid."
        )