"""
Tests for private alpha participation consent.
"""

from dataclasses import (
    FrozenInstanceError,
)
from datetime import (
    datetime,
    timezone,
)

import pytest

from performancelab.alpha_participation_consent import (
    ALPHA_PARTICIPATION_CONSENT_VERSION,
    AlphaParticipationConsent,
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


def test_current_active_consent_permits_participation():

    consent = AlphaParticipationConsent(
        user_id="user-1",
        accepted_at=accepted_at(),
    )

    assert (
        consent.notice_version
        == (
            ALPHA_PARTICIPATION_CONSENT_VERSION
        )
    )

    assert (
        consent.purpose
        == "private-alpha-participation"
    )

    assert consent.is_active is True

    assert (
        consent.permits_current_notice()
        is True
    )


def test_old_notice_does_not_permit_participation():

    consent = AlphaParticipationConsent(
        user_id="user-1",
        accepted_at=accepted_at(),
        notice_version=(
            "alpha-participation-consent-old"
        ),
    )

    assert consent.is_active is True

    assert (
        consent.permits_current_notice()
        is False
    )


def test_normalizes_identifiers():

    consent = AlphaParticipationConsent(
        user_id=" user-1 ",
        accepted_at=accepted_at(),
        consent_id=" consent-1 ",
    )

    assert consent.user_id == "user-1"

    assert (
        consent.consent_id
        == "consent-1"
    )


def test_withdraws_consent_immutably():

    consent = AlphaParticipationConsent(
        user_id="user-1",
        accepted_at=accepted_at(),
    )

    withdrawn_at = datetime(
        2026,
        8,
        26,
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
        withdrawn.permits_current_notice()
        is False
    )

    assert (
        withdrawn.consent_id
        == consent.consent_id
    )


def test_repeated_withdrawal_is_idempotent():

    consent = AlphaParticipationConsent(
        user_id="user-1",
        accepted_at=accepted_at(),
    ).withdraw(
        withdrawn_at=datetime(
            2026,
            8,
            26,
            9,
            30,
            tzinfo=timezone.utc,
        )
    )

    repeated = consent.withdraw(
        withdrawn_at=datetime(
            2026,
            8,
            27,
            9,
            30,
            tzinfo=timezone.utc,
        )
    )

    assert repeated is consent


def test_rejects_withdrawal_before_acceptance():

    with pytest.raises(
        ValueError,
        match="cannot be earlier",
    ):

        AlphaParticipationConsent(
            user_id="user-1",
            accepted_at=accepted_at(),
            withdrawn_at=datetime(
                2026,
                8,
                24,
                14,
                0,
                tzinfo=timezone.utc,
            ),
        )


@pytest.mark.parametrize(
    "timestamp_field",
    (
        "accepted_at",
        "withdrawn_at",
    ),
)
def test_requires_timezone_for_timestamps(
    timestamp_field,
):

    values = {
        "user_id": "user-1",
        "accepted_at": accepted_at(),
    }

    values[
        timestamp_field
    ] = datetime(
        2026,
        8,
        25,
        14,
        0,
    )

    with pytest.raises(
        ValueError,
        match="must include a timezone",
    ):

        AlphaParticipationConsent(
            **values
        )


def test_consent_is_immutable():

    consent = AlphaParticipationConsent(
        user_id="user-1",
        accepted_at=accepted_at(),
    )

    with pytest.raises(
        FrozenInstanceError
    ):

        consent.notice_version = "changed"