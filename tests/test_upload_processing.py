"""
Tests for isolated in-memory activity upload processing.
"""

from gzip import (
    compress,
)
from io import (
    BytesIO,
)

import pytest

from performancelab.upload_processing import (
    open_activity_upload,
)
from performancelab.upload_validation import (
    InvalidUploadContentError,
)


def fit_content():
    """
    Return a structurally valid empty FIT file.
    """

    header = bytearray(
        12
    )

    header[0] = 12

    header[
        4:8
    ] = (
        0
    ).to_bytes(
        4,
        byteorder="little",
    )

    header[
        8:12
    ] = b".FIT"

    return bytes(
        header
    )


def test_opens_validated_fit_only_in_memory():

    source_reference = None

    with open_activity_upload(
        "activity.fit",
        fit_content(),
    ) as (
        source,
        importer_format,
    ):

        source_reference = source

        assert isinstance(
            source,
            BytesIO,
        )

        assert (
            importer_format
            == "fit"
        )

        assert (
            source.name
            == "activity.fit"
        )

        assert (
            source.read()
            == fit_content()
        )

        assert (
            source.closed
            is False
        )

    assert source_reference is not None

    assert (
        source_reference.closed
        is True
    )


def test_expands_fit_gzip_in_memory():

    original_content = (
        fit_content()
    )

    with open_activity_upload(
        "activity.fit.gz",
        compress(
            original_content
        ),
    ) as (
        source,
        importer_format,
    ):

        assert (
            importer_format
            == "fit"
        )

        assert (
            source.name
            == "activity.fit"
        )

        assert (
            source.read()
            == original_content
        )


def test_closes_memory_stream_after_processing_error():

    source_reference = None

    with pytest.raises(
        RuntimeError,
        match="simulated importer failure",
    ):

        with open_activity_upload(
            "activity.fit",
            fit_content(),
        ) as (
            source,
            importer_format,
        ):

            source_reference = source

            raise RuntimeError(
                "simulated importer failure"
            )

    assert source_reference is not None

    assert (
        source_reference.closed
        is True
    )


def test_invalid_content_never_opens_import_stream():

    entered_context = False

    with pytest.raises(
        InvalidUploadContentError
    ):

        with open_activity_upload(
            "activity.fit",
            b"not a FIT file",
        ):

            entered_context = True

    assert (
        entered_context
        is False
    )


def test_processing_creates_no_files(
    tmp_path,
    monkeypatch,
):

    monkeypatch.chdir(
        tmp_path
    )

    contents_before = tuple(
        tmp_path.iterdir()
    )

    with open_activity_upload(
        "activity.fit",
        fit_content(),
    ) as (
        source,
        importer_format,
    ):

        assert source.read()

    contents_after = tuple(
        tmp_path.iterdir()
    )

    assert contents_before == ()
    assert contents_after == ()