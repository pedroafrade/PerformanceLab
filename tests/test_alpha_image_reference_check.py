"""
PerformanceLab

Immutable alpha image reference preflight tests.
"""

from scripts.check_alpha_image_reference import (
    FAILURE_MESSAGE,
    SUCCESS_MESSAGE,
    main,
    validate_image_reference,
)


VALID_REFERENCE = (
    "europe-west1-docker.pkg.dev/"
    "example-project/performancelab/"
    "alpha@sha256:"
    + "a" * 64
)


def test_accepts_sha256_digest_reference():

    assert validate_image_reference(
        VALID_REFERENCE
    )


def test_rejects_mutable_tag_reference():

    assert not validate_image_reference(
        "example.invalid/performancelab:latest"
    )


def test_rejects_missing_reference():

    assert not validate_image_reference(
        None
    )


def test_success_does_not_print_reference(
    capsys,
):

    result = main(
        {
            "DEPLOYMENT_IMAGE_REFERENCE": (
                VALID_REFERENCE
            ),
        }
    )

    captured = capsys.readouterr()

    assert result == 0
    assert SUCCESS_MESSAGE in captured.out
    assert VALID_REFERENCE not in captured.out
    assert captured.err == ""


def test_failure_does_not_expose_value(
    capsys,
):

    invalid_reference = (
        "example.invalid/private-image:"
        "secret-tag"
    )

    result = main(
        {
            "DEPLOYMENT_IMAGE_REFERENCE": (
                invalid_reference
            ),
        }
    )

    captured = capsys.readouterr()

    output = (
        captured.out
        + captured.err
    )

    assert result == 1
    assert FAILURE_MESSAGE in captured.err
    assert invalid_reference not in output
    assert "secret-tag" not in output