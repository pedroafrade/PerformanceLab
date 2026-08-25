"""
Tests for complete private alpha participant deletion.
"""

from contextlib import (
    contextmanager,
)
from types import (
    SimpleNamespace,
)

import pytest

from performancelab.application import (
    DeleteParticipantData,
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


class Repository:

    def __init__(
        self,
        items=(),
        *,
        key_name,
    ):

        self.items = list(
            items
        )
        self.key_name = key_name
        self.deleted = []

    def list(
        self,
    ):

        return list(
            self.items
        )

    def list_for_user(
        self,
        user_id,
    ):

        return tuple(
            item
            for item in self.items
            if item.user_id == user_id
        )

    def delete(
        self,
        item_id,
    ):

        self.deleted.append(
            item_id
        )

        self.items = [
            item
            for item in self.items
            if (
                getattr(
                    item,
                    self.key_name
                )
                != item_id
            )
        ]


class IdentityRepository(
    Repository
):

    def delete(
        self,
        issuer,
        subject,
    ):

        self.deleted.append(
            (
                issuer,
                subject,
            )
        )

        self.items = [
            item
            for item in self.items
            if (
                item.issuer,
                item.subject,
            )
            != (
                issuer,
                subject,
            )
        ]


class AccessRepository:

    def __init__(
        self,
        grants,
    ):

        self.items = list(
            grants
        )
        self.deleted = []

    def get(
        self,
        user_id,
        athlete_id,
    ):

        for grant in self.items:

            if (
                grant.user_id == user_id
                and grant.athlete_id
                == athlete_id
            ):

                return grant

        raise KeyError(
            "Access grant not found."
        )

    def list_for_athlete(
        self,
        athlete_id,
    ):

        return [
            grant
            for grant in self.items
            if (
                grant.athlete_id
                == athlete_id
            )
        ]

    def delete(
        self,
        user_id,
        athlete_id,
    ):

        self.deleted.append(
            (
                user_id,
                athlete_id,
            )
        )

        self.items = [
            grant
            for grant in self.items
            if (
                grant.user_id,
                grant.athlete_id,
            )
            != (
                user_id,
                athlete_id,
            )
        ]


class EntityRepository:

    def __init__(
        self,
        entities,
        *,
        key_name,
    ):

        self.entities = {
            getattr(
                entity,
                key_name
            ): entity
            for entity in entities
        }
        self.deleted = []

    def delete(
        self,
        entity_id,
    ):

        self.deleted.append(
            entity_id
        )

        del self.entities[
            entity_id
        ]


class TransactionFactory:

    def __init__(
        self,
    ):

        self.entered = False
        self.completed = False

    @contextmanager
    def __call__(
        self,
    ):

        self.entered = True

        yield

        self.completed = True


def test_deletes_complete_participant_data():

    athlete = Athlete(
        athlete_id="athlete-one",
        name="Participant",
    )

    user = User(
        user_id="user-one",
        email="participant@example.com",
        role="athlete",
        athlete_id=athlete.athlete_id,
    )

    owner_grant = AthleteAccessGrant(
        user_id=user.user_id,
        athlete_id=athlete.athlete_id,
        permission="owner",
    )

    coach_grant = AthleteAccessGrant(
        user_id="coach-user",
        athlete_id=athlete.athlete_id,
        permission="coach",
    )

    access_repository = (
        AccessRepository(
            [
                owner_grant,
                coach_grant,
            ]
        )
    )

    identity_repository = (
        IdentityRepository(
            [
                ExternalIdentityLink(
                    issuer="google",
                    subject="subject-one",
                    user_id=user.user_id,
                )
            ],
            key_name="subject",
        )
    )

    invitation = SimpleNamespace(
        invitation_id="invitation-one",
        email=user.email,
        athlete_id=athlete.athlete_id,
        claimed_by_user_id=user.user_id,
    )

    alpha_consent = SimpleNamespace(
        consent_id="alpha-consent",
        user_id=user.user_id,
    )

    coach_consent = SimpleNamespace(
        consent_id="coach-consent",
        user_id=user.user_id,
    )

    usage_event = SimpleNamespace(
        usage_id="usage-event",
        user_id=user.user_id,
    )

    invitation_repository = Repository(
        [invitation],
        key_name="invitation_id",
    )

    alpha_consent_repository = Repository(
        [alpha_consent],
        key_name="consent_id",
    )

    coach_consent_repository = Repository(
        [coach_consent],
        key_name="consent_id",
    )

    usage_repository = Repository(
        [usage_event],
        key_name="usage_id",
    )

    user_repository = EntityRepository(
        [user],
        key_name="user_id",
    )

    athlete_repository = EntityRepository(
        [athlete],
        key_name="athlete_id",
    )

    transaction_factory = (
        TransactionFactory()
    )

    result = DeleteParticipantData(
        athlete_repository=(
            athlete_repository
        ),
        user_repository=(
            user_repository
        ),
        external_identity_repository=(
            identity_repository
        ),
        invitation_repository=(
            invitation_repository
        ),
        athlete_access_repository=(
            access_repository
        ),
        alpha_participation_consent_repository=(
            alpha_consent_repository
        ),
        training_coach_consent_repository=(
            coach_consent_repository
        ),
        training_coach_usage_repository=(
            usage_repository
        ),
        authorization=(
            AthleteAuthorizationService(
                access_repository
            )
        ),
        transaction_factory=(
            transaction_factory
        ),
    ).execute(
        user
    )

    assert result.user_id == user.user_id
    assert result.athlete_id == athlete.athlete_id

    assert identity_repository.items == []
    assert invitation_repository.items == []
    assert access_repository.items == []
    assert alpha_consent_repository.items == []
    assert coach_consent_repository.items == []
    assert usage_repository.items == []
    assert user_repository.entities == {}
    assert athlete_repository.entities == {}

    assert transaction_factory.entered
    assert transaction_factory.completed


def test_refuses_deletion_without_owner_access():

    athlete = Athlete(
        athlete_id="athlete-one",
        name="Participant",
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
                    athlete_id=athlete.athlete_id,
                    permission="coach",
                )
            ]
        )
    )

    empty_repository = Repository(
        key_name="consent_id"
    )

    transaction_factory = (
        TransactionFactory()
    )

    with pytest.raises(
        PermissionError
    ):

        DeleteParticipantData(
            athlete_repository=(
                EntityRepository(
                    [athlete],
                    key_name="athlete_id",
                )
            ),
            user_repository=(
                EntityRepository(
                    [user],
                    key_name="user_id",
                )
            ),
            external_identity_repository=(
                IdentityRepository(
                    key_name="subject"
                )
            ),
            invitation_repository=(
                Repository(
                    key_name="invitation_id"
                )
            ),
            athlete_access_repository=(
                access_repository
            ),
            alpha_participation_consent_repository=(
                empty_repository
            ),
            training_coach_consent_repository=(
                empty_repository
            ),
            training_coach_usage_repository=(
                Repository(
                    key_name="usage_id"
                )
            ),
            authorization=(
                AthleteAuthorizationService(
                    access_repository
                )
            ),
            transaction_factory=(
                transaction_factory
            ),
        ).execute(
            user
        )

    assert not transaction_factory.entered