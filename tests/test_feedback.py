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