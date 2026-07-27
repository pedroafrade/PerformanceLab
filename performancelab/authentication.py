"""
PerformanceLab

Authentication service.
"""

from performancelab.identity import User
from performancelab.storage.user_repository import UserRepository


class AuthenticationService:
    """
    Manage user authentication.

    This initial implementation authenticates users by email only.
    Password validation can be introduced later without changing the
    application-facing interface.
    """

    def __init__(
        self,
        repository: UserRepository,
    ) -> None:
        self._repository = repository
        self._current_user: User | None = None

    @property
    def current_user(self) -> User | None:
        """
        Return the authenticated user.

        Returns None when no user is authenticated.
        """
        return self._current_user

    @property
    def is_authenticated(self) -> bool:
        """
        Return True when a user is authenticated.
        """
        return self._current_user is not None

    def login(self, email: str) -> User:
        """
        Authenticate a user by email.

        Raise KeyError when no user exists with the provided email.
        """
        user = self._repository.get_by_email(email)

        self._current_user = user

        return user

    def logout(self) -> None:
        """
        End the current authenticated session.
        """
        self._current_user = None