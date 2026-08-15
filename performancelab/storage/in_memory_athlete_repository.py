"""
PerformanceLab

In-memory athlete repository.

Provides isolated Athlete persistence for application
service tests.
"""

from collections.abc import (
    Iterable,
)

from performancelab.athlete import (
    Athlete,
)
from performancelab.storage.json import (
    athlete_from_dict,
    athlete_to_dict,
)


class InMemoryAthleteRepository:
    """
    Store serialized Athlete snapshots in memory.

    This implementation is intended for tests and local
    application-service composition. Returned athletes are
    reconstructed snapshots, preventing changes from
    becoming persistent before save() is called.
    """

    def __init__(
        self,
        athletes: Iterable[Athlete] = (),
    ) -> None:

        self._athletes: dict[
            str,
            dict[str, object],
        ] = {}

        for athlete in athletes:
            self.save(
                athlete
            )

    def get(
        self,
        athlete_id: str,
    ) -> Athlete:
        """
        Reconstruct and return the requested athlete.
        """

        try:
            snapshot = self._athletes[
                athlete_id
            ]

        except KeyError as error:
            raise FileNotFoundError(
                f"Athlete {athlete_id!r} does not exist"
            ) from error

        return athlete_from_dict(
            snapshot
        )

    def list(
        self,
    ) -> list[Athlete]:
        """
        Reconstruct and return every stored athlete.
        """

        return [
            athlete_from_dict(
                snapshot
            )
            for snapshot in (
                self._athletes.values()
            )
        ]

    def save(
        self,
        athlete: Athlete,
    ) -> None:
        """
        Save a serialized snapshot of an athlete.
        """

        self._athletes[
            athlete.athlete_id
        ] = athlete_to_dict(
            athlete
        )

    def delete(
        self,
        athlete_id: str,
    ) -> None:
        """
        Delete an athlete by ID.
        """

        if (
            athlete_id
            not in self._athletes
        ):
            raise FileNotFoundError(
                f"Athlete {athlete_id!r} does not exist"
            )

        del self._athletes[
            athlete_id
        ]