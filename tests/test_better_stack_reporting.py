"""
PerformanceLab

Privacy-safe Better Stack reporting tests.
"""

import pytest

from performancelab.better_stack_reporting import (
    BetterStackExceptionReporter,
    build_exception_reporter,
)
from performancelab.exception_reporting import (
    ExceptionAlert,
    LoggingExceptionReporter,
)


VALID_DSN = (
    "https://application-token"
    "@errors.example.com/12345"
)


class FakeSdk:

    def __init__(self):

        self.init_options = None
        self.events = []

    def init(
        self,
        **options,
    ):

        self.init_options = options

    def capture_event(
        self,
        event,
    ):

        self.events.append(event)


def test_local_environment_uses_logging_without_dsn():

    reporter = build_exception_reporter(
        {},
        environment="local",
    )

    assert isinstance(
        reporter,
        LoggingExceptionReporter,
    )


def test_alpha_environment_requires_better_stack_dsn():

    with pytest.raises(
        RuntimeError,
        match=(
            "BETTER_STACK_ERROR_DSN is required"
        ),
    ):

        build_exception_reporter(
            {},
            environment="alpha",
        )


def test_rejects_invalid_better_stack_dsn():

    with pytest.raises(
        ValueError,
        match="HTTPS application-token DSN",
    ):

        build_exception_reporter(
            {
                "BETTER_STACK_ERROR_DSN": (
                    "http://invalid.example.com"
                ),
            },
            environment="alpha",
        )


def test_disables_automatic_sdk_collection():

    sdk = FakeSdk()

    reporter = build_exception_reporter(
        {
            "BETTER_STACK_ERROR_DSN": (
                VALID_DSN
            ),
        },
        environment="alpha",
        sdk_module=sdk,
    )

    assert isinstance(
        reporter,
        BetterStackExceptionReporter,
    )

    assert sdk.init_options == {
        "dsn": VALID_DSN,
        "environment": "alpha",
        "release": "performancelab@0.1.0",
        "send_default_pii": False,
        "default_integrations": False,
        "max_breadcrumbs": 0,
        "attach_stacktrace": False,
        "traces_sample_rate": 0.0,
        "profiles_sample_rate": 0.0,
    }


def test_sends_only_sanitized_alert_metadata():

    sdk = FakeSdk()

    reporter = build_exception_reporter(
        {
            "BETTER_STACK_ERROR_DSN": (
                VALID_DSN
            ),
        },
        environment="alpha",
        sdk_module=sdk,
    )

    reporter.report(
        ExceptionAlert(
            operation="load_active_athlete",
            exception_type="RuntimeError",
            correlation_id=(
                "57c72fb9-4240-4a6b-"
                "9a61-2cb8116ef428"
            ),
        )
    )

    assert sdk.events == [
        {
            "message": (
                "performancelab_"
                "unhandled_exception"
            ),
            "level": "error",
            "tags": {
                "operation": (
                    "load_active_athlete"
                ),
                "exception_type": (
                    "RuntimeError"
                ),
                "correlation_id": (
                    "57c72fb9-4240-4a6b-"
                    "9a61-2cb8116ef428"
                ),
            },
        }
    ]

    serialized = repr(
        sdk.events
    )

    assert "email" not in serialized
    assert "password" not in serialized
    assert "traceback" not in serialized
    assert "physiological" not in serialized