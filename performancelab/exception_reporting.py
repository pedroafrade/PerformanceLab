"""
PerformanceLab

Privacy-safe operational exception reporting.
"""

from dataclasses import (
    dataclass,
)
import logging
import re
from typing import (
    Protocol,
)

from performancelab.operational_logging import (
    get_correlation_id,
)


_LOGGER = logging.getLogger(
    "performancelab.exceptions"
)

_OPERATION_PATTERN = re.compile(
    r"^[a-z][a-z0-9_]*$"
)


@dataclass(
    frozen=True
)
class ExceptionAlert:
    """
    Safe metadata describing an application exception.

    Exception messages, tracebacks, payloads, emails and
    physiological data are deliberately excluded.
    """

    operation: str
    exception_type: str
    correlation_id: str


class ExceptionReporter(
    Protocol
):
    """
    Boundary for a future external alert provider.
    """

    def report(
        self,
        alert: ExceptionAlert,
    ) -> None:
        ...


class LoggingExceptionReporter:
    """
    Report safe exception metadata to operational logs.
    """

    def report(
        self,
        alert: ExceptionAlert,
    ) -> None:

        _LOGGER.error(
            (
                "unhandled_exception "
                "operation=%s "
                "exception_type=%s "
                "correlation_id=%s"
            ),
            alert.operation,
            alert.exception_type,
            alert.correlation_id,
        )


def capture_exception(
    error: BaseException,
    *,
    operation: str,
    reporter: ExceptionReporter | None = None,
) -> ExceptionAlert:
    """
    Capture only safe metadata for an exception.
    """

    if not isinstance(
        error,
        BaseException,
    ):

        raise TypeError(
            "error must be an exception."
        )

    if not isinstance(
        operation,
        str,
    ):

        raise TypeError(
            "operation must be a string."
        )

    normalized_operation = (
        operation.strip().lower()
    )

    if not _OPERATION_PATTERN.fullmatch(
        normalized_operation
    ):

        raise ValueError(
            "operation must contain only lowercase "
            "letters, numbers and underscores."
        )

    alert = ExceptionAlert(
        operation=normalized_operation,
        exception_type=(
            type(error).__name__
        ),
        correlation_id=(
            get_correlation_id()
        ),
    )

    active_reporter = (
        reporter
        if reporter is not None
        else LoggingExceptionReporter()
    )

    active_reporter.report(
        alert
    )

    return alert