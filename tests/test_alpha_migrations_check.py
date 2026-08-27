"""
PerformanceLab

Private alpha migration preflight tests.
"""

from types import (
    SimpleNamespace,
)

from scripts.check_alpha_migrations import (
    FAILURE_MESSAGE,
    SUCCESS_MESSAGE,
    main,
    validate_alpha_migrations,
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


class FakeConnection:

    def __enter__(self):

        return self

    def __exit__(
        self,
        exception_type,
        exception,
        traceback,
    ):

        return False


class FakeEngine:

    def __init__(self):

        self.disposed = False

    def connect(self):

        return FakeConnection()

    def dispose(self):

        self.disposed = True


def validate_with_revisions(
    current_revisions,
    expected_revisions,
):

    engine = FakeEngine()

    result = validate_alpha_migrations(
        valid_alpha_values(),
        engine_factory=(
            lambda database_url, **options:
            engine
        ),
        config_factory=(
            lambda path:
            SimpleNamespace()
        ),
        script_factory=(
            lambda configuration:
            SimpleNamespace(
                get_heads=(
                    lambda:
                    expected_revisions
                )
            )
        ),
        context_factory=(
            lambda connection:
            SimpleNamespace(
                get_current_heads=(
                    lambda:
                    current_revisions
                )
            )
        ),
    )

    return result, engine


def test_accepts_current_database_revision():

    result, engine = validate_with_revisions(
        ("revision-2",),
        ("revision-2",),
    )

    assert result
    assert engine.disposed


def test_rejects_stale_database_revision():

    result, engine = validate_with_revisions(
        ("revision-1",),
        ("revision-2",),
    )

    assert not result
    assert engine.disposed


def test_rejects_database_without_revision():

    result, engine = validate_with_revisions(
        (),
        ("revision-2",),
    )

    assert not result
    assert engine.disposed


def test_rejects_non_alpha_environment():

    assert not validate_alpha_migrations(
        {
            "PERFORMANCELAB_ENV": "local",
        }
    )


def test_failure_does_not_expose_database_url(
    monkeypatch,
    capsys,
):

    monkeypatch.setattr(
        "scripts.check_alpha_migrations."
        "validate_alpha_migrations",
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
        "scripts.check_alpha_migrations."
        "validate_alpha_migrations",
        lambda values: True,
    )

    result = main(
        valid_alpha_values()
    )

    captured = capsys.readouterr()

    assert result == 0
    assert SUCCESS_MESSAGE in captured.out
    assert captured.err == ""