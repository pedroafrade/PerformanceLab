"""
Tests for the Training Coach consent interface.
"""

from app.components.training_coach_consent import (
    show_training_coach_consent_dialog,
    show_training_coach_consent_settings,
)


def test_consent_components_exist():

    assert callable(
        show_training_coach_consent_dialog
    )

    assert callable(
        show_training_coach_consent_settings
    )