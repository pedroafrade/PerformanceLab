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

        key = kwargs.get(
            "key"
        )

        if key in self.button_values:

            return self.button_values[
                key
            ]

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

    def rerun(self):

        self.rerun_called = True

    def dialog(
        self,
        title,
        **kwargs,
    ):

        self.messages.append(
            title
        )

        def decorator(function):

            return function

        return decorator


class FakeHistory:

    """
    Athlete history replacement.
    """

    def __init__(self):

        self.removed_workout = None
        self.removed_workouts = []
        self.sort_called = False

    def remove(
        self,
        workout,
    ):

        self.removed_workout = workout

    def remove_many(
        self,
        workouts,
    ):

        self.removed_workouts = list(
            workouts
        )

        return len(
            self.removed_workouts
        )

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
        estimated_rpe=None,
        effective_rpe=5,
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
            "workout_editor_delete_open": True,
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

    assert (
        "Delete workout"
        in fake_streamlit.messages
    )

    assert fake_streamlit.rerun_called is False


def test_confirm_delete_removes_workout(
    monkeypatch,
):

    fake_streamlit = FakeStreamlit(
        button_values={
            "workout_editor_delete_confirm": True,
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
        athlete.history.removed_workouts
        == [workout]
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
            "Save": True,
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
    
def test_automatic_rpe_is_preserved_when_not_overridden(
    monkeypatch,
):

    fake_streamlit = FakeStreamlit(
        button_values={
            "Save": True,
        },
        input_values={
            "Set RPE manually": False,
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

    workout.feedback.rpe = None
    workout.feedback.estimated_rpe = 6.0
    workout.feedback.effective_rpe = 6.0

    workout_editor.show_workout_editor(
        athlete,
        workout,
    )

    assert workout.feedback.rpe is None
    assert workout.feedback.estimated_rpe == 6.0

    assert (
        "Automatic RPE estimate: 6.0"
        in fake_streamlit.messages
    )


def test_automatic_rpe_can_be_overridden(
    monkeypatch,
):

    fake_streamlit = FakeStreamlit(
        button_values={
            "Save": True,
        },
        input_values={
            "Set RPE manually": True,
            "RPE": 8,
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

    workout.feedback.rpe = None
    workout.feedback.estimated_rpe = 6.0
    workout.feedback.effective_rpe = 6.0

    workout_editor.show_workout_editor(
        athlete,
        workout,
    )

    assert workout.feedback.rpe == 8
    assert workout.feedback.estimated_rpe == 6.0

def test_confirm_delete_removes_multiple_workouts(
    monkeypatch,
):

    fake_streamlit = FakeStreamlit(
        button_values={
            "multiple_delete_confirm": True,
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

    workout_1 = create_fake_workout()
    workout_2 = create_fake_workout()

    workout_editor.show_workout_delete_action(
        athlete,
        [
            workout_1,
            workout_2,
        ],
        key_prefix="multiple_delete",
    )

    assert (
        athlete.history.removed_workouts
        == [
            workout_1,
            workout_2,
        ]
    )

    assert (
        fake_streamlit
        .session_state
        .notice
        == "2 workouts deleted."
    )

    assert fake_streamlit.rerun_called is True