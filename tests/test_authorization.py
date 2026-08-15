import pytest

from performancelab.athlete_access import (
    AthleteAccessGrant,
)
from performancelab.authorization import (
    AthleteAuthorizationService,
)
from performancelab.storage.json_athlete_access_repository import (
    JsonAthleteAccessRepository,
)


def authorization_service(
    tmp_path,
    grants=(),
):

    repository = (
        JsonAthleteAccessRepository(
            tmp_path
        )
    )

    for grant in grants:

        repository.save(
            grant
        )

    return AthleteAuthorizationService(
        repository
    )


def test_owner_can_access_own_athlete(
    tmp_path,
):

    service = authorization_service(
        tmp_path,
        grants=(
            AthleteAccessGrant(
                user_id="user-123",
                athlete_id="athlete-123",
                permission="owner",
            ),
        ),
    )

    decision = service.decide(
        user_id="user-123",
        athlete_id="athlete-123",
    )

    assert decision.allowed is True
    assert (
        decision.permission
        == "owner"
    )
    assert (
        decision.reason
        == "authorized"
    )


def test_missing_grant_is_denied(
    tmp_path,
):

    service = authorization_service(
        tmp_path
    )

    decision = service.decide(
        user_id="user-123",
        athlete_id="athlete-123",
    )

    assert decision.allowed is False
    assert decision.permission is None

    assert (
        decision.reason
        == "grant_not_found"
    )


def test_user_cannot_access_another_athlete(
    tmp_path,
):

    service = authorization_service(
        tmp_path,
        grants=(
            AthleteAccessGrant(
                user_id="user-123",
                athlete_id="athlete-a",
                permission="owner",
            ),
        ),
    )

    decision = service.decide(
        user_id="user-123",
        athlete_id="athlete-b",
    )

    assert decision.allowed is False

    assert (
        decision.reason
        == "grant_not_found"
    )


def test_permission_can_be_restricted_to_owner(
    tmp_path,
):

    service = authorization_service(
        tmp_path,
        grants=(
            AthleteAccessGrant(
                user_id="coach-user",
                athlete_id="athlete-123",
                permission="coach",
            ),
        ),
    )

    decision = service.decide(
        user_id="coach-user",
        athlete_id="athlete-123",
        allowed_permissions=(
            "owner",
        ),
    )

    assert decision.allowed is False
    assert (
        decision.permission
        == "coach"
    )

    assert (
        decision.reason
        == "permission_not_allowed"
    )


def test_require_access_returns_grant(
    tmp_path,
):

    expected = AthleteAccessGrant(
        user_id="user-123",
        athlete_id="athlete-123",
        permission="owner",
    )

    service = authorization_service(
        tmp_path,
        grants=(
            expected,
        ),
    )

    result = service.require_access(
        user_id="user-123",
        athlete_id="athlete-123",
    )

    assert result == expected


def test_require_access_raises_when_denied(
    tmp_path,
):

    service = authorization_service(
        tmp_path
    )

    with pytest.raises(
        PermissionError,
        match="not authorized",
    ):
        service.require_access(
            user_id="user-123",
            athlete_id="athlete-123",
        )


def test_lists_only_authorized_athletes(
    tmp_path,
):

    service = authorization_service(
        tmp_path,
        grants=(
            AthleteAccessGrant(
                user_id="user-123",
                athlete_id="athlete-owner",
                permission="owner",
            ),
            AthleteAccessGrant(
                user_id="user-123",
                athlete_id="athlete-coached",
                permission="coach",
            ),
            AthleteAccessGrant(
                user_id="other-user",
                athlete_id="athlete-other",
                permission="owner",
            ),
        ),
    )

    assert (
        service.accessible_athlete_ids(
            user_id="user-123"
        )
        == (
            "athlete-coached",
            "athlete-owner",
        )
    )

    assert (
        service.accessible_athlete_ids(
            user_id="user-123",
            allowed_permissions=(
                "owner",
            ),
        )
        == (
            "athlete-owner",
        )
    )


def test_rejects_empty_permission_collection(
    tmp_path,
):

    service = authorization_service(
        tmp_path
    )

    with pytest.raises(
        ValueError,
        match="cannot be empty",
    ):
        service.decide(
            user_id="user-123",
            athlete_id="athlete-123",
            allowed_permissions=(),
        )


def test_rejects_permission_string(
    tmp_path,
):

    service = authorization_service(
        tmp_path
    )

    with pytest.raises(
        TypeError,
        match="not a string",
    ):
        service.decide(
            user_id="user-123",
            athlete_id="athlete-123",
            allowed_permissions="owner",
        )