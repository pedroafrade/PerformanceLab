"""
PerformanceLab

Critical two-user private alpha isolation tests.
"""

import pytest

from performancelab.application import (
    LoadActiveAthlete,
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
    User,
)
from performancelab.storage.in_memory_athlete_repository import (
    InMemoryAthleteRepository,
)
from performancelab.storage.json_athlete_access_repository import (
    JsonAthleteAccessRepository,
)


def private_alpha_context(tmp_path):

    athlete_a = Athlete(
        name="Athlete A",
    )

    athlete_b = Athlete(
        name="Athlete B",
    )

    user_a = User(
        email="athlete-a@example.com",
        athlete_id=athlete_a.athlete_id,
        user_id="user-a",
    )

    user_b = User(
        email="athlete-b@example.com",
        athlete_id=athlete_b.athlete_id,
        user_id="user-b",
    )

    athlete_repository = (
        InMemoryAthleteRepository(
            (
                athlete_a,
                athlete_b,
            )
        )
    )

    access_repository = (
        JsonAthleteAccessRepository(
            tmp_path / "athlete_access"
        )
    )

    access_repository.save(
        AthleteAccessGrant(
            user_id=user_a.user_id,
            athlete_id=athlete_a.athlete_id,
            permission="owner",
        )
    )

    access_repository.save(
        AthleteAccessGrant(
            user_id=user_b.user_id,
            athlete_id=athlete_b.athlete_id,
            permission="owner",
        )
    )

    authorization = (
        AthleteAuthorizationService(
            access_repository
        )
    )

    loader = LoadActiveAthlete(
        repository=athlete_repository,
        authorization=authorization,
    )

    return (
        athlete_a,
        athlete_b,
        user_a,
        user_b,
        athlete_repository,
        authorization,
        loader,
    )


def test_two_users_load_only_their_own_athletes(
    tmp_path,
):

    (
        athlete_a,
        athlete_b,
        user_a,
        user_b,
        _,
        _,
        loader,
    ) = private_alpha_context(tmp_path)

    result_a = loader.execute(user_a)
    result_b = loader.execute(user_b)

    assert (
        result_a.athlete.athlete_id
        == athlete_a.athlete_id
    )

    assert (
        result_b.athlete.athlete_id
        == athlete_b.athlete_id
    )

    assert (
        result_a.athlete.athlete_id
        != result_b.athlete.athlete_id
    )


def test_each_user_lists_only_their_accessible_athlete(
    tmp_path,
):

    (
        athlete_a,
        athlete_b,
        user_a,
        user_b,
        _,
        authorization,
        _,
    ) = private_alpha_context(tmp_path)

    assert (
        authorization.accessible_athlete_ids(
            user_id=user_a.user_id,
            allowed_permissions=("owner",),
        )
        == (athlete_a.athlete_id,)
    )

    assert (
        authorization.accessible_athlete_ids(
            user_id=user_b.user_id,
            allowed_permissions=("owner",),
        )
        == (athlete_b.athlete_id,)
    )


def test_tampered_athlete_id_is_denied(
    tmp_path,
):

    (
        _,
        athlete_b,
        user_a,
        user_b,
        _,
        _,
        loader,
    ) = private_alpha_context(tmp_path)

    user_a.athlete_id = athlete_b.athlete_id

    with pytest.raises(
        PermissionError,
        match="not authorized",
    ):

        loader.execute(user_a)

    result_b = loader.execute(user_b)

    assert (
        result_b.athlete.athlete_id
        == athlete_b.athlete_id
    )


def test_failed_cross_access_does_not_change_data(
    tmp_path,
):

    (
        athlete_a,
        athlete_b,
        user_a,
        _,
        athlete_repository,
        _,
        loader,
    ) = private_alpha_context(tmp_path)

    before_a = athlete_repository.get(
        athlete_a.athlete_id
    )

    before_b = athlete_repository.get(
        athlete_b.athlete_id
    )

    user_a.athlete_id = athlete_b.athlete_id

    with pytest.raises(PermissionError):

        loader.execute(user_a)

    after_a = athlete_repository.get(
        athlete_a.athlete_id
    )

    after_b = athlete_repository.get(
        athlete_b.athlete_id
    )

    assert after_a.name == before_a.name
    assert after_b.name == before_b.name
    assert (
        after_a.athlete_id
        != after_b.athlete_id
    )