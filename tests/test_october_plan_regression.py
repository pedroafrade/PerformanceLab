"""Regression coverage for the October alpha report."""

import ast
from contextlib import contextmanager
from datetime import date
from functools import wraps
from pathlib import Path
from types import SimpleNamespace

import pytest

from performancelab import Athlete
from performancelab.coaching.context import CoachContext
from performancelab.coaching.strategies.peak import PeakStrategy
from performancelab.race.entry import EventEntry
from performancelab.race.event import Event
from performancelab.storage import athlete_from_dict, athlete_to_dict
from performancelab.training.planning.planner import Planner


def test_sao_silvestre_and_smat_share_horizon():
    athlete = Athlete(name="October regression")
    road = Event(name="São Silvestre", date=date(2026, 12, 26),
                 sport="Road Running", distance=10, elevation_gain=105)
    trail = Event(name="SMAT", date=date(2027, 1, 31),
                  sport="Trail Running", distance=35, elevation_gain=1820)
    athlete.events.add(EventEntry(event=road, priority="A"))
    athlete.events.add(EventEntry(event=trail, priority="A"))
    context = CoachContext.from_athlete(athlete, today=date(2026, 10, 1))
    assert context.primary_event_id == trail.event_id
    assert set(context.competition_event_ids) == {road.event_id, trail.event_id}
    plan = Planner().build_training_plan(athlete=athlete, today=date(2026, 10, 1))
    assert plan.primary_event_id == trail.event_id
    assert plan.end_date == date(2027, 2, 7)


@pytest.mark.parametrize("rpe", [5, 8])
def test_peak_does_not_invent_frequency_from_sparse_history(rpe):
    context = SimpleNamespace(
        tsb=0, average_rpe=rpe, next_event=None, phase_event=None,
        primary_event=None, days_until_phase_event=21,
        training_reference=SimpleNamespace(typical_weekly_sessions=1.25),
    )
    plan = PeakStrategy().build(context)
    assert plan.target_sessions == 1
    assert plan.intensity_sessions == 0
    assert plan.recovery_days >= 6


@pytest.mark.parametrize("fails", [False, True])
def test_plan_action_commits_only_on_success(fails):
    source = (Path(__file__).parents[1] / "app" / "app.py").read_text()
    tree = ast.parse(source)
    helper = next(node for node in tree.body
                  if isinstance(node, ast.FunctionDef)
                  and node.name == "committed_plan_action")
    events = []

    @contextmanager
    def transaction():
        events.append("begin")
        try:
            yield
        except Exception:
            events.append("rollback")
            raise
        else:
            events.append("commit")

    namespace = {"wraps": wraps, "repository_bundle": SimpleNamespace(
        rollback_pending_read_transaction=lambda: events.append("clear reads"),
        transaction=transaction,
    )}
    exec(compile(ast.Module(body=[helper], type_ignores=[]), "app.py", "exec"), namespace)

    @namespace["committed_plan_action"]
    def action():
        events.append("write")
        if fails:
            raise ValueError("generation failed")
        return "saved"

    if fails:
        with pytest.raises(ValueError):
            action()
    else:
        assert action() == "saved"
    assert events == ["clear reads", "begin", "write", "rollback" if fails else "commit"]


def test_all_plan_generation_calls_use_committing_helpers():
    source = (Path(__file__).parents[1] / "app" / "app.py").read_text()
    assert source.count("GenerateTrainingPlan(") == 1
    assert source.count("ApplyPlanBuilderDraft(") == 1
    for name in ("generate_persisted_plan", "apply_persisted_plan_draft"):
        assert "@committed_plan_action\ndef " + name in source


def test_declared_training_routine_has_priority_over_sparse_imports():
    athlete = Athlete(
        name="Sparse import",
        usual_weekly_sessions=4,
        usual_weekly_minutes=300,
    )
    context = CoachContext.from_athlete(athlete, today=date.today())

    assert context.weekly_sessions_reference == 4
    assert context.weekly_minutes_reference == 300
    assert context.training_reference_is_declared


def test_missing_routine_uses_conservative_floor_for_sparse_imports():
    athlete = Athlete(name="Sparse import")
    context = CoachContext.from_athlete(athlete, today=date.today())

    assert context.weekly_sessions_reference == 2
    assert context.weekly_minutes_reference == 120
    assert not context.training_reference_is_declared


def test_training_routine_round_trips_in_athlete_snapshot():
    athlete = Athlete(
        name="Routine",
        usual_weekly_sessions=5,
        usual_weekly_minutes=420,
    )

    restored = athlete_from_dict(athlete_to_dict(athlete))

    assert restored.usual_weekly_sessions == 5
    assert restored.usual_weekly_minutes == 420
