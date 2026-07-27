import pytest

from performancelab.authentication import AuthenticationService
from performancelab.identity import User
from performancelab.storage.json_user_repository import (
    JsonUserRepository,
)


def test_authentication_starts_without_user(tmp_path):
    repository = JsonUserRepository(tmp_path)
    auth = AuthenticationService(repository)

    assert auth.current_user is None
    assert auth.is_authenticated is False


def test_login_authenticates_user_by_email(tmp_path):
    repository = JsonUserRepository(tmp_path)

    user = User(
        email="pedro@example.com",
        role="athlete",
        athlete_id="athlete-123",
    )

    repository.save(user)

    auth = AuthenticationService(repository)

    logged_in_user = auth.login(
        "pedro@example.com"
    )

    assert logged_in_user.user_id == user.user_id
    assert auth.current_user is logged_in_user
    assert auth.is_authenticated is True


def test_login_is_case_insensitive(tmp_path):
    repository = JsonUserRepository(tmp_path)

    user = User(
        email="pedro@example.com",
        role="athlete",
        athlete_id="athlete-123",
    )

    repository.save(user)

    auth = AuthenticationService(repository)

    logged_in_user = auth.login(
        "PEDRO@EXAMPLE.COM"
    )

    assert logged_in_user.user_id == user.user_id


def test_login_unknown_user_raises(tmp_path):
    repository = JsonUserRepository(tmp_path)
    auth = AuthenticationService(repository)

    with pytest.raises(
        KeyError,
        match="User not found",
    ):
        auth.login("unknown@example.com")

    assert auth.current_user is None
    assert auth.is_authenticated is False


def test_logout_removes_authenticated_user(tmp_path):
    repository = JsonUserRepository(tmp_path)

    user = User(
        email="pedro@example.com",
        role="athlete",
        athlete_id="athlete-123",
    )

    repository.save(user)

    auth = AuthenticationService(repository)

    auth.login("pedro@example.com")
    auth.logout()

    assert auth.current_user is None
    assert auth.is_authenticated is False