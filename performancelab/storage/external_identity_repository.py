"""
PerformanceLab

External identity repository contract.
"""

from typing import (
    Protocol,
)

from performancelab.identity import (
    ExternalIdentityLink,
)


class ExternalIdentityRepository(
    Protocol
):
    """
    Persistence operations for external identity links.
    """

    def get(
        self,
        issuer: str,
        subject: str,
    ) -> ExternalIdentityLink:
        """
        Return the link for one provider identity.

        Raise KeyError when no link exists.
        """

        ...

    def save(
        self,
        link: ExternalIdentityLink,
    ) -> None:
        """
        Persist a link without allowing reassignment.
        """

        ...

    def delete(
        self,
        issuer: str,
        subject: str,
    ) -> None:
        """
        Delete one external identity link.
        """

        ...

    def list(
        self,
    ) -> list[
        ExternalIdentityLink
    ]:
        """
        Return every stored link.
        """

        ...