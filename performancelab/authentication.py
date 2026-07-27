"""
PerformanceLab

Authentication service.
"""

from performancelab.identity import User


class AuthenticationService:
    """
    Manage the currently authenticated user.

    This initial implementation stores authentication state only in memory.
    Passwords, tokens and persistent sessions can be added later without
    changing the rest of the application.
    """

    def __init__(self) -> None:
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

    def login(self, user: User) -> None:
        """
        Authenticate a user.

        This initial version receives an already validated User object.
        """
        if not isinstance(user, User):
            raise TypeError(
                "AuthenticationService.login expects a User instance."
            )

        self._current_user = user

    def logout(self) -> None:
        """
        End the current authenticated session.
        """
        self._current_user = None