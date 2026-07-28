from performancelab.analysis.training_state import TrainingState


def make_training_state(
    *,
    ctl: float = 50.0,
    atl: float = 50.0,
    tsb: float = 0.0,
) -> TrainingState:
    return TrainingState(
        ctl=ctl,
        atl=atl,
        tsb=tsb,
        acute_chronic_ratio=None,
        monotony=None,
        strain=None,
        consistency=None,
        weekly_frequency=None,
        days_since_last_workout=None,
        recent_training_load=None,
    )


def test_recovery_status_is_good_when_intensity_is_tolerated():
    state = make_training_state(
        ctl=50.0,
        atl=50.0,
        tsb=0.0,
    )

    assert state.recovery_status == "Good"


def test_recovery_status_is_moderate_when_volume_can_be_absorbed():
    state = make_training_state(
        ctl=50.0,
        atl=55.0,
        tsb=-5.0,
    )

    assert state.recovery_status == "Moderate"


def test_recovery_status_is_low_when_training_should_remain_easy():
    state = make_training_state(
        ctl=50.0,
        atl=65.0,
        tsb=-15.0,
    )

    assert state.recovery_status == "Low"


def test_recovery_status_reports_when_recovery_is_needed():
    state = make_training_state(
        ctl=50.0,
        atl=71.0,
        tsb=-21.0,
    )

    assert state.recovery_status == "Recovery needed"


def test_recovery_boundary_does_not_require_recovery():
    state = make_training_state(
        ctl=50.0,
        atl=70.0,
        tsb=-20.0,
    )

    assert state.needs_recovery is False
    assert state.recovery_status == "Low"


def test_recovery_recommendation_allows_normal_training():
    state = make_training_state(
        ctl=50.0,
        atl=50.0,
        tsb=0.0,
    )

    assert (
        state.recovery_recommendation
        == "Ready for a normal training session."
    )


def test_recovery_recommendation_controls_demanding_sessions():
    state = make_training_state(
        ctl=50.0,
        atl=55.0,
        tsb=-5.0,
    )

    assert state.recovery_recommendation == (
        "Training can continue, but keep demanding sessions "
        "controlled."
    )


def test_recovery_recommendation_keeps_training_easy():
    state = make_training_state(
        ctl=50.0,
        atl=65.0,
        tsb=-15.0,
    )

    assert state.recovery_recommendation == (
        "Keep training easy and monitor recovery before adding "
        "more load."
    )


def test_recovery_recommendation_prioritises_recovery():
    state = make_training_state(
        ctl=50.0,
        atl=71.0,
        tsb=-21.0,
    )

    assert state.recovery_recommendation == (
        "Prioritise recovery before the next demanding "
        "training session."
    )