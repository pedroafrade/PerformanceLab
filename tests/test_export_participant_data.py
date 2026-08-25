"""
Tests for private alpha participant data export.
"""

import json

from datetime import (
    datetime,
    timezone,
)

import pytest

from performancelab.alpha_participation_consent import (
    AlphaParticipationConsent,
)
from performancelab.application import (
    ExportParticipantData,
)
from performancelab.athlete import (
    Athlete,
)
from performancelab.athlete_access import (
    AthleteAccessGrant,
)
from performancelab.authorization import (
    AthleteAuthorizationService,
)
from performancelab.identity import (
    ExternalIdentityLink,
    User,
)
from performancelab.training_coach_consent import (
    TrainingCoachConsent,
)
from performancelab.training_coach_usage import (
    TrainingCoachUsageEvent,
    TrainingCoachUsageStatus,
)


NOW = datetime(
    2026,
    8,
    25,
    14,
    0,
    tzinfo=timezone.utc,
)


class ItemRepository:

    def __init__(
        self,
        items=(),
    ):

        self.items = list(
            items
        )

    def list(
        self,
    ):

        return list(
            self.items
        )


class AthleteRepository:

    def __init__(
        self,
        athletes,
    ):

        self.athletes = {
            athlete.athlete_id: athlete
            for athlete in athletes
        }

    def get(
        self,
        athlete_id,
    ):

        return self.athletes[
            athlete_id
        ]


class AccessRepository(
    ItemRepository
):

    def get(
        self,
        user_id,
        athlete_id,
    ):

        for grant in self.items:

            if (
                grant.user_id
                == user_id
                and grant.athlete_id
                == athlete_id
            ):

                return grant

        raise KeyError(
            "Access grant not found."
        )

    def list_for_user(
        self,
        user_id,
    ):

        return [
            grant
            for grant in self.items
            if (
                grant.user_id
                == user_id
            )
        ]


class UserItemRepository(
    ItemRepository
):

    def list_for_user(
        self,
        user_id,
    ):

        return tuple(
            item
            for item in self.items
            if (
                item.user_id
                == user_id
            )
        )


def build_exporter(
    *,
    user,
    athlete,
    other_user=None,
    other_athlete=None,
):

    grant = AthleteAccessGrant(
        user_id=user.user_id,
        athlete_id=athlete.athlete_id,
        permission="owner",
    )

    identity_links = [
        ExternalIdentityLink(
            issuer="https://accounts.google.com",
            subject="participant-subject",
            user_id=user.user_id,
        )
    ]

    alpha_consents = [
        AlphaParticipationConsent(
            consent_id="alpha-consent",
            user_id=user.user_id,
            accepted_at=NOW,
        )
    ]

    coach_consents = [
        TrainingCoachConsent(
            consent_id="coach-consent",
            user_id=user.user_id,
            granted_at=NOW,
        )
    ]

    usage_events = [
        TrainingCoachUsageEvent(
            usage_id="usage-event",
            user_id=user.user_id,
            occurred_at=NOW,
            status=(
                TrainingCoachUsageStatus
                .GENERATED
            ),
            provider="google-gemini",
            model="gemini-3.5-flash",
            latency_ms=1200,
        )
    ]

    athletes = [
        athlete
    ]
    grants = [
        grant
    ]

    if (
        other_user is not None
        and other_athlete is not None
    ):

        athletes.append(
            other_athlete
        )

        grants.append(
            AthleteAccessGrant(
                user_id=other_user.user_id,
                athlete_id=(
                    other_athlete.athlete_id
                ),
                permission="owner",
            )
        )

        identity_links.append(
            ExternalIdentityLink(
                issuer=(
                    "https://accounts.google.com"
                ),
                subject="other-subject",
                user_id=other_user.user_id,
            )
        )

        alpha_consents.append(
            AlphaParticipationConsent(
                consent_id="other-alpha-consent",
                user_id=other_user.user_id,
                accepted_at=NOW,
            )
        )

        coach_consents.append(
            TrainingCoachConsent(
                consent_id="other-coach-consent",
                user_id=other_user.user_id,
                granted_at=NOW,
            )
        )

        usage_events.append(
            TrainingCoachUsageEvent(
                usage_id="other-usage-event",
                user_id=other_user.user_id,
                occurred_at=NOW,
                status=(
                    TrainingCoachUsageStatus
                    .FAILED
                ),
                error_code=(
                    "provider_unavailable"
                ),
            )
        )

    access_repository = (
        AccessRepository(
            grants
        )
    )

    exporter = ExportParticipantData(
        athlete_repository=(
            AthleteRepository(
                athletes
            )
        ),
        external_identity_repository=(
            ItemRepository(
                identity_links
            )
        ),
        athlete_access_repository=(
            access_repository
        ),
        alpha_participation_consent_repository=(
            UserItemRepository(
                alpha_consents
            )
        ),
        training_coach_consent_repository=(
            UserItemRepository(
                coach_consents
            )
        ),
        training_coach_usage_repository=(
            UserItemRepository(
                usage_events
            )
        ),
        authorization=(
            AthleteAuthorizationService(
                access_repository
            )
        ),
    )

    return exporter


