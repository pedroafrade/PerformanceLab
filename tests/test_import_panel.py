from datetime import date, datetime, timedelta
from gzip import compress

from types import SimpleNamespace

import app.components.import_panel as import_panel

from performancelab import History, Workout
from performancelab.analysis.training_state import (
    TrainingState,
)
from performancelab.training.planning import (
    PlannedWorkout,
    TrainingPlan,
)


def test_import_panel_uses_athlete_profile_for_rpe(
    monkeypatch,
):

    calls = {}

    def fake_estimator(
        workout,
        *,
        max_hr,
        resting_hr,
    ):

        calls["workout"] = workout
        calls["max_hr"] = max_hr
        calls["resting_hr"] = resting_hr

        return 6.0

    monkeypatch.setattr(
        import_panel,
        "estimate_workout_rpe",
        fake_estimator,
    )

    workout = object()

    athlete = SimpleNamespace(
        max_hr=190,
        resting_hr=50,
    )

    estimate = (
        import_panel._estimate_imported_workout_rpe(
            workout,
            athlete,
        )
    )

    assert estimate == 6.0
    assert calls["workout"] is workout
    assert calls["max_hr"] == 190
    assert calls["resting_hr"] == 50

def test_import_panel_merges_workout_into_history():

    workout = object()
    stored_workout = object()

    calls = {}

    class FakeHistory:

        def merge(
            self,
            received_workout,
        ):

            calls["workout"] = (
                received_workout
            )

            return (
                stored_workout,
                False,
            )

    athlete = SimpleNamespace(
        history=FakeHistory(),
    )

    added = (
        import_panel._store_imported_workout(
            workout,
            athlete,
        )
    )

    assert calls["workout"] is workout
    assert added is False

def test_imports_multiple_files_and_counts_results(
    monkeypatch,
):

    new_file = SimpleNamespace(
        name="new.fit"
    )

    existing_file = SimpleNamespace(
        name="existing.fit"
    )

    failed_file = SimpleNamespace(
        name="failed.fit"
    )

    def fake_import(
        uploaded_file,
        athlete,
        strava_titles=None,
    ):

        if uploaded_file is new_file:
            return (
                True,
                date(
                    2026,
                    8,
                    1,
                ),
            )

        if uploaded_file is existing_file:
            return (
                False,
                date(
                    2026,
                    8,
                    2,
                ),
            )

        raise ValueError(
            "Invalid activity"
        )
    monkeypatch.setattr(
        import_panel,
        "_import_uploaded_file",
        fake_import,
    )
    reconciled = {}

    def fake_reconcile(
        athlete,
        *,
        through_day,
    ):

        reconciled["athlete"] = athlete
        reconciled["through_day"] = (
            through_day
        )

    monkeypatch.setattr(
        import_panel,
        "_reconcile_training_plan",
        fake_reconcile,
    )
    counts = (
        import_panel._import_uploaded_files(
            [
                new_file,
                existing_file,
                failed_file,
            ],
            SimpleNamespace(),
        )
    )

    assert counts == (
        1,
        1,
        1,
    )
    assert (
        reconciled["through_day"]
        == date(
            2026,
            8,
            2,
        )
    )
def test_prepares_compressed_fit_upload():

    uploaded_file = SimpleNamespace(
        name="strava_activity.fit.gz",
        getvalue=lambda: compress(
            b"FIT activity data"
        ),
    )

    source, extension = (
        import_panel._prepare_uploaded_file(
            uploaded_file
        )
    )

    assert extension == "fit"
    assert source.name == (
        "strava_activity.fit"
    )
    assert source.read() == (
        b"FIT activity data"
    )

def test_reads_strava_activity_titles():

    csv_file = SimpleNamespace(
        name="activities.csv",
        getvalue=lambda: (
            (
                '"Nome da atividade","Nome do ficheiro"\n'
                '"T68- 6x20 + Z2 (pt 2)",'
                '"activities\\20284257187.fit.gz"\n'
            ).encode("utf-8")
        ),
    )

    titles = (
        import_panel._read_strava_titles(
            [csv_file]
        )
    )

    assert titles == {
        "20284257187.fit.gz": (
            "T68- 6x20 + Z2 (pt 2)"
        )
    }


