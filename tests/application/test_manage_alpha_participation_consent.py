"""
Tests for private alpha participation consent management.
"""

from datetime import (
    datetime,
    timezone,
)

from performancelab.application import (
    ManageAlphaParticipationConsent,
)
from performancelab.storage.in_memory_alpha_participation_consent_repository import (
    InMemoryAlphaParticipationConsentRepository,
)


def accepted_at():

    return datetime(
        2026,
        8,
        25,
        14,
        0,
        tzinfo=timezone.utc,
    )


def withdrawn_at():

    return datetime(
        2026,
        8,
        26,
        9,
        0,
        tzinfo=timezone.utc,
    )


def test_access_is_not_permitted_without_consent():

    manager = (
        ManageAlphaParticipationConsent(
            repository=(
                InMemoryAlphaParticipationConsentRepository()
            ),
            clock=accepted_at,
        )
    )

    assert (
        manager.is_permitted(
            user_id="user-1"
        )
        is False
    )


def test_accepts_current_notice():

    repository = (
        InMemoryAlphaParticipationConsentRepository()
    )

    manager = (
        ManageAlphaParticipationConsent(
            repository=repository,
            clock=accepted_at,
        )
    )

    consent = manager.accept(
        user_id="user-1"
    )

    assert (
        consent.accepted_at
        == accepted_at()
    )

    assert consent.is_active is True

    assert (
        manager.is_permitted(
            user_id="user-1"
        )
        is True
    )


def test_repeated_acceptance_is_idempotent():

    repository = (
        InMemoryAlphaParticipationConsentRepository()
    )

    manager = (
        ManageAlphaParticipationConsent(
            repository=repository,
            clock=accepted_at,
        )
    )

    first = manager.accept(
        user_id="user-1"
    )

    second = manager.accept(
        user_id="user-1"
    )

    assert second is first

    assert len(
        repository.list_for_user(
            "user-1"
        )
    ) == 1


def test_withdraws_current_consent():

    repository = (
        InMemoryAlphaParticipationConsentRepository()
    )

    manager = (
        ManageAlphaParticipationConsent(
            repository=repository,
            clock=accepted_at,
        )
    )

    accepted = manager.accept(
        user_id="user-1"
    )

    withdrawal_manager = (
        ManageAlphaParticipationConsent(
            repository=repository,
            clock=withdrawn_at,
        )
    )

    withdrawn = withdrawal_manager.withdraw(
        user_id="user-1"
    )

    assert withdrawn is not None

    assert (
        withdrawn.consent_id
        == accepted.consent_id
    )

    assert withdrawn.is_active is False

    assert (
        withdrawal_manager.is_permitted(
            user_id="user-1"
        )
        is False
    )


def test_withdrawal_without_consent_changes_nothing():

    manager = (
        ManageAlphaParticipationConsent(
            repository=(
                InMemoryAlphaParticipationConsentRepository()
            ),
            clock=withdrawn_at,
        )
    )

    assert (
        manager.withdraw(
            user_id="user-1"
        )
        is None
    )


def test_isolates_participant_consents():

    repository = (
        InMemoryAlphaParticipationConsentRepository()
    )

    manager = (
        ManageAlphaParticipationConsent(
            repository=repository,
            clock=accepted_at,
        )
    )

    manager.accept(
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