"""
Tests for the complete PlanPresenter.
"""

from dataclasses import FrozenInstanceError
from datetime import date, datetime, timedelta

import pytest

from performancelab.history import (
    History,
)
from performancelab.presentation import (
    PlanAdaptationData,
    PlanChartPointData,
    PlanCurrentPhaseData,
    PlanPhaseData,
    PlanPresenter,
    PlanProgressionPointData,
)
from performancelab.training.planning import (
    PlannedWorkout,
    TrainingPlan,
    TrainingPlanAdaptation,
    WorkoutOutcomeStatus,
)
from performancelab.workout import (
    Workout,
)


def planned_workout(
    *,
    day: int,
    title: str,
    intensity: str,
    duration_minutes: int,
    phase: str,
) -> PlannedWorkout:

    return PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            day,
            8,
            0,
        ),
        sport="Running",
        title=title,
        duration=timedelta(
            minutes=duration_minutes,
        ),
        intensity=intensity,
        phase=phase,
    )


def test_groups_complete_plan_by_week():

    first = planned_workout(
        day=4,
        title="Easy Run",
        intensity="Easy",
        duration_minutes=60,
        phase="Build",
    )

    second = planned_workout(
        day=6,
        title="LT2 Run",
        intensity="Hard",
        duration_minutes=45,
        phase="Build",
    )

    third = planned_workout(
        day=11,
        title="Hill Run",
        intensity="Hard",
        duration_minutes=60,
        phase="Peak",
    )

    plan = TrainingPlan(
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
            first,
            second,
            third,
        ],
    )

    result = PlanPresenter(
        plan=plan,
        history=History(),
    ).build(
        reference_day=date(
            2026,
            8,
            3,
        )
    )

    assert len(result.weeks) == 2

    assert (
        result.weeks[0].start_date
        == date(2026, 8, 3)
    )

    assert tuple(
        workout.title
        for workout in (
            result.weeks[0].workouts
        )
    ) == (
        "Easy Run",
        "LT2 Run",
    )

    assert (
        result.weeks[0].planned_load
        == pytest.approx(495)
    )

    assert (
        result.weeks[0]
        .workouts[0]
        .planned_load
        == pytest.approx(180)
    )

    assert (
        result.weeks[0]
        .workouts[1]
        .planned_load
        == pytest.approx(315)
    )

    assert not (
        result.weeks[0]
        .workouts[0]
        .is_race
    )

    assert not (
        result.weeks[0]
        .workouts[1]
        .is_race
    )

    assert (
        result.weeks[1].phase
        == "Peak"
    )


def test_attaches_workout_outcomes():

    completed = Workout(
        workout_id="completed-easy"
    )
    completed.info.date = date(
        2026,
        8,
        4,
    )
    completed.info.sport = "Running"
    completed.info.duration = timedelta(
        minutes=60,
    )
    completed.feedback.rpe = 3

    equivalent = planned_workout(
        day=4,
        title="Easy Run",
        intensity="Easy",
        duration_minutes=60,
        phase="Build",
    )

    pending = planned_workout(
        day=6,
        title="LT2 Run",
        intensity="Hard",
        duration_minutes=45,
        phase="Build",
    )

    result = PlanPresenter(
        plan=TrainingPlan(
            workouts=[
                equivalent,
                pending,
            ]
        ),
        history=History(
            workouts=[
                completed,
            ]
        ),
    ).build(
        reference_day=date(
            2026,
            8,
            5,
        )
    )

    assert tuple(
        workout.status
        for workout in (
            result.weeks[0].workouts
        )
    ) == (
        "equivalent",
        "pending",
    )


def test_marks_past_session_as_missed():

    missed = planned_workout(
        day=4,
        title="Easy Run",
        intensity="Easy",
        duration_minutes=60,
        phase="Build",
    )

    result = PlanPresenter(
        plan=TrainingPlan(
            workouts=[
                missed,
            ]
        ),
        history=History(),
    ).build(
        reference_day=date(
            2026,
            8,
            5,
        )
    )

    assert (
        result.weeks[0]
        .workouts[0]
        .status
        == "missed"
    )


def test_empty_plan_has_no_weeks():

    result = PlanPresenter(
        plan=TrainingPlan(),
        history=History(),
    ).build(
        reference_day=date(
            2026,
            8,
            3,
        )
    )

    assert result.weeks == ()
    assert result.progression == ()


