"""
PerformanceLab

Structured operational logging tests.
"""

from io import (
    StringIO,
)
import json
import logging

import pytest

from performancelab.operational_logging import (
    OperationalJsonFormatter,
    get_correlation_id,
    new_correlation_id,
    set_correlation_id,
)


def test_creates_and_binds_valid_correlation_id():

    correlation_id = new_correlation_id()

    assert (
        set_correlation_id(
            correlation_id
        )
        == correlation_id
    )

    assert (
        get_correlation_id()
        == correlation_id
    )


def test_rejects_invalid_correlation_id():

    with pytest.raises(
        ValueError,
        match="valid UUID",
    ):

        set_correlation_id(
            "user@example.com"
        )


def test_formats_operational_event_as_json():

    correlation_id = new_correlation_id()

    set_correlation_id(
        correlation_id
    )

    output = StringIO()

    handler = logging.StreamHandler(
        output
    )

    handler.setFormatter(
        OperationalJsonFormatter()
    )

    logger = logging.getLogger(
        "performancelab.test"
    )

    logger.handlers = [handler]
    logger.propagate = False
    logger.setLevel(logging.INFO)

    logger.info(
        "application_started"
    )

    payload = json.loads(
        output.getvalue()
    )

    assert (
        payload["event"]
        == "application_started"
    )

    assert (
        payload["correlation_id"]
        == correlation_id
    )

    assert payload["level"] == "INFO"

    assert (
        payload["logger"]
        == "performancelab.test"
    )

    assert "timestamp" in payload


def test_exception_log_excludes_exception_message():

    output = StringIO()

    handler = logging.StreamHandler(
        output
    )

    handler.setFormatter(
        OperationalJsonFormatter()
    )

    logger = logging.getLogger(
        "performancelab.exception_test"
    )

    logger.handlers = [handler]
    logger.propagate = False
    logger.setLevel(logging.ERROR)

    try:

        raise RuntimeError(
            "secret-token-and-private-payload"
        )

    except RuntimeError:

        logger.exception(
            "operation_failed"
        )

    payload = json.loads(
        output.getvalue()
    )

    assert (
        payload["event"]
        == "operation_failed"
    )

    assert (
        payload["exception_type"]
        == "RuntimeError"
    )

    serialized = json.dumps(
        payload
    )

    assert "secret-token" not in serialized
    assert "private-payload" not in serialized
    assert "Traceback" not in serialized