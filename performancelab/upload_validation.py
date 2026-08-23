"""
PerformanceLab

Validation of activity upload content before import.
"""

from csv import (
    DictReader,
)
from dataclasses import (
    dataclass,
)
from io import (
    StringIO,
)
from typing import (
    Literal,
)
from xml.etree import (
    ElementTree,
)

from performancelab.upload_decompression import (
    decompress_fit_gzip,
)
from performancelab.upload_policy import (
    DEFAULT_ACTIVITY_UPLOAD_POLICY,
)


ImporterUploadFormat = Literal[
    "fit",
    "gpx",
    "strava-csv",
]


class InvalidUploadContentError(
    ValueError
):
    """
    Raised when file content does not match its declared format.
    """


@dataclass(
    frozen=True
)
class ValidatedActivityUpload:
    """
    Validated content ready for an importer or metadata reader.
    """

    original_name: str
    prepared_name: str
    importer_format: ImporterUploadFormat
    content: bytes


def _binary_content(
    content,
) -> bytes:
    """
    Return immutable uploaded bytes.
    """

    if not isinstance(
        content,
        (
            bytes,
            bytearray,
            memoryview,
        ),
    ):

        raise TypeError(
            "Uploaded content must be bytes."
        )

    return bytes(
        content
    )


def _validate_fit(
    content: bytes,
) -> None:
    """
    Validate the structural FIT file header.

    This does not construct a Workout or replace the complete
    FIT importer validation.
    """

    if len(
        content
    ) < 12:

        raise InvalidUploadContentError(
            "FIT content is shorter than its minimum header."
        )

    header_size = content[0]

    if header_size not in (
        12,
        14,
    ):

        raise InvalidUploadContentError(
            "FIT header size is not supported."
        )

    if len(
        content
    ) < header_size:

        raise InvalidUploadContentError(
            "FIT header is incomplete."
        )

    if (
        content[
            8:12
        ]
        != b".FIT"
    ):

        raise InvalidUploadContentError(
            "FIT signature is missing."
        )

    data_size = int.from_bytes(
        content[
            4:8
        ],
        byteorder="little",
        signed=False,
    )

    required_size = (
        header_size
        + data_size
    )

    accepted_sizes = {
        required_size,
        required_size + 2,
    }

    if len(
        content
    ) not in accepted_sizes:

        raise InvalidUploadContentError(
            "FIT content size does not match its header."
        )


def _validate_gpx(
    content: bytes,
) -> None:
    """
    Validate that GPX content is safe, complete XML with a GPX
    root element.
    """

    upper_content = (
        content.upper()
    )

    if (
        b"<!DOCTYPE"
        in upper_content
        or b"<!ENTITY"
        in upper_content
    ):

        raise InvalidUploadContentError(
            "GPX document type and entity declarations "
            "are not accepted."
        )

    try:

        root = ElementTree.fromstring(
            content
        )

    except (
        ElementTree.ParseError,
        ValueError,
    ) as error:

        raise InvalidUploadContentError(
            "GPX content is not valid XML."
        ) from error

    root_name = (
        str(
            root.tag
        )
        .rsplit(
            "}",
            1,
        )[-1]
        .lower()
    )

    if root_name != "gpx":

        raise InvalidUploadContentError(
            "XML root element must be gpx."
        )


def _validate_strava_csv(
    content: bytes,
) -> None:
    """
    Validate the metadata columns used from activities.csv.
    """

    if b"\x00" in content:

        raise InvalidUploadContentError(
            "Strava CSV contains binary null bytes."
        )

    try:

        text = content.decode(
            "utf-8-sig"
        )

    except UnicodeDecodeError as error:

        raise InvalidUploadContentError(
            "Strava CSV must use UTF-8 encoding."
        ) from error

    reader = DictReader(
        StringIO(
            text
        )
    )

    field_names = {
        str(
            field_name
            or ""
        ).strip()
        for field_name
        in (
            reader.fieldnames
            or ()
        )
    }

    activity_name_fields = {
        "Activity Name",
        "Nome da atividade",
    }

    activity_file_fields = {
        "Filename",
        "File Name",
        "Nome do ficheiro",
    }

    if not (
        field_names
        & activity_name_fields
    ):

        raise InvalidUploadContentError(
            "Strava CSV has no recognized activity name column."
        )

    if not (
        field_names
        & activity_file_fields
    ):

        raise InvalidUploadContentError(
            "Strava CSV has no recognized activity file column."
        )


def validate_activity_upload_content(
    file_name: str,
    content,
) -> ValidatedActivityUpload:
    """
    Validate one upload before passing it to an importer.

    FIT.GZ content is safely expanded and returned as FIT.
    """

    binary_content = _binary_content(
        content
    )

    upload_format = (
        DEFAULT_ACTIVITY_UPLOAD_POLICY
        .format_for(
            file_name
        )
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
    )

    if upload_format == "fit.gz":

        expanded_content = (
            decompress_fit_gzip(
                binary_content
            )
        )

        _validate_fit(
            expanded_content
        )

        return ValidatedActivityUpload(
            original_name=normalized_name,
            prepared_name=(
                normalized_name[:-3]
            ),
            importer_format="fit",
            content=expanded_content,
        )

    if upload_format == "fit":

        _validate_fit(
            binary_content
        )

        return ValidatedActivityUpload(
            original_name=normalized_name,
            prepared_name=normalized_name,
            importer_format="fit",
            content=binary_content,
        )

    if upload_format == "gpx":

        _validate_gpx(
            binary_content
        )

        return ValidatedActivityUpload(
            original_name=normalized_name,
            prepared_name=normalized_name,
            importer_format="gpx",
            content=binary_content,
        )

    _validate_strava_csv(
        binary_content
    )

    return ValidatedActivityUpload(
        original_name=normalized_name,
        prepared_name=normalized_name,
        importer_format="strava-csv",
        content=binary_content,
    )