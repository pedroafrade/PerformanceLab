from performancelab.authentication import AuthenticationService
from performancelab.identity import User


def test_authentication_starts_without_user():
    auth = AuthenticationService()

    assert auth.current_user is None
    assert auth.is_authenticated is False


def test_login_authenticates_user():
    user = User(
        email="pedro@example.com",
        role="athlete",
        athlete_id="athlete-123",
    )

    auth = AuthenticationService()

    auth.login(user)

    assert auth.current_user is user
    assert auth.is_authenticated is True


def test_logout_removes_authenticated_user():
    user = User(
        email="pedro@example.com",
        role="athlete",
        athlete_id="athlete-123",
    )

    auth = AuthenticationService()

    auth.login(user)
    auth.logout()

    assert auth.current_user is None
    assert auth.is_authenticated is False


def test_login_rejects_invalid_object():
    auth = AuthenticationService()

    try:
        auth.login("pedro")
    except TypeError as error:
        assert str(error) == (
            "AuthenticationService.login expects a User instance."
        )
    else:
        raise AssertionError(
            "Expected AuthenticationService.login to raise TypeError."
        )