def test_uses_strava_activity_title():

    uploaded_file = SimpleNamespace(
        name="20284257187.fit.gz",
    )

    title = import_panel._activity_title(
        uploaded_file,
        {
            "20284257187.fit.gz": (
                "Morning Run"
            ),
        },
    )

    assert title == "Morning Run"

def test_reconciliation_updates_athlete_plan(
    monkeypatch,
):

    original_plan = object()
    adapted_plan = object()
    history = object()
    training_state = object()

    athlete = SimpleNamespace(
        training_plan=original_plan,
        history=history,
        analytics=SimpleNamespace(
            training_state=training_state,
        ),
    )

    calls = {}

    class FakeReconciler:

        def reconcile(
            self,
            *,
            plan,
            history,
            training_state,
            through_day,
        ):

            calls["plan"] = plan
            calls["history"] = history
            calls["training_state"] = (
                training_state
            )
            calls["through_day"] = (
                through_day
            )

            return adapted_plan

    monkeypatch.setattr(
        import_panel,
        "TrainingPlanReconciler",
        FakeReconciler,
    )

    import_panel._reconcile_training_plan(
        athlete,
        through_day=date(
            2026,
            8,
            2,
        ),
    )

    assert calls["plan"] is original_plan
    assert calls["history"] is history

    assert (
        calls["training_state"]
        is training_state
    )

    assert (
        calls["through_day"]
        == date(
            2026,
            8,
            2,
        )
    )

    assert (
        athlete.training_plan
        is adapted_plan
    )

def test_imported_activity_adapts_athlete_plan():

    plan = TrainingPlan(
        plan_id="import-flow-plan",
        start_date=date(
            2026,
            8,
            1,
        ),
        end_date=date(
            2026,
            8,
            31,
        ),
        workouts=[
            PlannedWorkout(
                scheduled_at=datetime(
                    2026,
                    8,
                    4,
                    8,
                    0,
                ),
                sport="Running",
                title="Easy Run",
                duration=timedelta(
                    minutes=60,
                ),
                intensity="Easy",
            ),
            PlannedWorkout(
                scheduled_at=datetime(
                    2026,
                    8,
                    6,
                    8,
                    0,
                ),
                sport="Running",
                title="Tempo Run",
                duration=timedelta(
                    minutes=50,
                ),
                intensity="Tempo",
            ),
        ],
    )

    training_state = TrainingState(
        ctl=40.0,
        atl=65.0,
        tsb=-25.0,
        acute_chronic_ratio=1.4,
        monotony=1.0,
        strain=650.0,
        consistency=0.8,
        weekly_frequency=4.0,
        days_since_last_workout=0,
        recent_training_load=500.0,
    )

    athlete = SimpleNamespace(
        training_plan=plan,
        history=History(),
        analytics=SimpleNamespace(
            training_state=training_state,
        ),
    )

    completed = Workout(
        workout_id="imported-overload",
    )

    completed.info.date = datetime(
        2026,
        8,
        4,
        9,
        0,
    )

    completed.info.sport = "Running"

    completed.info.duration = timedelta(
        minutes=90,
    )

    completed.feedback.rpe = 4

    added = (
        import_panel._store_imported_workout(
            completed,
            athlete,
        )
    )

    import_panel._reconcile_training_plan(
        athlete,
        through_day=date(
            2026,
            8,
            4,
        ),
    )

    assert added is True

    assert (
        len(athlete.history)
        == 1
    )

    assert (
        athlete.training_plan.workouts[0].duration
        == timedelta(minutes=60)
    )

    assert (
        athlete.training_plan.workouts[1].duration
        == timedelta(minutes=40)
    )

    assert (
        athlete.training_plan.reconciled_through
        == date(
            2026,
            8,
            4,
        )
    )

    assert (
        athlete.training_plan
        .reconciled_workout_ids
        == (
            "imported-overload",
        )
    )



def test_repairs_imported_strava_title():

    uploaded_file = SimpleNamespace(
        name="activity.fit",
    )

    title = import_panel._activity_title(
        uploaded_file,
        {
            "activity.fit": (
                "T75_RecuperaÃ§Ã£o"
            ),
        },
    )

    assert title == (
        "T75_Recuperação"
    )