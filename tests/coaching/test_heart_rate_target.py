import pytest

from performancelab.coaching import (
    HeartRateTarget,
    SessionPurpose,
    heart_rate_target_for,
)


@pytest.mark.parametrize(
    (
        "purpose",
        "expected_zones",
    ),
    (
        (
            SessionPurpose.RECOVERY,
            ("Z1",),
        ),
        (
            SessionPurpose.SHAKEOUT,
            ("Z1", "Z2"),
        ),
        (
            SessionPurpose.EASY,
            ("Z2",),
        ),
        (
            SessionPurpose.LONG,
            ("Z2",),
        ),
        (
            SessionPurpose.PRE_RACE,
            ("Z2",),
        ),
        (
            SessionPurpose.TECHNIQUE,
            ("Z2", "Z3"),
        ),
        (
            SessionPurpose.CROSS_TRAINING,
            ("Z2",),
        ),
    ),
)
def test_returns_target_for_session_purpose(
    purpose,
    expected_zones,
):

    target = heart_rate_target_for(
        purpose
    )

    assert isinstance(
        target,
        HeartRateTarget,
    )

    assert (
        target.zone_names
        == expected_zones
    )


@pytest.mark.parametrize(
    (
        "focus",
        "expected_zones",
    ),
    (
        (
            "tempo",
            ("Z3", "Z4"),
        ),
        (
            "threshold",
            ("Z4",),
        ),
        (
            "hills",
            ("Z4",),
        ),
        (
            "speed",
            ("Z4",),
        ),
        (
            "vo2max",
            ("Z5",),
        ),
        (
            None,
            ("Z4",),
        ),
    ),
)
def test_returns_intensity_target_for_focus(
    focus,
    expected_zones,
):

    target = heart_rate_target_for(
        SessionPurpose.INTENSITY,
        focus=focus,
    )

    assert target is not None

    assert (
        target.zone_names
        == expected_zones
    )


def test_normalizes_intensity_focus():

    target = heart_rate_target_for(
        SessionPurpose.INTENSITY,
        focus=" Threshold ",
    )

    assert target is not None
    assert target.zone_names == ("Z4",)

def test_tempo_uses_narrow_threshold_range():

    target = heart_rate_target_for(
        SessionPurpose.INTENSITY,
        focus="tempo",
    )

    assert target is not None

    assert target.threshold_range == (
        0.95,
        0.99,
    )


def test_threshold_uses_narrow_threshold_range():

    target = heart_rate_target_for(
        SessionPurpose.INTENSITY,
        focus="threshold",
    )

    assert target is not None

    assert target.threshold_range == (
        1.00,
        1.02,
    )

@pytest.mark.parametrize(
    "purpose",
    (
        SessionPurpose.REST,
        SessionPurpose.RACE,
    ),
)
def test_does_not_create_generic_target(
    purpose,
):

    assert (
        heart_rate_target_for(
            purpose
        )
        is None
    )


def test_target_normalizes_zone_names():

    target = HeartRateTarget(
        (" z2 ", "z3")
    )

    assert target.zone_names == (
        "Z2",
        "Z3",
    )

    assert target.primary_zone == "Z2"
    assert target.label == "Z2–Z3"


def test_rejects_invalid_purpose():

    with pytest.raises(
        TypeError,
        match="SessionPurpose",
    ):

        heart_rate_target_for(
            "easy"
        )