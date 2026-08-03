"""
Tests for the reusable activity input component.
"""

from types import SimpleNamespace

import app.components.activity_input as activity_input


def test_file_input_uses_key_prefix(
    monkeypatch,
):

    calls = {}

    monkeypatch.setattr(
        activity_input.st,
        "header",
        lambda value: calls.update(
            header=value
        ),
    )

    def fake_segmented_control(
        label,
        *,
        options,
        default,
        label_visibility,
        key,
    ):

        calls["segmented_key"] = key

        return "File"

    monkeypatch.setattr(
        activity_input.st,
        "segmented_control",
        fake_segmented_control,
    )

    def fake_import_panel(
        athlete,
        *,
        key_prefix,
    ):

        calls["athlete"] = athlete
        calls["import_key_prefix"] = (
            key_prefix
        )

    monkeypatch.setattr(
        activity_input,
        "show_import_panel",
        fake_import_panel,
    )

    athlete = SimpleNamespace()

    result = (
        activity_input.show_activity_input(
            athlete,
            key_prefix="activities_page",
        )
    )

    assert result is athlete
    assert calls["header"] == (
        "Add activity"
    )
    assert calls["segmented_key"] == (
        "activities_page_input_mode"
    )
    assert calls["import_key_prefix"] == (
        "activities_page"
    )
    assert calls["athlete"] is athlete


def test_manual_input_uses_key_prefix(
    monkeypatch,
):

    calls = {}

    monkeypatch.setattr(
        activity_input.st,
        "header",
        lambda value: calls.update(
            header=value
        ),
    )

    monkeypatch.setattr(
        activity_input.st,
        "segmented_control",
        lambda *args, **kwargs: (
            "Manual"
        ),
    )

    def fake_manual_form(
        athlete,
        *,
        key_prefix,
    ):

        calls["athlete"] = athlete
        calls["manual_key_prefix"] = (
            key_prefix
        )

    monkeypatch.setattr(
        activity_input,
        "show_manual_workout_form",
        fake_manual_form,
    )

    athlete = SimpleNamespace()

    activity_input.show_activity_input(
        athlete,
        key_prefix="manual_test",
    )

    assert calls["manual_key_prefix"] == (
        "manual_test"
    )
    assert calls["athlete"] is athlete


def test_can_hide_activity_input_header(
    monkeypatch,
):

    calls = {
        "header_count": 0,
    }

    def fake_header(value):

        calls["header_count"] += 1

    monkeypatch.setattr(
        activity_input.st,
        "header",
        fake_header,
    )

    monkeypatch.setattr(
        activity_input.st,
        "segmented_control",
        lambda *args, **kwargs: None,
    )

    athlete = SimpleNamespace()

    activity_input.show_activity_input(
        athlete,
        key_prefix="hidden_header",
        show_header=False,
    )

    assert calls["header_count"] == 0