def test_complete_plan_data_is_immutable():

    result = PlanPresenter(
        plan=TrainingPlan(),
        history=History(),
    ).build(
        reference_day=date(
            2026,
            8,
            3,
        )
    )

    with pytest.raises(
        FrozenInstanceError
    ):
        result.weeks = ()

def test_builds_immutable_plan_progression():

    first = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            4,
            8,
            0,
        ),
        sport="Trail Running",
        title="Easy Run",
        duration=timedelta(
            minutes=60,
        ),
        distance=10.0,
        elevation_gain=200.0,
        intensity="Easy",
        phase="Build",
    )

    second = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            6,
            8,
            0,
        ),
        sport="Trail Running",
        title="Long Run",
        duration=timedelta(
            minutes=90,
        ),
        distance=15.0,
        elevation_gain=400.0,
        intensity="Easy to moderate",
        phase="Build",
    )

    result = PlanPresenter(
        plan=TrainingPlan(
            workouts=[
                first,
                second,
            ]
        ),
        history=History(),
    ).build(
        reference_day=date(
            2026,
            8,
            3,
        )
    )

    assert len(
        result.progression
    ) == 1

    point = result.progression[0]

    assert isinstance(
        point,
        PlanProgressionPointData,
    )
    assert (
        point.week_start
        == date(2026, 8, 3)
    )
    assert point.phase == "Build"
    assert (
        point.duration_minutes
        == pytest.approx(150.0)
    )
    assert (
        point.distance
        == pytest.approx(25.0)
    )
    assert (
        point.elevation_gain
        == pytest.approx(600.0)
    )
    assert (
        point.planned_load
        > 0
    )

    with pytest.raises(
        FrozenInstanceError
    ):
        point.distance = 30.0

def test_marks_race_session_for_presentation():

    race = planned_workout(
        day=13,
        title="Race",
        intensity="Race effort",
        duration_minutes=120,
        phase="Race",
    )

    result = PlanPresenter(
        plan=TrainingPlan(
            workouts=[
                race,
            ]
        ),
        history=History(),
    ).build(
        reference_day=date(
            2026,
            8,
            3,
        )
    )

    assert (
        result.weeks[0]
        .workouts[0]
        .is_race
    )

def test_exposes_current_plan_phase():

    build_week = (
        planned_workout(
            day=4,
            title="Easy Run",
            intensity="Easy",
            duration_minutes=60,
            phase="Build",
        )
    )

    peak_week_one = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            11,
            8,
            0,
        ),
        sport="Running",
        title="LT2 Run",
        duration=timedelta(
            minutes=45,
        ),
        intensity="Hard",
        phase="Peak",
    )

    peak_week_two = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            18,
            8,
            0,
        ),
        sport="Running",
        title="Long Run",
        duration=timedelta(
            minutes=90,
        ),
        intensity="Easy to moderate",
        phase="Peak",
    )

    taper_week = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            25,
            8,
            0,
        ),
        sport="Running",
        title="Pre-Race Run",
        duration=timedelta(
            minutes=40,
        ),
        intensity="Easy",
        phase="Taper",
    )

    result = PlanPresenter(
        plan=TrainingPlan(
            workouts=[
                build_week,
                peak_week_one,
                peak_week_two,
                taper_week,
            ]
        ),
        history=History(),
    ).build(
        reference_day=date(
            2026,
            8,
            12,
        )
    )

    assert isinstance(
        result.current_phase,
        PlanCurrentPhaseData,
    )

    assert (
        result.current_phase.name
        == "Peak"
    )
    assert (
        result.current_phase.objective
        == (
            "Increase race-specific endurance "
            "and key-session quality."
        )
    )

    assert (
        result.current_phase.start_date
        == date(2026, 8, 10)
    )

    assert (
        result.current_phase.end_date
        == date(2026, 8, 23)
    )

    assert (
        result.current_phase.weeks_remaining
        == 2
    )
    assert (
        result.current_phase.sessions_remaining
        == 1
    )

    assert (
        result.current_phase
        .planned_load_remaining
        > 0
    )

    assert (
        result.current_phase
        .longest_session_minutes
        == 90
    )

def test_has_no_current_phase_outside_plan():

    workout = planned_workout(
        day=4,
        title="Easy Run",
        intensity="Easy",
        duration_minutes=60,
        phase="Build",
    )

    result = PlanPresenter(
        plan=TrainingPlan(
            workouts=[
                workout,
            ]
        ),
        history=History(),
    ).build(
        reference_day=date(
            2026,
            8,
            20,
        )
    )

    assert result.current_phase is None

