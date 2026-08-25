"""
PerformanceLab

Structured privacy-safe operational logging.
"""

from contextvars import (
    ContextVar,
)
from datetime import (
    datetime,
    timezone,
)
import json
import logging
import sys
from uuid import (
    UUID,
    uuid4,
)


_CORRELATION_ID = ContextVar(
    "performancelab_correlation_id",
    default="unbound",
)


class OperationalJsonFormatter(
    logging.Formatter
):
    """
    Format operational records as one JSON object per line.

    Exception messages and tracebacks are deliberately
    excluded because they may contain personal data,
    credentials or provider payloads.
    """

    def format(
        self,
        record: logging.LogRecord,
    ) -> str:

        payload = {
            "timestamp": (
                datetime.now(timezone.utc)
                .isoformat()
            ),
            "level": record.levelname,
            "logger": record.name,
            "event": record.getMessage(),
            "correlation_id": (
                _CORRELATION_ID.get()
            ),
        }

        if record.exc_info:

            exception_type = (
                record.exc_info[0]
            )

            payload["exception_type"] = (
                exception_type.__name__
                if exception_type is not None
                else "UnknownException"
            )

        return json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
        )


def new_correlation_id() -> str:
    """
    Create an opaque identifier for one application session.
    """

    return str(uuid4())


def set_correlation_id(
    correlation_id: str,
) -> str:
    """
    Validate and bind a correlation identifier.
    """

    if not isinstance(
        correlation_id,
        str,
    ):

        raise TypeError(
            "correlation_id must be a string."
        )

    normalized_value = (
        correlation_id.strip()
    )

    try:

        normalized_uuid = str(
            UUID(normalized_value)
        )

    except (
        ValueError,
        AttributeError,
    ) as error:

        raise ValueError(
            "correlation_id must be a valid UUID."
        ) from error

    _CORRELATION_ID.set(
        normalized_uuid
    )

    return normalized_uuid


def get_correlation_id() -> str:
    """
    Return the correlation identifier for this context.
    """

    return _CORRELATION_ID.get()


def configure_operational_logging(
    *,
    stream=None,
) -> logging.Logger:
    """
    Configure the PerformanceLab logger once.

    Existing handlers not created by this function are
    preserved.
    """

    logger = logging.getLogger(
        "performancelab"
    )

    for handler in logger.handlers:

        if getattr(
            handler,
            "_performancelab_operational",
            False,
        ):

            return logger

    handler = logging.StreamHandler(
        stream
        if stream is not None
        else sys.stdout
    )

    handler.setFormatter(
        OperationalJsonFormatter()
    )

    handler._performancelab_operational = True

    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    return logger