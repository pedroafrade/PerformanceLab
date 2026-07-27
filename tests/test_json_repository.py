from performancelab.athlete import Athlete
from performancelab.storage.json_repository import (
    JsonAthleteRepository,
)


def test_list_empty_repository(tmp_path):
    repository = JsonAthleteRepository(tmp_path)

    assert repository.list() == []


def test_list_returns_saved_athletes(tmp_path):
    repository = JsonAthleteRepository(tmp_path)

    athlete1 = Athlete(name="Pedro")
    athlete2 = Athlete(name="Maria")

    repository.save(athlete1)
    repository.save(athlete2)

    athletes = repository.list()

    ids = {athlete.athlete_id for athlete in athletes}

    assert ids == {
        athlete1.athlete_id,
        athlete2.athlete_id,
    }


def test_get_returns_requested_athlete(tmp_path):
    repository = JsonAthleteRepository(tmp_path)

    athlete1 = Athlete(name="Pedro")
    athlete2 = Athlete(name="Maria")

    repository.save(athlete1)
    repository.save(athlete2)

    loaded = repository.get(athlete2.athlete_id)

    assert loaded.athlete_id == athlete2.athlete_id
    assert loaded.name == athlete2.name


def test_delete_removes_athlete(tmp_path):
    repository = JsonAthleteRepository(tmp_path)

    athlete = Athlete(name="Pedro")

    repository.save(athlete)

    assert repository.exists(athlete.athlete_id)

    repository.delete(athlete.athlete_id)

    assert not repository.exists(athlete.athlete_id)
    assert repository.list() == []


def test_delete_unknown_athlete_raises(tmp_path):
    repository = JsonAthleteRepository(tmp_path)

    import pytest

    with pytest.raises(FileNotFoundError):
        repository.delete("unknown-athlete")