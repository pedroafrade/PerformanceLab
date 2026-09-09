from pathlib import Path


EVENT_MANAGER_PATH = (
    Path(__file__).resolve().parents[1]
    / "app"
    / "components"
    / "dashboard"
    / "event_manager.py"
)


def test_event_deletion_requests_plan_regeneration():
    source = EVENT_MANAGER_PATH.read_text(encoding="utf-8")
    delete_body = source.split("def _delete_event(", 1)[1].split(
        "def _confirm_delete_event", 1
    )[0]
    assert "athlete.events.remove" in delete_body
    assert "event_plan_refresh_requested" in delete_body


def test_event_addition_and_edit_request_plan_regeneration():
    source = EVENT_MANAGER_PATH.read_text(encoding="utf-8")
    form_body = source.split("def _show_add_event_form(", 1)[1]
    assert "athlete.events._sort()" in form_body
    assert "athlete.events.add" in form_body
    assert "event_plan_refresh_requested" in form_body


def test_event_deletion_confirmation_uses_popup():
    source = EVENT_MANAGER_PATH.read_text(encoding="utf-8")
    assert 'with st.popover(' in source
    assert 'f\'Delete "{event.name}"?\'' in source
    assert 'st.warning("Delete this event?")' not in source