def test_provides_objective_for_each_plan_phase():

    expected_objectives = {
        "Build": (
            "Develop sustainable training volume "
            "and aerobic durability."
        ),
        "Peak": (
            "Increase race-specific endurance "
            "and key-session quality."
        ),
        "Taper": (
            "Reduce fatigue while preserving "
            "race readiness."
        ),
        "Race": (
            "Execute the target event with "
            "freshness and specificity."
        ),
        "Transition": (
            "Recover from racing while maintaining "
            "gentle movement."
        ),
        "Regeneration": (
            "Restore physical and mental freshness "
            "before rebuilding."
        ),
    }

    for phase_name, expected in (
        expected_objectives.items()
    ):

        assert (
            PlanPresenter._phase_objective(
                phase_name
            )
            == expected
        )


def test_provides_fallback_phase_objective():

    assert (
        PlanPresenter._phase_objective(
            "Unassigned"
        )
        == (
            "Follow the planned sessions for "
            "the current phase."
        )
    )

def test_exposes_complete_phase_timeline():

    build = planned_workout(
        day=4,
        title="Easy Run",
        intensity="Easy",
        duration_minutes=60,
        phase="Build",
    )

    peak_one = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            11,
            8,
            0,
        ),
        sport="Running",
        title="LT2 Run",
        duration=timedelta(
            minutes=45,
        ),
        intensity="Hard",
        phase="Peak",
    )

    peak_two = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            18,
            8,
            0,
        ),
        sport="Running",
        title="Long Run",
        duration=timedelta(
            minutes=90,
        ),
        intensity="Easy to moderate",
        phase="Peak",
    )

    taper = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            25,
            8,
            0,
        ),
        sport="Running",
        title="Pre-Race Run",
        duration=timedelta(
            minutes=40,
        ),
        intensity="Easy",
        phase="Taper",
    )

    result = PlanPresenter(
        plan=TrainingPlan(
            workouts=[
                build,
                peak_one,
                peak_two,
                taper,
            ]
        ),
        history=History(),
    ).build(
        reference_day=date(
            2026,
            8,
            12,
        )
    )

    assert result.phases == (
        PlanPhaseData(
            name="Build",
            start_date=date(
                2026,
                8,
                3,
            ),
            end_date=date(
                2026,
                8,
                9,
            ),
            is_current=False,
        ),
        PlanPhaseData(
            name="Peak",
            start_date=date(
                2026,
                8,
                10,
            ),
            end_date=date(
                2026,
                8,
                23,
            ),
            is_current=True,
        ),
        PlanPhaseData(
            name="Taper",
            start_date=date(
                2026,
                8,
                24,
            ),
            end_date=date(
                2026,
                8,
                30,
            ),
            is_current=False,
        ),
    )


def test_has_empty_phase_timeline_for_empty_plan():

    result = PlanPresenter(
        plan=TrainingPlan(),
        history=History(),
    ).build(
        reference_day=date(
            2026,
            8,
            12,
        )
    )

    assert result.phases == ()

def test_clips_first_plan_week_to_plan_horizon():

    workout = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            2,
            8,
            0,
        ),
        sport="Running",
        title="Easy Run",
        duration=timedelta(
            minutes=60,
        ),
        intensity="Easy",
        phase="Build",
    )

    result = PlanPresenter(
        plan=TrainingPlan(
            start_date=date(
                2026,
                8,
                2,
            ),
            end_date=date(
                2026,
                8,
                9,
            ),
            workouts=[
                workout,
            ],
        ),
        history=History(),
    ).build(
        reference_day=date(
            2026,
            8,
            4,
        )
    )

    assert (
        result.weeks[0].start_date
        == date(
            2026,
            8,
            2,
        )
    )

    assert (
        result.weeks[0].end_date
        == date(
            2026,
            8,
            2,
        )
    )

    assert (
        result.weeks[0].phase
        == "Build"
    )

    assert (
        result.phases[0].name
        == "Build"
    )

    assert (
        result.phases[0].start_date
        == date(
            2026,
            8,
            2,
        )
    )

