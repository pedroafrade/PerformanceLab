"""
Tests for JSON private alpha consent persistence.
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
from performancelab.storage.json_alpha_participation_consent_repository import (
    JsonAlphaParticipationConsentRepository,
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
        JsonAlphaParticipationConsentRepository(
            tmp_path
        )
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

    reloaded = (
        JsonAlphaParticipationConsentRepository(
            tmp_path
        )
    )

    assert (
        reloaded.latest(
            user_id="user-1",
            notice_version=(
                ALPHA_PARTICIPATION_CONSENT_VERSION
            ),
        )
        == consent
    )


def test_persists_withdrawal(
    tmp_path,
):

    repository = (
        JsonAlphaParticipationConsentRepository(
            tmp_path
        )
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

    withdrawn = consent.withdraw(
        withdrawn_at=timestamp(
            26
        )
    )

    repository.save(
        withdrawn
    )

    loaded = repository.latest(
        user_id="user-1",
        notice_version=(
            ALPHA_PARTICIPATION_CONSENT_VERSION
        ),
    )

    assert loaded == withdrawn
    assert loaded.is_active is False


def test_rejects_consent_identity_change(
    tmp_path,
):

    repository = (
        JsonAlphaParticipationConsentRepository(
            tmp_path
        )
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
        user_id="user-1",
        accepted_at=timestamp(
            26
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


def test_saved_file_contains_no_athlete_data(
    tmp_path,
):

    repository = (
        JsonAlphaParticipationConsentRepository(
            tmp_path
        )
    )

    repository.save(
        AlphaParticipationConsent(
            user_id="user-1",
            accepted_at=timestamp(
                25
            ),
            consent_id="consent-1",
        )
    )

    saved_text = (
        (
            tmp_path
            / "consent-1.json"
        )
        .read_text(
            encoding="utf-8"
        )
    )

    assert "user-1" in saved_text

    assert "heart_rate" not in saved_text
    assert "workout" not in saved_text
    assert "location" not in saved_text
    assert "feedback" not in saved_text