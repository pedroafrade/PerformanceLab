"""
PerformanceLab

Isolated in-memory processing of validated activity uploads.
"""

from contextlib import (
    contextmanager,
)
from io import (
    BytesIO,
)

from performancelab.upload_validation import (
    validate_activity_upload_content,
)


@contextmanager
def open_activity_upload(
    file_name: str,
    content,
):
    """
    Open one validated upload as a temporary in-memory stream.

    No original upload is written to disk. The stream is always
    closed after success or failure.
    """

    validated_upload = (
        validate_activity_upload_content(
            file_name,
            content,
        )
    )

    source = BytesIO(
        validated_upload.content
    )

    source.name = (
        validated_upload.prepared_name
    )

    try:

        yield (
            source,
            validated_upload
            .importer_format,
        )

    finally:

        source.close()