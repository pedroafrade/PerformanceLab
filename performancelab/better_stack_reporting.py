"""
PerformanceLab

Privacy-safe Better Stack exception reporting.
"""

from collections.abc import (
    Mapping,
)
from urllib.parse import (
    urlsplit,
)

import sentry_sdk

from performancelab.exception_reporting import (
    ExceptionAlert,
    ExceptionReporter,
    LoggingExceptionReporter,
)


BETTER_STACK_ERROR_DSN_SETTING = (
    "BETTER_STACK_ERROR_DSN"
)


class BetterStackExceptionReporter:
    """
    Send only sanitized ExceptionAlert metadata.

    The original exception, message, traceback, user,
    request, breadcrumbs and physiological data are never
    provided to the SDK.
    """

    def __init__(
        self,
        *,
        dsn: str,
        environment: str,
        sdk_module=sentry_sdk,
    ) -> None:

        self._sdk = sdk_module

        self._sdk.init(
            dsn=_validated_dsn(dsn),
            environment=environment,
            release="performancelab@0.1.0",
            send_default_pii=False,
            default_integrations=False,
            max_breadcrumbs=0,
            attach_stacktrace=False,
            traces_sample_rate=0.0,
            profiles_sample_rate=0.0,
        )

    def report(
        self,
        alert: ExceptionAlert,
    ) -> None:

        if not isinstance(
            alert,
            ExceptionAlert,
        ):

            raise TypeError(
                "alert must be an ExceptionAlert."
            )

        self._sdk.capture_event(
            {
                "message": (
                    "performancelab_unhandled_exception"
                ),
                "level": "error",
                "tags": {
                    "operation": alert.operation,
                    "exception_type": (
                        alert.exception_type
                    ),
                    "correlation_id": (
                        alert.correlation_id
                    ),
                },
            }
        )


def build_exception_reporter(
    values: Mapping[str, object],
    *,
    environment: str,
    sdk_module=sentry_sdk,
) -> ExceptionReporter:
    """
    Build local logging or Better Stack reporting.

    Better Stack is mandatory in the alpha environment but
    remains optional during local development and tests.
    """

    if not isinstance(
        values,
        Mapping,
    ):

        raise TypeError(
            "values must be a mapping."
        )

    normalized_environment = (
        environment.strip().lower()
        if isinstance(environment, str)
        else environment
    )

    configured_dsn = values.get(
        BETTER_STACK_ERROR_DSN_SETTING
    )

    dsn = (
        configured_dsn.strip()
        if isinstance(configured_dsn, str)
        and configured_dsn.strip()
        else None
    )

    if (
        configured_dsn is not None
        and not isinstance(
            configured_dsn,
            str,
        )
    ):

        raise TypeError(
            "BETTER_STACK_ERROR_DSN must be "
            "a string or None."
        )

    if dsn is None:

        if normalized_environment == "alpha":

            raise RuntimeError(
                "BETTER_STACK_ERROR_DSN is required "
                "in the alpha environment."
            )

        return LoggingExceptionReporter()

    return BetterStackExceptionReporter(
        dsn=dsn,
        environment=normalized_environment,
        sdk_module=sdk_module,
    )


def _validated_dsn(
    dsn: str,
) -> str:
    """
    Validate the Better Stack Sentry-compatible DSN.
    """

    if not isinstance(
        dsn,
        str,
    ):

        raise TypeError(
            "BETTER_STACK_ERROR_DSN must be a string."
        )

    normalized_dsn = dsn.strip()
    parsed = urlsplit(
        normalized_dsn
    )

    if (
        parsed.scheme != "https"
        or not parsed.username
        or parsed.password is not None
        or not parsed.hostname
        or not parsed.path.strip("/")
        or parsed.query
        or parsed.fragment
    ):

        raise ValueError(
            "BETTER_STACK_ERROR_DSN must use the "
            "HTTPS application-token DSN supplied "
            "by Better Stack."
        )

    return normalized_dsn