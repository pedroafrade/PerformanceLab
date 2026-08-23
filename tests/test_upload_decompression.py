"""
Tests for bounded FIT.GZ decompression.
"""

from gzip import (
    compress,
)

import pytest

from performancelab.upload_decompression import (
    MAXIMUM_FIT_GZIP_EXPANDED_BYTES,
    ExpandedUploadTooLargeError,
    UploadDecompressionError,
    decompress_fit_gzip,
)
from performancelab.upload_policy import (
    MEBIBYTE,
)


def test_decompresses_valid_fit_gzip_content():

    original_content = (
        b"valid FIT activity data"
    )

    result = decompress_fit_gzip(
        compress(
            original_content
        )
    )

    assert result == original_content


def test_accepts_content_at_exact_expanded_limit():

    original_content = (
        b"A"
        * 100
    )

    result = decompress_fit_gzip(
        compress(
            original_content
        ),
        maximum_expanded_bytes=100,
    )

    assert result == original_content


def test_rejects_content_above_expanded_limit():

    compressed_content = compress(
        b"A"
        * 101
    )

    with pytest.raises(
        ExpandedUploadTooLargeError,
        match="exceeds 100 bytes",
    ):

        decompress_fit_gzip(
            compressed_content,
            maximum_expanded_bytes=100,
        )


def test_rejects_highly_compressible_oversized_content():

    compressed_content = compress(
        b"A"
        * (
            2
            * MEBIBYTE
        )
    )

    assert len(
        compressed_content
    ) < (
        10
        * 1024
    )

    with pytest.raises(
        ExpandedUploadTooLargeError
    ):

        decompress_fit_gzip(
            compressed_content,
            maximum_expanded_bytes=(
                1
                * MEBIBYTE
            ),
        )


def test_rejects_non_gzip_content():

    with pytest.raises(
        UploadDecompressionError,
        match="invalid or incomplete",
    ):

        decompress_fit_gzip(
            b"this is not gzip content"
        )


def test_rejects_truncated_gzip_content():

    compressed_content = compress(
        b"FIT activity data"
    )

    truncated_content = (
        compressed_content[:-4]
    )

    with pytest.raises(
        UploadDecompressionError,
        match="invalid or incomplete",
    ):

        decompress_fit_gzip(
            truncated_content
        )


@pytest.mark.parametrize(
    "compressed_content",
    (
        None,
        "not bytes",
        123,
    ),
)
def test_rejects_non_binary_content(
    compressed_content,
):

    with pytest.raises(
        TypeError,
        match="must be bytes",
    ):

        decompress_fit_gzip(
            compressed_content
        )


@pytest.mark.parametrize(
    (
        "maximum_expanded_bytes",
        "expected_error",
    ),
    (
        (
            0,
            ValueError,
        ),
        (
            -1,
            ValueError,
        ),
        (
            1.5,
            TypeError,
        ),
        (
            True,
            TypeError,
        ),
        (
            "100",
            TypeError,
        ),
    ),
)
def test_rejects_invalid_expanded_limit(
    maximum_expanded_bytes,
    expected_error,
):

    with pytest.raises(
        expected_error
    ):

        decompress_fit_gzip(
            compress(
                b"FIT"
            ),
            maximum_expanded_bytes=(
                maximum_expanded_bytes
            ),
        )


def test_default_expanded_limit_is_100_mebibytes():

    assert (
        MAXIMUM_FIT_GZIP_EXPANDED_BYTES
        == 100
        * MEBIBYTE
    )