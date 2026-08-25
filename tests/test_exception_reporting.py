"""
PerformanceLab

Privacy-safe exception reporting tests.
"""

from pathlib import Path
import logging

import pytest

from performancelab.exception_reporting import (
    ExceptionAlert,
    capture_exception,
)
from performancelab.operational_logging import (
    new_correlation_id,
    set_correlation_id,
)


APP_PATH = (
    Path(__file__).parents[1]
    / "app"
    / "app.py"
)


class RecordingReporter:

    def __init__(self):

        self.alerts = []

    def report(
        self,
        alert,
    ):

        self.alerts.append(
            alert
        )


def test_captures_only_safe_exception_metadata():

    correlation_id = new_correlation_id()

    set_correlation_id(
        correlation_id
    )

    reporter = RecordingReporter()

    alert = capture_exception(
        RuntimeError(
            "private@example.com secret-password"
        ),
        operation="load_active_athlete",
        reporter=reporter,
    )

    assert alert == ExceptionAlert(
        operation="load_active_athlete",
        exception_type="RuntimeError",
        correlation_id=correlation_id,
    )

    assert reporter.alerts == [
        alert,
    ]

    assert not hasattr(
        alert,
        "message",
    )

    assert not hasattr(
        alert,
        "traceback",
    )


def test_default_report_excludes_exception_message(
    caplog,
):

    set_correlation_id(
        new_correlation_id()
    )

    caplog.set_level(
        logging.ERROR,
        logger=(
            "performancelab.exceptions"
        ),
    )

    capture_exception(
        RuntimeError(
            "database-password private@example.com"
        ),
        operation="repository_failure",
    )

    assert "unhandled_exception" in caplog.text
    assert "repository_failure" in caplog.text
    assert "RuntimeError" in caplog.text

    assert "database-password" not in caplog.text
    assert "private@example.com" not in caplog.text
    assert "Traceback" not in caplog.text


def test_rejects_operation_that_could_contain_private_data():

    with pytest.raises(
        ValueError,
        match="lowercase",
    ):

        capture_exception(
            RuntimeError(),
            operation=(
                "load-user@example.com"
            ),
        )


def test_app_reports_critical_exceptions_safely():

    text = APP_PATH.read_text(
        encoding="utf-8",
    )

    assert (
        'operation=(\n'
        '                "generate_training_plan"\n'
        '            )'
        in text
    )

    assert (
        'operation=(\n'
        '                "load_active_athlete"\n'
        '            )'
        in text
    )

    assert "st.exception(error)" not in text