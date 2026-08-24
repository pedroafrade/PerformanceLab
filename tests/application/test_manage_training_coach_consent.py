"""
Tests for Training Coach consent management.
"""

from datetime import (
    datetime,
    timezone,
)

import pytest

from performancelab.application import (
    ManageTrainingCoachConsent,
)
from performancelab.storage.in_memory_training_coach_consent_repository import (
    InMemoryTrainingCoachConsentRepository,
)
from performancelab.training_coach_consent import (
    TRAINING_COACH_CONSENT_VERSION,
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


def test_has_no_permission_without_consent():

    manager = ManageTrainingCoachConsent(
        repository=(
            InMemoryTrainingCoachConsentRepository()
        ),
        clock=lambda: timestamp(
            24
        ),
    )

    assert (
        manager.is_permitted(
            user_id="user-1"
        )
        is False
    )


def test_grants_current_consent():

    repository = (
        InMemoryTrainingCoachConsentRepository()
    )

    manager = ManageTrainingCoachConsent(
        repository=repository,
        clock=lambda: timestamp(
            24
        ),
    )

    granted = manager.grant(
        user_id="user-1"
    )

    assert granted.user_id == "user-1"

    assert (
        granted.policy_version
        == TRAINING_COACH_CONSENT_VERSION
    )

    assert granted.is_active is True

    assert (
        manager.is_permitted(
            user_id="user-1"
        )
        is True
    )

    assert (
        repository.list_for_user(
            "user-1"
        )
        == (
            granted,
        )
    )


def test_repeated_grant_is_idempotent():

    repository = (
        InMemoryTrainingCoachConsentRepository()
    )

    manager = ManageTrainingCoachConsent(
        repository=repository,
        clock=lambda: timestamp(
            24
        ),
    )

    first = manager.grant(
        user_id="user-1"
    )

    second = manager.grant(
        user_id="user-1"
    )

    assert second == first

    assert len(
        repository.list_for_user(
            "user-1"
        )
    ) == 1


def test_withdraws_active_consent():

    repository = (
        InMemoryTrainingCoachConsentRepository()
    )

    times = iter(
        (
            timestamp(
                24
            ),
            timestamp(
                25
            ),
        )
    )

    manager = ManageTrainingCoachConsent(
        repository=repository,
        clock=lambda: next(
            times
        ),
    )

    granted = manager.grant(
        user_id="user-1"
    )

    withdrawn = manager.withdraw(
        user_id="user-1"
    )

    assert withdrawn is not None

    assert (
        withdrawn.consent_id
        == granted.consent_id
    )

    assert withdrawn.is_active is False

    assert (
        withdrawn.withdrawn_at
        == timestamp(
            25
        )
    )

    assert (
        manager.is_permitted(
            user_id="user-1"
        )
        is False
    )


def test_withdrawal_without_consent_is_safe():

    manager = ManageTrainingCoachConsent(
        repository=(
            InMemoryTrainingCoachConsentRepository()
        ),
        clock=lambda: timestamp(
            24
        ),
    )

    assert (
        manager.withdraw(
            user_id="user-1"
        )
        is None
    )


def test_new_consent_can_follow_withdrawal():

    repository = (
        InMemoryTrainingCoachConsentRepository()
    )

    times = iter(
        (
            timestamp(
                23
            ),
            timestamp(
                24
            ),
            timestamp(
                25
            ),
        )
    )

    manager = ManageTrainingCoachConsent(
        repository=repository,
        clock=lambda: next(
            times
        ),
    )

    first = manager.grant(
        user_id="user-1"
    )

    manager.withdraw(
        user_id="user-1"
    )

    second = manager.grant(
        user_id="user-1"
    )

    assert (
        second.consent_id
        != first.consent_id
    )

    assert second.is_active is True

    assert len(
        repository.list_for_user(
            "user-1"
        )
    ) == 2


def test_isolates_users():

    repository = (
        InMemoryTrainingCoachConsentRepository()
    )

    manager = ManageTrainingCoachConsent(
        repository=repository,
        clock=lambda: timestamp(
            24
        ),
    )

    manager.grant(
        user_id="user-1"
    )

    assert (
        manager.is_permitted(
            user_id="user-1"
        )
        is True
    )

    assert (
        manager.is_permitted(
            user_id="user-2"
        )
        is False
    )


@pytest.mark.parametrize(
    "user_id",
    (
        "",
        "   ",
    ),
)
def test_rejects_empty_user_id(
    user_id,
):

    manager = ManageTrainingCoachConsent(
        repository=(
            InMemoryTrainingCoachConsentRepository()
        ),
    )

    with pytest.raises(
        ValueError,
        match="cannot be empty",
    ):

        manager.grant(
            user_id=user_id
        )