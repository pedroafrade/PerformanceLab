"""
Tests for activity upload content validation.
"""

from gzip import (
    compress,
)

import pytest

from performancelab.upload_validation import (
    InvalidUploadContentError,
    validate_activity_upload_content,
)


def fit_content(
    *,
    data=b"",
    header_size=12,
    signature=b".FIT",
):
    """
    Build a minimal structural FIT file for validation tests.
    """

    header = bytearray(
        header_size
    )

    header[0] = header_size

    header[
        4:8
    ] = len(
        data
    ).to_bytes(
        4,
        byteorder="little",
    )

    header[
        8:12
    ] = signature

    return (
        bytes(
            header
        )
        + data
    )


def test_validates_fit_signature_and_structure():

    content = fit_content(
        data=b"FIT records"
    )

    result = (
        validate_activity_upload_content(
            "activity.fit",
            content,
        )
    )

    assert (
        result.importer_format
        == "fit"
    )
    assert (
        result.prepared_name
        == "activity.fit"
    )
    assert result.content == content


def test_validates_and_expands_fit_gzip():

    expanded_content = (
        fit_content(
            data=b"FIT records"
        )
    )

    result = (
        validate_activity_upload_content(
            "activity.fit.gz",
            compress(
                expanded_content
            ),
        )
    )

    assert (
        result.importer_format
        == "fit"
    )
    assert (
        result.prepared_name
        == "activity.fit"
    )
    assert (
        result.content
        == expanded_content
    )


def test_rejects_fake_fit_extension():

    with pytest.raises(
        InvalidUploadContentError,
        match="signature",
    ):

        validate_activity_upload_content(
            "activity.fit",
            (
                b"\x0c"
                + b"\x00"
                * 7
                + b"FAKE"
            ),
        )


def test_rejects_fit_size_that_disagrees_with_header():

    content = bytearray(
        fit_content()
    )

    content[
        4:8
    ] = (
        100
    ).to_bytes(
        4,
        byteorder="little",
    )

    with pytest.raises(
        InvalidUploadContentError,
        match="size does not match",
    ):

        validate_activity_upload_content(
            "activity.fit",
            bytes(
                content
            ),
        )


def test_validates_namespaced_gpx():

    content = (
        b'<?xml version="1.0"?>'
        b'<gpx xmlns="http://www.topografix.com/'
        b'GPX/1/1" version="1.1"></gpx>'
    )

    result = (
        validate_activity_upload_content(
            "route.gpx",
            content,
        )
    )

    assert (
        result.importer_format
        == "gpx"
    )
    assert result.content == content


def test_rejects_malformed_gpx():

    with pytest.raises(
        InvalidUploadContentError,
        match="not valid XML",
    ):

        validate_activity_upload_content(
            "route.gpx",
            b"<gpx><trk></gpx>",
        )


def test_rejects_xml_that_is_not_gpx():

    with pytest.raises(
        InvalidUploadContentError,
        match="must be gpx",
    ):

        validate_activity_upload_content(
            "route.gpx",
            b"<html></html>",
        )


@pytest.mark.parametrize(
    "declaration",
    (
        b'<!DOCTYPE gpx SYSTEM "external.dtd">',
        b'<!ENTITY example "unsafe">',
    ),
)
def test_rejects_gpx_document_declarations(
    declaration,
):

    content = (
        declaration
        + b"<gpx></gpx>"
    )

    with pytest.raises(
        InvalidUploadContentError,
        match="not accepted",
    ):

        validate_activity_upload_content(
            "route.gpx",
            content,
        )


def test_validates_strava_activities_csv():

    content = (
        (
            '"Nome da atividade",'
            '"Nome do ficheiro"\n'
            '"Morning run",'
            '"activities\\activity.fit.gz"\n'
        ).encode(
            "utf-8"
        )
    )

    result = (
        validate_activity_upload_content(
            "activities.csv",
            content,
        )
    )

    assert (
        result.importer_format
        == "strava-csv"
    )
    assert result.content == content


def test_rejects_unrecognized_csv_columns():

    with pytest.raises(
        InvalidUploadContentError,
        match="activity name column",
    ):

        validate_activity_upload_content(
            "activities.csv",
            b'"Unknown","Value"\n"one","two"\n',
        )


def test_rejects_content_that_does_not_match_extension():

    with pytest.raises(
        InvalidUploadContentError
    ):

        validate_activity_upload_content(
            "route.gpx",
            fit_content(),
        )


def test_rejects_non_binary_content():

    with pytest.raises(
        TypeError,
        match="must be bytes",
    ):

        validate_activity_upload_content(
            "activity.fit",
            "not binary",
        )