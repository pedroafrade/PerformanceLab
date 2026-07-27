import pytest

from performancelab.identity import User
from performancelab.storage.json_user_repository import (
    JsonUserRepository,
)


def test_list_empty_repository(tmp_path):
    repository = JsonUserRepository(tmp_path)

    assert repository.list() == []


def test_save_and_get_user(tmp_path):
    repository = JsonUserRepository(tmp_path)

    user = User(
        email="pedro@example.com",
        role="athlete",
        athlete_id="athlete-123",
    )

    repository.save(user)

    loaded = repository.get(user.user_id)

    assert loaded.user_id == user.user_id
    assert loaded.email == user.email
    assert loaded.role == user.role
    assert loaded.athlete_id == user.athlete_id


def test_save_creates_json_file(tmp_path):
    repository = JsonUserRepository(tmp_path)

    user = User(
        email="pedro@example.com",
        role="athlete",
        athlete_id="athlete-123",
    )

    repository.save(user)

    path = tmp_path / f"{user.user_id}.json"

    assert path.exists()


def test_get_by_email_returns_user(tmp_path):
    repository = JsonUserRepository(tmp_path)

    user = User(
        email="pedro@example.com",
        role="athlete",
        athlete_id="athlete-123",
    )

    repository.save(user)

    loaded = repository.get_by_email(
        "PEDRO@EXAMPLE.COM"
    )

    assert loaded.user_id == user.user_id


def test_get_unknown_user_raises(tmp_path):
    repository = JsonUserRepository(tmp_path)

    with pytest.raises(
        KeyError,
        match="User not found",
    ):
        repository.get("unknown-user")


def test_get_by_unknown_email_raises(tmp_path):
    repository = JsonUserRepository(tmp_path)

    with pytest.raises(
        KeyError,
        match="User not found",
    ):
        repository.get_by_email(
            "unknown@example.com"
        )


def test_list_returns_saved_users(tmp_path):
    repository = JsonUserRepository(tmp_path)

    user1 = User(
        email="pedro@example.com",
        role="athlete",
        athlete_id="athlete-123",
    )

    user2 = User(
        email="coach@example.com",
        role="coach",
    )

    repository.save(user1)
    repository.save(user2)

    users = repository.list()

    assert len(users) == 2
    assert {
        user.user_id
        for user in users
    } == {
        user1.user_id,
        user2.user_id,
    }


def test_delete_removes_user(tmp_path):
    repository = JsonUserRepository(tmp_path)

    user = User(
        email="pedro@example.com",
        role="athlete",
        athlete_id="athlete-123",
    )

    repository.save(user)
    repository.delete(user.user_id)

    assert repository.list() == []

    with pytest.raises(KeyError):
        repository.get(user.user_id)


def test_delete_unknown_user_raises(tmp_path):
    repository = JsonUserRepository(tmp_path)

    with pytest.raises(
        KeyError,
        match="User not found",
    ):
        repository.delete("unknown-user")


def test_save_updates_existing_user(tmp_path):
    repository = JsonUserRepository(tmp_path)

    user = User(
        email="old@example.com",
        role="athlete",
        athlete_id="athlete-123",
    )

    repository.save(user)

    user.email = "new@example.com"

    repository.save(user)

    users = repository.list()

    assert len(users) == 1
    assert users[0].email == "new@example.com"