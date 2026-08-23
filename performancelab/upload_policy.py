"""
PerformanceLab

Explicit limits for activity file uploads.
"""

from dataclasses import (
    dataclass,
)
from typing import (
    Literal,
)


MEBIBYTE = (
    1024
    * 1024
)


UploadFormat = Literal[
    "fit",
    "fit.gz",
    "gpx",
    "strava-csv",
]


class UploadPolicyError(
    ValueError
):
    """
    Base error for a rejected upload selection.
    """


class TooManyUploadFilesError(
    UploadPolicyError
):
    """
    Raised when one selection contains too many files.
    """


class UploadFileTooLargeError(
    UploadPolicyError
):
    """
    Raised when one compressed or uncompressed source file is
    larger than the accepted input limit.
    """


class UnsupportedUploadFormatError(
    UploadPolicyError
):
    """
    Raised when a file name does not identify an accepted format.
    """


@dataclass(
    frozen=True
)
class UploadCandidate:
    """
    Factual metadata available before reading an uploaded file.
    """

    name: str
    size_bytes: int

    def __post_init__(
        self,
    ) -> None:
        """
        Normalize and validate the factual file metadata.
        """

        if not isinstance(
            self.name,
            str,
        ):
            raise TypeError(
                "Upload file name must be a string."
            )

        normalized_name = (
            self.name.strip()
        )

        if not normalized_name:

            raise ValueError(
                "Upload file name cannot be empty."
            )

        if (
            not isinstance(
                self.size_bytes,
                int,
            )
            or isinstance(
                self.size_bytes,
                bool,
            )
        ):

            raise TypeError(
                "Upload file size must be an integer."
            )

        if self.size_bytes < 0:

            raise ValueError(
                "Upload file size cannot be negative."
            )

        object.__setattr__(
            self,
            "name",
            normalized_name,
        )


@dataclass(
    frozen=True
)
class ActivityUploadPolicy:
    """
    Immutable limits for one activity upload selection.

    The compressed FIT.GZ size is checked here. Its expanded
    size receives a separate limit in the next step.
    """

    maximum_files: int = 20

    maximum_file_size_bytes: int = (
        20
        * MEBIBYTE
    )

    def __post_init__(
        self,
    ) -> None:
        """
        Validate the configured limits.
        """

        for field_name in (
            "maximum_files",
            "maximum_file_size_bytes",
        ):

            value = getattr(
                self,
                field_name,
            )

            if (
                not isinstance(
                    value,
                    int,
                )
                or isinstance(
                    value,
                    bool,
                )
            ):

                raise TypeError(
                    f"{field_name} must be an integer."
                )

            if value < 1:

                raise ValueError(
                    f"{field_name} must be positive."
                )

    @staticmethod
    def format_for(
        file_name: str,
    ) -> UploadFormat:
        """
        Return the supported format identified by a file name.

        A CSV file is accepted only when its name is exactly
        activities.csv, the metadata index used in a Strava
        export.
        """

        if not isinstance(
            file_name,
            str,
        ):

            raise TypeError(
                "Upload file name must be a string."
            )

        normalized_name = (
            file_name
            .strip()
            .replace(
                "\\",
                "/",
            )
            .rsplit(
                "/",
                1,
            )[-1]
            .lower()
        )

        if normalized_name.endswith(
            ".fit.gz"
        ):

            return "fit.gz"

        if normalized_name.endswith(
            ".fit"
        ):

            return "fit"

        if normalized_name.endswith(
            ".gpx"
        ):

            return "gpx"

        if (
            normalized_name
            == "activities.csv"
        ):

            return "strava-csv"

        raise UnsupportedUploadFormatError(
            f"Unsupported activity upload: "
            f"{normalized_name or 'unnamed file'}."
        )

    def validate(
        self,
        candidates,
    ) -> tuple[
        UploadCandidate,
        ...,
    ]:
        """
        Validate one complete selection before file parsing.

        Returns the immutable validated selection in its original
        order.
        """

        validated_candidates = tuple(
            candidates
        )

        if (
            len(
                validated_candidates
            )
            > self.maximum_files
        ):

            raise TooManyUploadFilesError(
                "A maximum of "
                f"{self.maximum_files} files "
                "can be uploaded at once."
            )

        for candidate in (
            validated_candidates
        ):

            if not isinstance(
                candidate,
                UploadCandidate,
            ):

                raise TypeError(
                    "Every upload candidate must be an "
                    "UploadCandidate."
                )

            self.format_for(
                candidate.name
            )

            if (
                candidate.size_bytes
                > self.maximum_file_size_bytes
            ):

                raise UploadFileTooLargeError(
                    f"{candidate.name} exceeds the "
                    f"{self.maximum_file_size_bytes} byte "
                    "upload limit."
                )

        return validated_candidates


DEFAULT_ACTIVITY_UPLOAD_POLICY = (
    ActivityUploadPolicy()
)