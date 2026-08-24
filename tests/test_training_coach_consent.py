"""
Tests for versioned Training Coach consent.
"""

from dataclasses import (
    FrozenInstanceError,
)
from datetime import (
    datetime,
    timezone,
)

import pytest

from performancelab.training_coach_consent import (
    TRAINING_COACH_CONSENT_VERSION,
    TrainingCoachConsent,
)


def granted_at():

    return datetime(
        2026,
        8,
        24,
        14,
        0,
        tzinfo=timezone.utc,
    )


def test_current_active_consent_permits_generation():

    consent = TrainingCoachConsent(
        user_id="user-1",
        granted_at=granted_at(),
    )

    assert (
        consent.policy_version
        == TRAINING_COACH_CONSENT_VERSION
    )

    assert (
        consent.purpose
        == "training-coach"
    )

    assert consent.is_active is True

    assert (
        consent.permits_current_policy()
        is True
    )


def test_old_policy_version_does_not_permit_generation():

    consent = TrainingCoachConsent(
        user_id="user-1",
        granted_at=granted_at(),
        policy_version=(
            "training-coach-consent-old"
        ),
    )

    assert consent.is_active is True

    assert (
        consent.permits_current_policy()
        is False
    )


def test_withdraws_consent_immutably():

    consent = TrainingCoachConsent(
        user_id="user-1",
        granted_at=granted_at(),
    )

    withdrawn_at = datetime(
        2026,
        8,
        25,
        9,
        30,
        tzinfo=timezone.utc,
    )

    withdrawn = consent.withdraw(
        withdrawn_at=withdrawn_at
    )

    assert consent.is_active is True
    assert withdrawn.is_active is False

    assert (
        withdrawn.withdrawn_at
        == withdrawn_at
    )

    assert (
        withdrawn.permits_current_policy()
        is False
    )

    assert (
        withdrawn.consent_id
        == consent.consent_id
    )


def test_repeated_withdrawal_is_idempotent():

    consent = TrainingCoachConsent(
        user_id="user-1",
        granted_at=granted_at(),
    ).withdraw(
        withdrawn_at=datetime(
            2026,
            8,
            25,
            9,
            30,
            tzinfo=timezone.utc,
        )
    )

    repeated = consent.withdraw(
        withdrawn_at=datetime(
            2026,
            8,
            26,
            9,
            30,
            tzinfo=timezone.utc,
        )
    )

    assert repeated is consent


def test_rejects_withdrawal_before_grant():

    with pytest.raises(
        ValueError,
        match="cannot be earlier",
    ):

        TrainingCoachConsent(
            user_id="user-1",
            granted_at=granted_at(),
            withdrawn_at=datetime(
                2026,
                8,
                23,
                14,
                0,
                tzinfo=timezone.utc,
            ),
        )


@pytest.mark.parametrize(
    "timestamp_field",
    (
        "granted_at",
        "withdrawn_at",
    ),
)
def test_requires_timezone_for_consent_timestamps(
    timestamp_field,
):

    values = {
        "user_id": "user-1",
        "granted_at": granted_at(),
    }

    values[
        timestamp_field
    ] = datetime(
        2026,
        8,
        24,
        14,
        0,
    )

    with pytest.raises(
        ValueError,
        match="must include a timezone",
    ):

        TrainingCoachConsent(
            **values
        )


def test_consent_is_immutable():

    consent = TrainingCoachConsent(
        user_id="user-1",
        granted_at=granted_at(),
    )

    with pytest.raises(
        FrozenInstanceError
    ):

        consent.policy_version = (
            "changed"
        )