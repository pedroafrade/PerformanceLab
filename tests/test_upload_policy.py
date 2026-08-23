"""
Tests for factual activity upload limits.
"""

from dataclasses import (
    FrozenInstanceError,
)

import pytest

from performancelab.upload_policy import (
    DEFAULT_ACTIVITY_UPLOAD_POLICY,
    MEBIBYTE,
    ActivityUploadPolicy,
    TooManyUploadFilesError,
    UnsupportedUploadFormatError,
    UploadCandidate,
    UploadFileTooLargeError,
)


@pytest.mark.parametrize(
    (
        "file_name",
        "expected_format",
    ),
    (
        (
            "activity.fit",
            "fit",
        ),
        (
            "ACTIVITY.FIT",
            "fit",
        ),
        (
            "activity.fit.gz",
            "fit.gz",
        ),
        (
            "Activity.FIT.GZ",
            "fit.gz",
        ),
        (
            "route.gpx",
            "gpx",
        ),
        (
            "activities.csv",
            "strava-csv",
        ),
        (
            "ACTIVITIES.CSV",
            "strava-csv",
        ),
    ),
)
def test_identifies_supported_upload_formats(
    file_name,
    expected_format,
):

    assert (
        DEFAULT_ACTIVITY_UPLOAD_POLICY
        .format_for(
            file_name
        )
        == expected_format
    )


@pytest.mark.parametrize(
    "file_name",
    (
        "activity.csv",
        "workouts.csv",
        "route.gpx.gz",
        "archive.gz",
        "activity.zip",
        "activity.exe",
        "activity",
    ),
)
def test_rejects_unsupported_upload_formats(
    file_name,
):

    with pytest.raises(
        UnsupportedUploadFormatError
    ):

        (
            DEFAULT_ACTIVITY_UPLOAD_POLICY
            .format_for(
                file_name
            )
        )


def test_accepts_selection_at_exact_limits():

    policy = ActivityUploadPolicy(
        maximum_files=2,
        maximum_file_size_bytes=(
            20
            * MEBIBYTE
        ),
    )

    candidates = (
        UploadCandidate(
            name="first.fit",
            size_bytes=(
                20
                * MEBIBYTE
            ),
        ),
        UploadCandidate(
            name="second.gpx",
            size_bytes=(
                20
                * MEBIBYTE
            ),
        ),
    )

    assert (
        policy.validate(
            candidates
        )
        == candidates
    )


def test_rejects_too_many_files():

    policy = ActivityUploadPolicy(
        maximum_files=2
    )

    candidates = (
        UploadCandidate(
            name="first.fit",
            size_bytes=1,
        ),
        UploadCandidate(
            name="second.fit",
            size_bytes=1,
        ),
        UploadCandidate(
            name="third.fit",
            size_bytes=1,
        ),
    )

    with pytest.raises(
        TooManyUploadFilesError,
        match="maximum of 2 files",
    ):

        policy.validate(
            candidates
        )


def test_rejects_file_above_size_limit():

    policy = ActivityUploadPolicy(
        maximum_file_size_bytes=100
    )

    with pytest.raises(
        UploadFileTooLargeError,
        match="large.fit",
    ):

        policy.validate(
            (
                UploadCandidate(
                    name="large.fit",
                    size_bytes=101,
                ),
            )
        )


def test_rejects_unsupported_file_before_parsing():

    policy = ActivityUploadPolicy()

    with pytest.raises(
        UnsupportedUploadFormatError
    ):

        policy.validate(
            (
                UploadCandidate(
                    name="activity.zip",
                    size_bytes=1,
                ),
            )
        )


def test_default_policy_uses_private_alpha_limits():

    assert (
        DEFAULT_ACTIVITY_UPLOAD_POLICY
        .maximum_files
        == 20
    )

    assert (
        DEFAULT_ACTIVITY_UPLOAD_POLICY
        .maximum_file_size_bytes
        == 20
        * MEBIBYTE
    )


def test_upload_models_are_immutable():

    candidate = UploadCandidate(
        name="activity.fit",
        size_bytes=100,
    )

    policy = ActivityUploadPolicy()

    with pytest.raises(
        FrozenInstanceError
    ):

        candidate.size_bytes = 200

    with pytest.raises(
        FrozenInstanceError
    ):

        policy.maximum_files = 100


@pytest.mark.parametrize(
    "size_bytes",
    (
        -1,
        1.5,
        True,
        "100",
    ),
)
def test_rejects_invalid_file_size(
    size_bytes,
):

    expected_error = (
        ValueError
        if (
            isinstance(
                size_bytes,
                int,
            )
            and not isinstance(
                size_bytes,
                bool,
            )
        )
        else TypeError
    )

    with pytest.raises(
        expected_error
    ):

        UploadCandidate(
            name="activity.fit",
            size_bytes=size_bytes,
        )


def test_empty_selection_is_valid():

    assert (
        DEFAULT_ACTIVITY_UPLOAD_POLICY
        .validate(
            ()
        )
        == ()
    )