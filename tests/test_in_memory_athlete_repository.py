import pytest

from performancelab.athlete import (
    Athlete,
)
from performancelab.storage.athlete_repository import (
    AthleteRepository,
)
from performancelab.storage.in_memory_athlete_repository import (
    InMemoryAthleteRepository,
)


def test_implements_athlete_repository_contract():

    repository = (
        InMemoryAthleteRepository()
    )

    assert isinstance(
        repository,
        AthleteRepository,
    )


def test_starts_empty():

    repository = (
        InMemoryAthleteRepository()
    )

    assert repository.list() == []


def test_initializes_with_athletes():

    athlete = Athlete(
        name="Pedro"
    )

    repository = (
        InMemoryAthleteRepository(
            (
                athlete,
            )
        )
    )

    loaded = repository.get(
        athlete.athlete_id
    )

    assert (
        loaded.athlete_id
        == athlete.athlete_id
    )
    assert loaded.name == "Pedro"


def test_save_and_get_athlete():

    repository = (
        InMemoryAthleteRepository()
    )

    athlete = Athlete(
        name="Pedro"
    )

    result = repository.save(
        athlete
    )

    loaded = repository.get(
        athlete.athlete_id
    )

    assert result is None
    assert (
        loaded.athlete_id
        == athlete.athlete_id
    )
    assert loaded.name == "Pedro"


def test_get_returns_independent_copy():

    athlete = Athlete(
        name="Pedro"
    )

    repository = (
        InMemoryAthleteRepository(
            (
                athlete,
            )
        )
    )

    loaded = repository.get(
        athlete.athlete_id
    )

    loaded.name = "Changed"

    stored = repository.get(
        athlete.athlete_id
    )

    assert stored.name == "Pedro"


def test_changes_persist_only_after_save():

    athlete = Athlete(
        name="Pedro"
    )

    repository = (
        InMemoryAthleteRepository(
            (
                athlete,
            )
        )
    )

    loaded = repository.get(
        athlete.athlete_id
    )

    loaded.name = "Updated"

    repository.save(
        loaded
    )

    stored = repository.get(
        athlete.athlete_id
    )

    assert stored.name == "Updated"


def test_list_returns_independent_copies():

    athlete = Athlete(
        name="Pedro"
    )

    repository = (
        InMemoryAthleteRepository(
            (
                athlete,
            )
        )
    )

    listed = repository.list()

    listed[0].name = "Changed"

    stored = repository.get(
        athlete.athlete_id
    )

    assert stored.name == "Pedro"


def test_get_unknown_athlete_raises():

    repository = (
        InMemoryAthleteRepository()
    )

    with pytest.raises(
        FileNotFoundError,
        match="does not exist",
    ):
        repository.get(
            "unknown-athlete"
        )


def test_delete_removes_athlete():

    athlete = Athlete(
        name="Pedro"
    )

    repository = (
        InMemoryAthleteRepository(
            (
                athlete,
            )
        )
    )

    repository.delete(
        athlete.athlete_id
    )

    assert repository.list() == []

    with pytest.raises(
        FileNotFoundError,
    ):
        repository.get(
            athlete.athlete_id
        )


def test_delete_unknown_athlete_raises():

    repository = (
        InMemoryAthleteRepository()
    )

    with pytest.raises(
        FileNotFoundError,
        match="does not exist",
    ):
        repository.delete(
            "unknown-athlete"
        )