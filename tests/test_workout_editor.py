"""
Tests for the Streamlit workout editor component.
"""

from datetime import date, timedelta
from types import SimpleNamespace

import app.components.workout_editor as workout_editor


# ======================================================
# Test doubles
# ======================================================

class FakeSessionState(dict):

    """
    Dictionary with Streamlit-like attribute access.
    """

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

    """
    Context manager returned by st.columns().
    """

    def __enter__(self):

        return self

    def __exit__(
        self,
        exception_type,
        exception,
        traceback,
    ):

        return False


class FakeStreamlit:

    """
    Minimal Streamlit replacement used by unit tests.
    """

    def __init__(
        self,
        button_values=None,
        input_values=None,
    ):

        self.session_state = FakeSessionState()

        self.button_values = (
            button_values or {}
        )

        self.input_values = (
            input_values or {}
        )

        self.rerun_called = False
        self.messages = []

    def columns(
        self,
        count,
    ):

        return [
            FakeColumn()
            for _ in range(count)
        ]

    def button(
        self,
        label,
        **kwargs,
    ):

        return self.button_values.get(
            label,
            False,
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

    def divider(self):

        return None

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

    def success(
        self,
        message,
    ):

        self.messages.append(
            message
        )

    def rerun(self):

        self.rerun_called = True


class FakeHistory:

    """
    Athlete history replacement.
    """

    def __init__(self):

        self.removed_workout = None
        self.sort_called = False

    def remove(
        self,
        workout,
    ):

        self.removed_workout = workout

    def _sort(self):

        self.sort_called = True


def create_fake_workout():

    """
    Creates a workout-shaped object for component tests.
    """

    workout_info = SimpleNamespace(
        title="Easy Run",
        sport="Running",
        date=date(2026, 1, 10),
        distance=10.0,
        duration=timedelta(minutes=50),
        elevation_gain=120.0,
    )

    feedback = SimpleNamespace(
        rpe=5,
    )

    return SimpleNamespace(
        info=workout_info,
        feedback=feedback,
        sport="Running",
        date=workout_info.date,
        distance=workout_info.distance,
        duration=workout_info.duration,
        elevation_gain=workout_info.elevation_gain,
    )


def create_fake_athlete():

    return SimpleNamespace(
        history=FakeHistory(),
    )


# ======================================================
# Tests
# ======================================================

def test_initializes_session_state(
    monkeypatch,
):

    fake_streamlit = FakeStreamlit()

    monkeypatch.setattr(
        workout_editor,
        "st",
        fake_streamlit,
    )

    athlete = create_fake_athlete()
    workout = create_fake_workout()

    workout_editor.show_workout_editor(
        athlete,
        workout,
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


def test_delete_button_enables_confirmation(
    monkeypatch,
):

    fake_streamlit = FakeStreamlit(
        button_values={
            "🗑 Delete workout": True,
        },
    )

    monkeypatch.setattr(
        workout_editor,
        "st",
        fake_streamlit,
    )

    athlete = create_fake_athlete()
    workout = create_fake_workout()

    workout_editor.show_workout_editor(
        athlete,
        workout,
    )

    assert (
        fake_streamlit
        .session_state
        .confirm_delete
        is True
    )

    assert fake_streamlit.rerun_called is True


def test_confirm_delete_removes_workout(
    monkeypatch,
):

    fake_streamlit = FakeStreamlit(
        button_values={
            "✅ Delete": True,
        },
    )

    fake_streamlit.session_state.confirm_delete = True
    fake_streamlit.session_state.edit_workout = False

    monkeypatch.setattr(
        workout_editor,
        "st",
        fake_streamlit,
    )

    athlete = create_fake_athlete()
    workout = create_fake_workout()

    workout_editor.show_workout_editor(
        athlete,
        workout,
    )

    assert (
        athlete.history.removed_workout
        is workout
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
        .notice
        == "Workout deleted."
    )

    assert fake_streamlit.rerun_called is True


def test_save_updates_selected_workout(
    monkeypatch,
):

    fake_streamlit = FakeStreamlit(
        button_values={
            "💾 Save": True,
        },
        input_values={
            "Title": "Tempo Run",
            "Sport": "Running",
            "Date": date(2026, 1, 12),
            "Distance (km)": 12.5,
            "Hours": 1,
            "Minutes": 5,
            "Seconds": 30,
            "Elevation gain (m)": 250.0,
            "RPE": 7,
        },
    )

    fake_streamlit.session_state.confirm_delete = False
    fake_streamlit.session_state.edit_workout = True

    monkeypatch.setattr(
        workout_editor,
        "st",
        fake_streamlit,
    )

    athlete = create_fake_athlete()
    workout = create_fake_workout()

    workout_editor.show_workout_editor(
        athlete,
        workout,
    )

    assert workout.info.title == "Tempo Run"
    assert workout.info.sport == "Running"
    assert workout.info.date == date(2026, 1, 12)
    assert workout.info.distance == 12.5

    assert workout.info.duration == timedelta(
        hours=1,
        minutes=5,
        seconds=30,
    )

    assert workout.info.elevation_gain == 250.0
    assert workout.feedback.rpe == 7

    assert athlete.history.sort_called is True

    assert (
        fake_streamlit
        .session_state
        .edit_workout
        is False
    )

    assert (
        fake_streamlit
        .session_state
        .notice
        == "Workout updated."
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

    athlete = create_fake_athlete()

    workout_editor.show_workout_editor(
        athlete,
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