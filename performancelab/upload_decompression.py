"""
PerformanceLab

Bounded decompression of uploaded activity files.
"""

from gzip import (
    BadGzipFile,
    GzipFile,
)
from io import (
    BytesIO,
)

from performancelab.upload_policy import (
    MEBIBYTE,
)


MAXIMUM_FIT_GZIP_EXPANDED_BYTES = (
    100
    * MEBIBYTE
)

_DECOMPRESSION_CHUNK_BYTES = (
    64
    * 1024
)


class UploadDecompressionError(
    ValueError
):
    """
    Raised when compressed upload content is not valid.
    """


class ExpandedUploadTooLargeError(
    UploadDecompressionError
):
    """
    Raised when expanded content exceeds the safe limit.
    """


def decompress_fit_gzip(
    compressed_content,
    *,
    maximum_expanded_bytes: int = (
        MAXIMUM_FIT_GZIP_EXPANDED_BYTES
    ),
) -> bytes:
    """
    Decompress one FIT.GZ upload without unbounded allocation.

    At most the configured limit plus one detection byte is read
    from the expanded stream.
    """

    if not isinstance(
        compressed_content,
        (
            bytes,
            bytearray,
            memoryview,
        ),
    ):

        raise TypeError(
            "Compressed upload content must be bytes."
        )

    if (
        not isinstance(
            maximum_expanded_bytes,
            int,
        )
        or isinstance(
            maximum_expanded_bytes,
            bool,
        )
    ):

        raise TypeError(
            "maximum_expanded_bytes must be an integer."
        )

    if maximum_expanded_bytes < 1:

        raise ValueError(
            "maximum_expanded_bytes must be positive."
        )

    source = BytesIO(
        bytes(
            compressed_content
        )
    )

    expanded_parts = []
    expanded_size = 0

    try:

        with GzipFile(
            fileobj=source,
            mode="rb",
        ) as compressed_file:

            while True:

                remaining_bytes = (
                    maximum_expanded_bytes
                    - expanded_size
                )

                read_size = min(
                    _DECOMPRESSION_CHUNK_BYTES,
                    remaining_bytes + 1,
                )

                part = compressed_file.read(
                    read_size
                )

                if not part:

                    break

                expanded_size += len(
                    part
                )

                if (
                    expanded_size
                    > maximum_expanded_bytes
                ):

                    raise (
                        ExpandedUploadTooLargeError(
                            "Expanded FIT.GZ content exceeds "
                            f"{maximum_expanded_bytes} bytes."
                        )
                    )

                expanded_parts.append(
                    part
                )

    except ExpandedUploadTooLargeError:

        raise

    except (
        BadGzipFile,
        EOFError,
        OSError,
    ) as error:

        raise UploadDecompressionError(
            "The FIT.GZ content is invalid or incomplete."
        ) from error

    return b"".join(
        expanded_parts
    )