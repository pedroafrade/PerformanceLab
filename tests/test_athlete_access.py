import pytest

from performancelab.athlete_access import (
    AthleteAccessGrant,
)
from performancelab.storage.json_athlete_access_repository import (
    JsonAthleteAccessRepository,
)


def grant(
    *,
    user_id="user-123",
    athlete_id="athlete-123",
    permission="owner",
):

    return AthleteAccessGrant(
        user_id=user_id,
        athlete_id=athlete_id,
        permission=permission,
    )


def test_normalizes_access_grant():

    access = AthleteAccessGrant(
        user_id=" user-123 ",
        athlete_id=" athlete-123 ",
        permission="owner",
    )

    assert access.user_id == (
        "user-123"
    )
    assert access.athlete_id == (
        "athlete-123"
    )
    assert access.grant_key == (
        "user-123",
        "athlete-123",
    )


def test_rejects_invalid_permission():

    with pytest.raises(
        ValueError,
        match="permission",
    ):
        grant(
            permission="administrator"
        )


def test_owner_and_coach_properties():

    owner = grant(
        permission="owner"
    )

    coach = grant(
        permission="coach"
    )

    assert owner.is_owner is True
    assert owner.is_coach is False
    assert coach.is_owner is False
    assert coach.is_coach is True


def test_repository_round_trip(
    tmp_path,
):

    repository = (
        JsonAthleteAccessRepository(
            tmp_path
        )
    )

    access = grant()

    repository.save(
        access
    )

    loaded = repository.get(
        access.user_id,
        access.athlete_id,
    )

    assert loaded == access


def test_repeated_save_is_idempotent(
    tmp_path,
):

    repository = (
        JsonAthleteAccessRepository(
            tmp_path
        )
    )

    access = grant()

    repository.save(
        access
    )
    repository.save(
        access
    )

    assert repository.list() == [
        access
    ]


def test_permission_cannot_change_silently(
    tmp_path,
):

    repository = (
        JsonAthleteAccessRepository(
            tmp_path
        )
    )

    repository.save(
        grant(
            permission="owner"
        )
    )

    with pytest.raises(
        ValueError,
        match="cannot be changed silently",
    ):
        repository.save(
            grant(
                permission="coach"
            )
        )


def test_lists_grants_for_user(
    tmp_path,
):

    repository = (
        JsonAthleteAccessRepository(
            tmp_path
        )
    )

    first = grant(
        athlete_id="athlete-1"
    )
    second = grant(
        athlete_id="athlete-2"
    )
    unrelated = grant(
        user_id="another-user",
        athlete_id="athlete-3",
    )

    repository.save(
        first
    )
    repository.save(
        second
    )
    repository.save(
        unrelated
    )

    assert (
        repository.list_for_user(
            "user-123"
        )
        == [
            first,
            second,
        ]
    )


def test_lists_grants_for_athlete(
    tmp_path,
):

    repository = (
        JsonAthleteAccessRepository(
            tmp_path
        )
    )

    owner = grant(
        user_id="owner-user",
        permission="owner",
    )
    coach = grant(
        user_id="coach-user",
        permission="coach",
    )
    unrelated = grant(
        user_id="other-user",
        athlete_id="another-athlete",
    )

    repository.save(
        owner
    )
    repository.save(
        coach
    )
    repository.save(
        unrelated
    )

    assert (
        repository.list_for_athlete(
            "athlete-123"
        )
        == [
            coach,
            owner,
        ]
    )


def test_delete_removes_grant(
    tmp_path,
):

    repository = (
        JsonAthleteAccessRepository(
            tmp_path
        )
    )

    access = grant()

    repository.save(
        access
    )

    repository.delete(
        access.user_id,
        access.athlete_id,
    )

    with pytest.raises(
        KeyError,
        match="does not exist",
    ):
        repository.get(
            access.user_id,
            access.athlete_id,
        )


def test_unknown_grant_raises(
    tmp_path,
):

    repository = (
        JsonAthleteAccessRepository(
            tmp_path
        )
    )

    with pytest.raises(
        KeyError,
        match="does not exist",
    ):
        repository.get(
            "unknown-user",
            "unknown-athlete",
        )