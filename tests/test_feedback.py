"""
Tests for AthleteFeedback.
"""

from performancelab.workout import AthleteFeedback


def test_feedback_creation():

    feedback = AthleteFeedback(

        rpe=8,

        feeling=7,

        motivation=9

    )

    assert feedback.rpe == 8

    assert feedback.feeling == 7

    assert feedback.motivation == 9

def test_effective_rpe_uses_estimate_when_manual_is_missing():

    feedback = AthleteFeedback(
        estimated_rpe=6,
    )

    assert feedback.rpe is None
    assert feedback.estimated_rpe == 6
    assert feedback.effective_rpe == 6


def test_effective_rpe_prioritises_manual_value():

    feedback = AthleteFeedback(
        rpe=8,
        estimated_rpe=6,
    )

    assert feedback.effective_rpe == 8


def test_effective_rpe_is_missing_without_any_value():

    feedback = AthleteFeedback()

    assert feedback.effective_rpe is None