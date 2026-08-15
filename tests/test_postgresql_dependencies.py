"""
PostgreSQL persistence dependency smoke tests.
"""

from importlib.metadata import (
    version,
)

import alembic
import psycopg
import sqlalchemy


def major_version(
    distribution: str,
) -> int:

    value = version(
        distribution
    )

    return int(
        value.split(
            ".",
            maxsplit=1,
        )[0]
    )


def test_postgresql_stack_is_importable():

    assert sqlalchemy is not None
    assert alembic is not None
    assert psycopg is not None


def test_postgresql_stack_uses_supported_major_versions():

    assert (
        major_version(
            "SQLAlchemy"
        )
        == 2
    )

    assert (
        major_version(
            "alembic"
        )
        == 1
    )

    assert (
        major_version(
            "psycopg"
        )
        == 3
    )