def test_export_contains_complete_participant_data():

    athlete = Athlete(
        athlete_id="athlete-one",
        name="Participant One",
    )

    user = User(
        user_id="user-one",
        email="participant@example.com",
        role="athlete",
        athlete_id=athlete.athlete_id,
    )

    result = build_exporter(
        user=user,
        athlete=athlete,
    ).execute(
        user,
        generated_at=NOW,
    )

    data = result.data

    assert data[
        "format"
    ] == (
        "PerformanceLab participant "
        "data export"
    )

    assert data[
        "version"
    ] == 1

    assert data[
        "participant"
    ] == {
        "user_id": "user-one",
        "email": "participant@example.com",
        "role": "athlete",
        "athlete_id": "athlete-one",
    }

    assert data[
        "external_identities"
    ][0][
        "subject"
    ] == "participant-subject"

    assert data[
        "athlete_access"
    ][0][
        "permission"
    ] == "owner"

    assert data[
        "alpha_participation_consents"
    ][0][
        "consent_id"
    ] == "alpha-consent"

    assert data[
        "training_coach_consents"
    ][0][
        "consent_id"
    ] == "coach-consent"

    assert data[
        "training_coach_usage"
    ][0][
        "usage_id"
    ] == "usage-event"

    assert data[
        "athlete"
    ][
        "athlete"
    ][
        "id"
    ] == "athlete-one"


def test_export_json_is_readable_and_serializable():

    athlete = Athlete(
        athlete_id="athlete-one",
        name="Atleta",
    )

    user = User(
        user_id="user-one",
        email="participant@example.com",
        role="athlete",
        athlete_id=athlete.athlete_id,
    )

    result = build_exporter(
        user=user,
        athlete=athlete,
    ).execute(
        user,
        generated_at=NOW,
    )

    exported_json = (
        result.to_json()
    )

    decoded = json.loads(
        exported_json
    )

    assert decoded == result.data

    assert "\n    " in exported_json

    assert "Atleta" in exported_json


def test_export_excludes_other_participant_data():

    athlete = Athlete(
        athlete_id="athlete-one",
        name="Participant One",
    )

    user = User(
        user_id="user-one",
        email="one@example.com",
        role="athlete",
        athlete_id=athlete.athlete_id,
    )

    other_athlete = Athlete(
        athlete_id="athlete-two",
        name="Participant Two",
    )

    other_user = User(
        user_id="user-two",
        email="two@example.com",
        role="athlete",
        athlete_id=(
            other_athlete.athlete_id
        ),
    )

    result = build_exporter(
        user=user,
        athlete=athlete,
        other_user=other_user,
        other_athlete=other_athlete,
    ).execute(
        user,
        generated_at=NOW,
    )

    exported_json = (
        result.to_json()
    )

    assert "user-two" not in exported_json
    assert "athlete-two" not in exported_json
    assert "two@example.com" not in exported_json
    assert "other-subject" not in exported_json
    assert (
        "other-alpha-consent"
        not in exported_json
    )
    assert (
        "other-coach-consent"
        not in exported_json
    )
    assert (
        "other-usage-event"
        not in exported_json
    )


def test_export_requires_owner_access():

    athlete = Athlete(
        athlete_id="athlete-one",
        name="Participant One",
    )

    user = User(
        user_id="user-one",
        email="participant@example.com",
        role="athlete",
        athlete_id=athlete.athlete_id,
    )

    access_repository = (
        AccessRepository(
            [
                AthleteAccessGrant(
                    user_id=user.user_id,
                    athlete_id=(
                        athlete.athlete_id
                    ),
                    permission="coach",
                )
            ]
        )
    )

    exporter = ExportParticipantData(
        athlete_repository=(
            AthleteRepository(
                [athlete]
            )
        ),
        external_identity_repository=(
            ItemRepository()
        ),
        athlete_access_repository=(
            access_repository
        ),
        alpha_participation_consent_repository=(
            UserItemRepository()
        ),
        training_coach_consent_repository=(
            UserItemRepository()
        ),
        training_coach_usage_repository=(
            UserItemRepository()
        ),
        authorization=(
            AthleteAuthorizationService(
                access_repository
            )
        ),
    )

    with pytest.raises(
        PermissionError
    ):

        exporter.execute(
            user,
            generated_at=NOW,
        )


def test_export_requires_timezone_aware_timestamp():

    athlete = Athlete(
        athlete_id="athlete-one",
        name="Participant One",
    )

    user = User(
        user_id="user-one",
        email="participant@example.com",
        role="athlete",
        athlete_id=athlete.athlete_id,
    )

    exporter = build_exporter(
        user=user,
        athlete=athlete,
    )

    with pytest.raises(
        ValueError,
        match="timezone",
    ):

        exporter.execute(
            user,
            generated_at=datetime(
                2026,
                8,
                25,
                14,
                0,
            ),
        )