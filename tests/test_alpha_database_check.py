"""
PerformanceLab

Private alpha database preflight tests.
"""

from types import (
    SimpleNamespace,
)

from scripts.check_alpha_database import (
    FAILURE_MESSAGE,
    SUCCESS_MESSAGE,
    main,
    validate_alpha_database,
)


def valid_alpha_values() -> dict[str, str]:

    return {
        "PERFORMANCELAB_ENV": "alpha",
        "DATABASE_URL": (
            "postgresql+psycopg://"
            "user@db.example.com/"
            "performancelab"
        ),
        "PRIVACY_CONTACT_EMAIL": (
            "privacy@example.com"
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


class FakeRepositoryBundle:

    def __init__(self):

        self.closed = False

    def close(self):

        self.closed = True


def test_accepts_ready_alpha_database():

    bundle = FakeRepositoryBundle()

    result = validate_alpha_database(
        valid_alpha_values(),
        bundle_builder=(
            lambda configuration: bundle
        ),
        health_checker=(
            lambda configuration, repository_bundle:
            SimpleNamespace(ready=True)
        ),
    )

    assert result
    assert bundle.closed


def test_rejects_unavailable_alpha_database():

    bundle = FakeRepositoryBundle()

    result = validate_alpha_database(
        valid_alpha_values(),
        bundle_builder=(
            lambda configuration: bundle
        ),
        health_checker=(
            lambda configuration, repository_bundle:
            SimpleNamespace(ready=False)
        ),
    )

    assert not result
    assert bundle.closed


def test_rejects_non_alpha_environment():

    assert not validate_alpha_database(
        {
            "PERFORMANCELAB_ENV": "local",
        }
    )


def test_failure_does_not_expose_database_url(
    monkeypatch,
    capsys,
):

    monkeypatch.setattr(
        "scripts.check_alpha_database."
        "validate_alpha_database",
        lambda values: False,
    )

    result = main(
        {
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


def test_success_message_is_safe(
    monkeypatch,
    capsys,
):

    monkeypatch.setattr(
        "scripts.check_alpha_database."
        "validate_alpha_database",
        lambda values: True,
    )

    result = main(
        valid_alpha_values()
    )

    captured = capsys.readouterr()

    assert result == 0
    assert SUCCESS_MESSAGE in captured.out
    assert captured.err == ""