def test_exposes_session_level_plan_chart_data():

    workout = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            4,
            8,
            0,
        ),
        sport="Running",
        title="Long Run",
        duration=timedelta(
            minutes=90,
        ),
        distance=18.0,
        elevation_gain=650.0,
        intensity="Easy to moderate",
        phase="Build",
    )

    result = PlanPresenter(
        plan=TrainingPlan(
            workouts=[
                workout,
            ]
        ),
        history=History(),
    ).build(
        reference_day=date(
            2026,
            8,
            4,
        )
    )

    assert len(
        result.chart_points
    ) == 1

    chart_point = (
        result.chart_points[0]
    )

    assert isinstance(
        chart_point,
        PlanChartPointData,
    )

    assert (
        chart_point.day
        == date(
            2026,
            8,
            4,
        )
    )

    assert (
        chart_point.title
        == "Long Run"
    )

    assert (
        chart_point.phase
        == "Build"
    )

    assert (
        chart_point.distance
        == 18.0
    )

    assert (
        chart_point.elevation_gain
        == 650.0
    )

    assert (
        chart_point.is_race
        is False
    )

    assert (
        chart_point.status
        == "pending"
    )

    assert (
        chart_point.planned_load
        is not None
    )


def test_plan_chart_data_is_immutable():

    workout = planned_workout(
        day=4,
        title="Easy Run",
        intensity="Easy",
        duration_minutes=60,
        phase="Build",
    )

    result = PlanPresenter(
        plan=TrainingPlan(
            workouts=[
                workout,
            ]
        ),
        history=History(),
    ).build(
        reference_day=date(
            2026,
            8,
            4,
        )
    )

    with pytest.raises(
        FrozenInstanceError
    ):

        result.chart_points[
            0
        ].title = "Changed"

def test_exposes_latest_plan_adaptation():

    older = TrainingPlanAdaptation(
        reconciled_on=date(
            2026,
            8,
            3,
        ),
        workout_day=date(
            2026,
            8,
            5,
        ),
        workout_title="Easy Run",
        previous_duration=timedelta(
            minutes=60,
        ),
        revised_duration=timedelta(
            minutes=50,
        ),
        trigger_status=(
            WorkoutOutcomeStatus.MODIFIED
        ),
        load_difference=-40.0,
    )

    latest = TrainingPlanAdaptation(
        reconciled_on=date(
            2026,
            8,
            5,
        ),
        workout_day=date(
            2026,
            8,
            6,
        ),
        workout_title="LT2 Run",
        previous_duration=timedelta(
            minutes=50,
        ),
        revised_duration=timedelta(
            minutes=38,
        ),
        trigger_status=(
            WorkoutOutcomeStatus.MODIFIED
        ),
        load_difference=120.0,
    )

    plan = TrainingPlan(
        adaptations=(
            older,
            latest,
        ),
    )

    result = PlanPresenter(
        plan=plan,
        history=History(),
    ).build(
        reference_day=date(
            2026,
            8,
            7,
        )
    )

    assert result.latest_adaptation == (
        PlanAdaptationData(
            reconciled_on=date(
                2026,
                8,
                5,
            ),
            workout_day=date(
                2026,
                8,
                6,
            ),
            workout_title="LT2 Run",
            previous_minutes=50,
            revised_minutes=38,
            reason=(
                "Completed load was higher "
                "than planned."
            ),
        )
    )


def test_has_no_latest_adaptation():

    result = PlanPresenter(
        plan=TrainingPlan(),
        history=History(),
    ).build(
        reference_day=date(
            2026,
            8,
            7,
        )
    )

    assert result.latest_adaptation is None

def test_current_phase_metrics_only_include_remaining_sessions():

    completed_phase_session = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            11,
            8,
            0,
        ),
        sport="Running",
        title="LT2 Run",
        duration=timedelta(
            minutes=45,
        ),
        intensity="Hard",
        phase="Peak",
    )

    today_session = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            12,
            8,
            0,
        ),
        sport="Running",
        title="Easy Run",
        duration=timedelta(
            minutes=50,
        ),
        intensity="Easy",
        phase="Peak",
    )

    future_session = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            18,
            8,
            0,
        ),
        sport="Running",
        title="Long Run",
        duration=timedelta(
            minutes=90,
        ),
        intensity="Easy to moderate",
        phase="Peak",
    )

    result = PlanPresenter(
        plan=TrainingPlan(
            workouts=[
                completed_phase_session,
                today_session,
                future_session,
            ],
        ),
        history=History(),
    ).build(
        reference_day=date(
            2026,
            8,
            12,
        )
    )

    phase = result.current_phase

    assert phase is not None

    assert (
        phase.sessions_remaining
        == 2
    )

    assert (
        phase.longest_session_minutes
        == 90
    )

    expected_remaining_load = sum(
        workout.planned_load
        for workout in (
            result.weeks[0].workouts[1],
            result.weeks[1].workouts[0],
        )
        if workout.planned_load is not None
    )

    assert (
        phase.planned_load_remaining
        == pytest.approx(
            expected_remaining_load
        )
    )
