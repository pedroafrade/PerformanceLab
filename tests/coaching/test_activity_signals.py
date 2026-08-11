import pytest

from performancelab.coaching import (
    ActivitySignalCategory,
    ActivitySignalSeverity,
    assess_activity_signals,
)


def build_signals(
    **changes,
):
    values = {
        "planned_load": None,
        "completed_load": None,
        "duration_minutes": None,
        "average_heart_rate": None,
        "threshold_heart_rate": None,
        "distance": None,
        "elevation_gain": None,
        "event_distance": None,
        "event_elevation_gain": None,
        "readiness": None,
        "state_is_current": False,
    }

    values.update(
        changes
    )

    return assess_activity_signals(
        **values
    )


def signal_for(
    signals,
    code,
):
    return next(
        signal
        for signal in signals
        if signal.code == code
    )


def test_marks_load_above_plan():
    signals = build_signals(
        planned_load=400.0,
        completed_load=600.0,
    )

    signal = signal_for(
        signals,
        "load_above_plan",
    )

    assert (
        signal.category
        is ActivitySignalCategory.LOAD
    )
    assert (
        signal.severity
        is ActivitySignalSeverity.CAUTION
    )
    assert signal.ratio == pytest.approx(
        1.5
    )


def test_reuses_equivalent_load_tolerance():
    signals = build_signals(
        planned_load=400.0,
        completed_load=480.0,
    )

    signal = signal_for(
        signals,
        "load_near_plan",
    )

    assert (
        signal.severity
        is ActivitySignalSeverity.POSITIVE
    )
    assert signal.ratio == pytest.approx(
        1.2
    )


def test_classifies_unplanned_load():
    signals = build_signals(
        completed_load=450.0,
    )

    signal = signal_for(
        signals,
        "unplanned_training_load",
    )

    assert signal.observed == 450.0
    assert signal.reference is None
    assert signal.unit == "AU"


def test_detects_sustained_cardiovascular_demand():
    signals = build_signals(
        duration_minutes=102.0,
        average_heart_rate=164.0,
        threshold_heart_rate=177.0,
    )

    signal = signal_for(
        signals,
        (
            "sustained_high_"
            "cardiovascular_demand"
        ),
    )

    assert (
        signal.category
        is ActivitySignalCategory
        .CARDIOVASCULAR
    )
    assert signal.ratio == pytest.approx(
        164.0 / 177.0
    )


def test_short_activity_does_not_create_sustained_signal():
    signals = build_signals(
        duration_minutes=45.0,
        average_heart_rate=170.0,
        threshold_heart_rate=177.0,
    )

    assert all(
        signal.code
        != (
            "sustained_high_"
            "cardiovascular_demand"
        )
        for signal in signals
    )


def test_measures_target_event_specificity():
    signals = build_signals(
        distance=11.58,
        elevation_gain=632.0,
        event_distance=23.0,
        event_elevation_gain=950.0,
    )

    distance_signal = signal_for(
        signals,
        "event_distance_exposure",
    )
    elevation_signal = signal_for(
        signals,
        "event_elevation_exposure",
    )

    assert (
        distance_signal.ratio
        == pytest.approx(
            11.58 / 23.0
        )
    )
    assert (
        elevation_signal.ratio
        == pytest.approx(
            632.0 / 950.0
        )
    )

    assert (
        distance_signal.severity
        is ActivitySignalSeverity.POSITIVE
    )
    assert (
        elevation_signal.severity
        is ActivitySignalSeverity.POSITIVE
    )


def test_uses_recovery_only_for_current_state():
    historical_signals = build_signals(
        readiness="recovery",
        state_is_current=False,
    )

    current_signals = build_signals(
        readiness="recovery",
        state_is_current=True,
    )

    assert all(
        signal.category
        is not ActivitySignalCategory.RECOVERY
        for signal in historical_signals
    )

    signal = signal_for(
        current_signals,
        "recovery_attention",
    )

    assert (
        signal.severity
        is ActivitySignalSeverity.CAUTION
    )


def test_returns_immutable_collection():
    signals = build_signals(
        completed_load=450.0,
    )

    assert isinstance(
        signals,
        tuple,
    )