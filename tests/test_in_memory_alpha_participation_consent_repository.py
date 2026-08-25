"""
Tests for in-memory private alpha consent persistence.
"""

from datetime import (
    datetime,
    timezone,
)

import pytest

from performancelab.alpha_participation_consent import (
    ALPHA_PARTICIPATION_CONSENT_VERSION,
    AlphaParticipationConsent,
)
from performancelab.storage.in_memory_alpha_participation_consent_repository import (
    InMemoryAlphaParticipationConsentRepository,
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


def test_saves_and_finds_consent():

    repository = (
        InMemoryAlphaParticipationConsentRepository()
    )

    consent = AlphaParticipationConsent(
        user_id="user-1",
        accepted_at=timestamp(
            25
        ),
    )

    repository.save(
        consent
    )

    assert (
        repository.latest(
            user_id="user-1",
            notice_version=(
                ALPHA_PARTICIPATION_CONSENT_VERSION
            ),
        )
        == consent
    )


def test_isolates_users():

    repository = (
        InMemoryAlphaParticipationConsentRepository()
    )

    first = AlphaParticipationConsent(
        user_id="user-1",
        accepted_at=timestamp(
            25
        ),
    )

    second = AlphaParticipationConsent(
        user_id="user-2",
        accepted_at=timestamp(
            25
        ),
    )

    repository.save(
        first
    )
    repository.save(
        second
    )

    assert (
        repository.list_for_user(
            "user-1"
        )
        == (
            first,
        )
    )


def test_rejects_identity_change():

    repository = (
        InMemoryAlphaParticipationConsentRepository()
    )

    consent = AlphaParticipationConsent(
        user_id="user-1",
        accepted_at=timestamp(
            25
        ),
        consent_id="consent-1",
    )

    repository.save(
        consent
    )

    changed = AlphaParticipationConsent(
        user_id="user-2",
        accepted_at=timestamp(
            25
        ),
        consent_id="consent-1",
    )

    with pytest.raises(
        ValueError,
        match="cannot be changed",
    ):

        repository.save(
            changed
        )