def test_exposes_final_race_as_target_event():

    first_race = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            9,
            13,
            8,
            0,
        ),
        sport="Road Running",
        title="Sealand",
        duration=timedelta(
            minutes=50,
        ),
        intensity="Race effort",
        phase="Race",
    )

    final_race = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            9,
            27,
            8,
            0,
        ),
        sport="Trail Running",
        title="Race",
        duration=timedelta(
            minutes=201,
        ),
        intensity="Race effort",
        objective=(
            "Execute the planned race strategy. "
            "Perform effectively at "
            "III Trail PÃ© Firme."
        ),
        phase="Race",
    )

    result = PlanPresenter(
        plan=TrainingPlan(
            workouts=[
                first_race,
                final_race,
            ],
        ),
        history=History(),
    ).build(
        reference_day=date(
            2026,
            8,
            5,
        )
    )

    assert (
        result.target_event_title
        == "III Trail Pé Firme"
    )

    assert (
        result.target_event_date
        == date(
            2026,
            9,
            27,
        )
    )


def test_exposes_single_race_as_target_event():

    race = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            9,
            13,
            8,
            0,
        ),
        sport="Road Running",
        title="Sealand",
        duration=timedelta(
            minutes=50,
        ),
        intensity="Race effort",
        phase="Race",
    )

    result = PlanPresenter(
        plan=TrainingPlan(
            workouts=[
                race,
            ],
        ),
        history=History(),
    ).build(
        reference_day=date(
            2026,
            8,
            5,
        )
    )

    assert (
        result.target_event_title
        == "Sealand"
    )

    assert (
        result.target_event_date
        == date(
            2026,
            9,
            13,
        )
    )


def test_has_no_target_event_without_races():

    training = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            8,
            11,
            8,
            0,
        ),
        sport="Running",
        title="LT2 Run",
        duration=timedelta(
            minutes=45,
        ),
        intensity="Hard",
        phase="Peak",
    )

    result = PlanPresenter(
        plan=TrainingPlan(
            workouts=[
                training,
            ],
        ),
        history=History(),
    ).build(
        reference_day=date(
            2026,
            8,
            5,
        )
    )

    assert (
        result.target_event_title
        is None
    )

    assert (
        result.target_event_date
        is None
    )

def test_prefers_specific_race_title():

    race = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            9,
            13,
            8,
            0,
        ),
        sport="Road Running",
        title="Sealand 10K",
        duration=timedelta(
            minutes=50,
        ),
        intensity="Race effort",
        objective=(
            "Perform effectively at Sealand."
        ),
        phase="Race",
    )

    result = PlanPresenter(
        plan=TrainingPlan(
            workouts=[
                race,
            ],
        ),
        history=History(),
    ).build(
        reference_day=date(
            2026,
            8,
            5,
        )
    )

    assert (
        result.target_event_title
        == "Sealand 10K"
    )
def test_uses_generic_race_title_without_event_name():

    race = PlannedWorkout(
        scheduled_at=datetime(
            2026,
            9,
            13,
            8,
            0,
        ),
        sport="Road Running",
        title="Race",
        duration=timedelta(
            minutes=50,
        ),
        intensity="Race effort",
        objective=(
            "Execute the planned competition."
        ),
        phase="Race",
    )

    result = PlanPresenter(
        plan=TrainingPlan(
            workouts=[
                race,
            ],
        ),
        history=History(),
    ).build(
        reference_day=date(
            2026,
            8,
            5,
        )
    )

    assert (
        result.target_event_title
        == "Race"
    )

def test_repairs_utf8_mojibake():

    assert (
        PlanPresenter
        ._repair_text_encoding(
            "III Trail PÃ© Firme"
        )
        == "III Trail Pé Firme"
    )


def test_keeps_valid_unicode_unchanged():

    assert (
        PlanPresenter
        ._repair_text_encoding(
            "III Trail Pé Firme"
        )
        == "III Trail Pé Firme"
    )