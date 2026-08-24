"""
Tests for in-memory Training Coach consent persistence.
"""

from datetime import (
    datetime,
    timezone,
)

import pytest

from performancelab.storage.in_memory_training_coach_consent_repository import (
    InMemoryTrainingCoachConsentRepository,
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


def consent(
    *,
    user_id="user-1",
    day=24,
    policy_version=(
        TRAINING_COACH_CONSENT_VERSION
    ),
):

    return TrainingCoachConsent(
        user_id=user_id,
        granted_at=timestamp(
            day
        ),
        policy_version=(
            policy_version
        ),
    )


def test_empty_repository_has_no_consent():

    repository = (
        InMemoryTrainingCoachConsentRepository()
    )

    assert (
        repository.latest(
            user_id="user-1",
            policy_version=(
                TRAINING_COACH_CONSENT_VERSION
            ),
        )
        is None
    )


def test_saves_and_finds_current_consent():

    repository = (
        InMemoryTrainingCoachConsentRepository()
    )

    granted = consent()

    repository.save(
        granted
    )

    assert (
        repository.latest(
            user_id="user-1",
            policy_version=(
                TRAINING_COACH_CONSENT_VERSION
            ),
        )
        == granted
    )


def test_returns_latest_consent_state():

    older = consent(
        day=23
    )

    newer = consent(
        day=24
    )

    repository = (
        InMemoryTrainingCoachConsentRepository(
            (
                older,
                newer,
            )
        )
    )

    assert (
        repository.latest(
            user_id="user-1",
            policy_version=(
                TRAINING_COACH_CONSENT_VERSION
            ),
        )
        == newer
    )


def test_withdrawal_replaces_same_consent_record():

    repository = (
        InMemoryTrainingCoachConsentRepository()
    )

    granted = consent()

    repository.save(
        granted
    )

    withdrawn = granted.withdraw(
        withdrawn_at=timestamp(
            25
        )
    )

    repository.save(
        withdrawn
    )

    stored = repository.latest(
        user_id="user-1",
        policy_version=(
            TRAINING_COACH_CONSENT_VERSION
        ),
    )

    assert stored == withdrawn
    assert stored.is_active is False

    assert (
        repository.list_for_user(
            "user-1"
        )
        == (
            withdrawn,
        )
    )


def test_keeps_different_policy_versions():

    current = consent()

    old = consent(
        day=22,
        policy_version=(
            "training-coach-consent-old"
        ),
    )

    repository = (
        InMemoryTrainingCoachConsentRepository(
            (
                old,
                current,
            )
        )
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
        repository.latest(
            user_id="user-1",
            policy_version=(
                "training-coach-consent-old"
            ),
        )
        == old
    )


def test_isolates_consent_by_user():

    first = consent(
        user_id="user-1",
        day=23,
    )

    second = consent(
        user_id="user-2",
        day=24,
    )

    repository = (
        InMemoryTrainingCoachConsentRepository(
            (
                first,
                second,
            )
        )
    )

    assert (
        repository.list_for_user(
            "user-1"
        )
        == (
            first,
        )
    )

    assert (
        repository.list_for_user(
            "user-2"
        )
        == (
            second,
        )
    )


def test_rejects_non_consent_value():

    repository = (
        InMemoryTrainingCoachConsentRepository()
    )

    with pytest.raises(
        TypeError,
        match="TrainingCoachConsent",
    ):

        repository.save(
            object()
        )