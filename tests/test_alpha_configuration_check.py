"""
PerformanceLab

Private alpha configuration preflight tests.
"""

from scripts.check_alpha_configuration import (
    FAILURE_MESSAGE,
    SUCCESS_MESSAGE,
    main,
    validate_alpha_configuration,
)


def valid_alpha_values() -> dict[
    str,
    str,
]:

    return {
        "PERFORMANCELAB_ENV": "alpha",
        "DATABASE_URL": (
            "postgresql+psycopg://"
            "user:secret@db.example.com/"
            "performancelab"
        ),
        "PRIVACY_CONTACT_EMAIL": (
            "privacy@example.com"
        ),
        "SUPPORT_CONTACT_EMAIL": (
            "support@example.com"
        ),
        "RETENTION_INACTIVE_ACCOUNT_DAYS": "90",
        "RETENTION_INACTIVITY_NOTICE_DAYS": "14",
        "RETENTION_TRAINING_COACH_USAGE_DAYS": "30",
        "RETENTION_CONSENT_EVIDENCE_DAYS": "0",
        "RETENTION_UNUSED_INVITATION_DAYS": "14",
        "RETENTION_EXPIRED_INVITATION_DAYS": "7",
        "RETENTION_APPLICATION_LOG_DAYS": "14",
        "RETENTION_ERROR_ALERT_DAYS": "30",
        "RETENTION_BACKUP_DAYS": "14",
        "RETENTION_SUPPORT_REQUEST_DAYS": "90",
        "RETENTION_POST_ALPHA_DAYS": "30",
    }


def test_accepts_complete_alpha_configuration():

    assert validate_alpha_configuration(
        valid_alpha_values()
    )


def test_rejects_local_configuration():

    assert not validate_alpha_configuration(
        {
            "PERFORMANCELAB_ENV": "local",
        }
    )


def test_success_message_contains_no_values(
    capsys,
):

    result = main(
        valid_alpha_values()
    )

    captured = capsys.readouterr()

    assert result == 0
    assert SUCCESS_MESSAGE in captured.out
    assert "db.example.com" not in captured.out
    assert "secret" not in captured.out
    assert captured.err == ""


def test_failure_does_not_expose_secret(
    capsys,
):

    result = main(
        {
            "PERFORMANCELAB_ENV": "alpha",
            "DATABASE_URL": (
                "postgresql+psycopg://"
                "user:super-secret-password"
                "@db.example.com/performancelab"
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
    assert "super-secret-password" not in output
    assert "db.example.com" not in output

def test_rejects_alpha_without_support_contact():

    values = valid_alpha_values()

    values.pop(
        "SUPPORT_CONTACT_EMAIL"
    )

    assert not validate_alpha_configuration(
        values
    )


def test_support_contact_is_not_printed(
    capsys,
):

    values = valid_alpha_values()

    result = main(
        values
    )

    captured = capsys.readouterr()

    output = (
        captured.out
        + captured.err
    )

    assert result == 0
    assert "support@example.com" not in output