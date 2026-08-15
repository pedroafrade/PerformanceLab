"""
Tests for the Streamlit workout editor component.
"""

from datetime import (
    date,
    datetime,
    timedelta,
    timezone,
)
from types import (
    SimpleNamespace,
)

import app.components.workout_editor as workout_editor


class FakeSessionState(
    dict
):

    def __getattr__(
        self,
        name,
    ):

        try:
            return self[name]

        except KeyError as error:
            raise AttributeError(
                name
            ) from error

    def __setattr__(
        self,
        name,
        value,
    ):

        self[name] = value


class FakeColumn:

    def __enter__(
        self,
    ):

        return self

    def __exit__(
        self,
        exception_type,
        exception,
        traceback,
    ):

        return False


class FakeStreamlit:

    def __init__(
        self,
        button_values=None,
        input_values=None,
    ):

        self.session_state = (
            FakeSessionState()
        )
        self.button_values = (
            button_values
            or {}
        )
        self.input_values = (
            input_values
            or {}
        )
        self.rerun_called = False
        self.messages = []

    def columns(
        self,
        count,
        **kwargs,
    ):

        return [
            FakeColumn()
            for _ in range(
                count
            )
        ]

    def button(
        self,
        label,
        **kwargs,
    ):

        key = kwargs.get(
            "key"
        )

        return self.button_values.get(
            key,
            self.button_values.get(
                label,
                False,
            ),
        )

    def text_input(
        self,
        label,
        value="",
        **kwargs,
    ):

        return self.input_values.get(
            label,
            value,
        )

    def selectbox(
        self,
        label,
        options,
        index=0,
        **kwargs,
    ):

        return self.input_values.get(
            label,
            options[index],
        )

    def date_input(
        self,
        label,
        value=None,
        **kwargs,
    ):

        return self.input_values.get(
            label,
            value,
        )

    def number_input(
        self,
        label,
        value=0,
        **kwargs,
    ):

        return self.input_values.get(
            label,
            value,
        )

    def slider(
        self,
        label,
        value=None,
        **kwargs,
    ):

        return self.input_values.get(
            label,
            value,
        )

    def checkbox(
        self,
        label,
        value=False,
        **kwargs,
    ):

        return self.input_values.get(
            label,
            value,
        )

    def subheader(
        self,
        message,
    ):

        self.messages.append(
            message
        )

    def warning(
        self,
        message,
    ):

        self.messages.append(
            message
        )

    def info(
        self,
        message,
    ):

        self.messages.append(
            message
        )

    def error(
        self,
        message,
    ):

        self.messages.append(
            message
        )

    def markdown(
        self,
        message,
        **kwargs,
    ):

        return None

    def container(
        self,
        **kwargs,
    ):

        return FakeColumn()

    def rerun(
        self,
    ):

        self.rerun_called = True

    def dialog(
        self,
        title,
        **kwargs,
    ):

        self.messages.append(
            title
        )

        def decorator(
            function,
        ):

            return function

        return decorator


def create_fake_workout():

    info = SimpleNamespace(
        title="Easy Run",
        sport="Running",
        date=date(
            2026,
            1,
            10,
        ),
        distance=10.0,
        duration=timedelta(
            minutes=50
        ),
        elevation_gain=120.0,
    )

    feedback = SimpleNamespace(
        rpe=5,
        estimated_rpe=None,
        effective_rpe=5,
    )

    return SimpleNamespace(
        workout_id="workout-1",
        info=info,
        feedback=feedback,
        sport=info.sport,
        date=info.date,
        distance=info.distance,
        duration=info.duration,
        elevation_gain=(
            info.elevation_gain
        ),
    )


def test_save_routes_update_through_callback(
    monkeypatch,
):

    fake_streamlit = FakeStreamlit(
        button_values={
            "Save": True,
        },
        input_values={
            "Title": "Tempo Run",
            "Date": date(
                2026,
                1,
                12,
            ),
            "Distance (km)": 12.5,
            "Hours": 1,
            "Minutes": 5,
            "Seconds": 30,
            "Elevation gain (m)": 250.0,
            "RPE": 7,
        },
    )

    fake_streamlit.session_state.edit_workout = True
    fake_streamlit.session_state.confirm_delete = False

    monkeypatch.setattr(
        workout_editor,
        "st",
        fake_streamlit,
    )

    calls = {}

    def on_update_workout(
        workout_id,
        update,
    ):

        calls["workout_id"] = (
            workout_id
        )
        calls["update"] = update

        return SimpleNamespace(
            changed=True
        )

    workout_editor.show_workout_editor(
        create_fake_workout(),
        on_update_workout=(
            on_update_workout
        ),
        on_delete_workouts=lambda ids: None,
    )

    assert (
        calls["workout_id"]
        == "workout-1"
    )
    assert (
        calls["update"].title
        == "Tempo Run"
    )
    assert (
        calls["update"].distance
        == 12.5
    )
    assert (
        calls["update"].duration
        == timedelta(
            hours=1,
            minutes=5,
            seconds=30,
        )
    )
    assert (
        calls["update"].rpe
        == 7.0
    )
    assert (
        fake_streamlit
        .session_state
        .persisted_notice
        == "Workout updated."
    )
    assert fake_streamlit.rerun_called is True


def test_edit_preserves_exact_workout_time(
    monkeypatch,
):

    workout = create_fake_workout()

    workout.info.date = datetime(
        2026,
        8,
        12,
        11,
        8,
        30,
        tzinfo=timezone.utc,
    )

    updated = (
        workout_editor._updated_workout_date(
            workout,
            date(
                2026,
                8,
                13,
            ),
        )
    )

    assert updated == datetime(
        2026,
        8,
        13,
        11,
        8,
        30,
        tzinfo=timezone.utc,
    )


def test_delete_routes_ids_through_callback(
    monkeypatch,
):

    fake_streamlit = FakeStreamlit(
        button_values={
            "delete_test_confirm": True,
        },
    )

    fake_streamlit.session_state.confirm_delete = True
    fake_streamlit.session_state.edit_workout = False

    monkeypatch.setattr(
        workout_editor,
        "st",
        fake_streamlit,
    )

    calls = {}

    def on_delete_workouts(
        workout_ids,
    ):

        calls["workout_ids"] = (
            workout_ids
        )

        return SimpleNamespace(
            removed_count=1
        )

    workout_editor.show_workout_delete_action(
        create_fake_workout(),
        on_delete_workouts=(
            on_delete_workouts
        ),
        key_prefix="delete_test",
    )

    assert calls["workout_ids"] == (
        "workout-1",
    )
    assert (
        fake_streamlit
        .session_state
        .persisted_notice
        == "Workout deleted."
    )
    assert fake_streamlit.rerun_called is True


def test_no_workout_closes_editor_state(
    monkeypatch,
):

    fake_streamlit = FakeStreamlit()

    fake_streamlit.session_state.confirm_delete = True
    fake_streamlit.session_state.edit_workout = True

    monkeypatch.setattr(
        workout_editor,
        "st",
        fake_streamlit,
    )

    workout_editor.show_workout_editor(
        None,
    )

    assert (
        fake_streamlit
        .session_state
        .confirm_delete
        is False
    )
    assert (
        fake_streamlit
        .session_state
        .edit_workout
        is False
    )