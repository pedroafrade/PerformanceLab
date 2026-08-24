"""
Tests for JSON Training Coach consent persistence.
"""

from datetime import (
    datetime,
    timezone,
)

import pytest

from performancelab.storage.json_training_coach_consent_repository import (
    JsonTrainingCoachConsentRepository,
)
from performancelab.training_coach_consent import (
    TRAINING_COACH_CONSENT_VERSION,
    TrainingCoachConsent,
)


def timestamp(
    day,
):

    return datetime(
        2026,
        8,
        day,
        12,
        0,
        tzinfo=timezone.utc,
    )


def test_saves_and_loads_consent(
    tmp_path,
):

    repository = (
        JsonTrainingCoachConsentRepository(
            tmp_path
        )
    )

    consent = TrainingCoachConsent(
        user_id="user-1",
        granted_at=timestamp(
            24
        ),
    )

    repository.save(
        consent
    )

    loaded = repository.latest(
        user_id="user-1",
        policy_version=(
            TRAINING_COACH_CONSENT_VERSION
        ),
    )

    assert loaded == consent


def test_persists_withdrawal(
    tmp_path,
):

    repository = (
        JsonTrainingCoachConsentRepository(
            tmp_path
        )
    )

    consent = TrainingCoachConsent(
        user_id="user-1",
        granted_at=timestamp(
            24
        ),
    )

    repository.save(
        consent
    )

    withdrawn = consent.withdraw(
        withdrawn_at=timestamp(
            25
        )
    )

    repository.save(
        withdrawn
    )

    loaded = repository.latest(
        user_id="user-1",
        policy_version=(
            TRAINING_COACH_CONSENT_VERSION
        ),
    )

    assert loaded == withdrawn
    assert loaded.is_active is False


def test_isolates_users_and_policy_versions(
    tmp_path,
):

    repository = (
        JsonTrainingCoachConsentRepository(
            tmp_path
        )
    )

    current = TrainingCoachConsent(
        user_id="user-1",
        granted_at=timestamp(
            24
        ),
    )

    old = TrainingCoachConsent(
        user_id="user-1",
        granted_at=timestamp(
            23
        ),
        policy_version=(
            "training-coach-consent-old"
        ),
    )

    other_user = TrainingCoachConsent(
        user_id="user-2",
        granted_at=timestamp(
            24
        ),
    )

    repository.save(
        current
    )
    repository.save(
        old
    )
    repository.save(
        other_user
    )

    assert (
        repository.latest(
            user_id="user-1",
            policy_version=(
                TRAINING_COACH_CONSENT_VERSION
            ),
        )
        == current
    )

    assert (
        repository.list_for_user(
            "user-1"
        )
        == (
            old,
            current,
        )
    )


def test_rejects_consent_identity_change(
    tmp_path,
):

    repository = (
        JsonTrainingCoachConsentRepository(
            tmp_path
        )
    )

    consent = TrainingCoachConsent(
        user_id="user-1",
        granted_at=timestamp(
            24
        ),
    )

    repository.save(
        consent
    )

    changed = TrainingCoachConsent(
        consent_id=(
            consent.consent_id
        ),
        user_id="user-1",
        granted_at=timestamp(
            25
        ),
    )

    with pytest.raises(
        ValueError,
        match="cannot be changed",
    ):

        repository.save(
            changed
        )