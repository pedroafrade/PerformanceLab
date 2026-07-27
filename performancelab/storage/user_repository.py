"""
PerformanceLab

User repository contract.
"""

from typing import Protocol

from performancelab.identity import User


class UserRepository(Protocol):
    """
    Define the persistence operations available for users.
    """

    def save(self, user: User) -> None:
        """
        Save a user.
        """
        ...

    def get(self, user_id: str) -> User:
        """
        Return a user by ID.

        Raise KeyError when the user does not exist.
        """
        ...

    def get_by_email(self, email: str) -> User:
        """
        Return a user by email address.

        Raise KeyError when the user does not exist.
        """
        ...

    def list(self) -> list[User]:
        """
        Return all users.
        """
        ...

    def delete(self, user_id: str) -> None:
        """
        Delete a user.

        Raise KeyError when the user does not exist.
        """
        ...