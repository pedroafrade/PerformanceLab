"""
Tests for the PostgreSQL athlete snapshot repository.
"""

import pytest

from sqlalchemy import (
    create_engine,
    func,
    select,
)
from sqlalchemy.dialects.postgresql import (
    JSONB,
)
from sqlalchemy.ext.compiler import (
    compiles,
)

from performancelab.athlete import (
    Athlete,
)
from performancelab.storage.athlete_repository import (
    AthleteRepository,
)
from performancelab.storage.postgresql_athlete_repository import (
    PostgreSQLAthleteRepository,
)
from performancelab.storage.postgresql_schema import (
    athlete_snapshots,
    athletes,
    metadata,
)


@compiles(
    JSONB,
    "sqlite",
)
def compile_jsonb_for_sqlite(
    element,
    compiler,
    **kwargs,
):
    """
    Allow isolated repository tests to use SQLite in memory.

    Production continues to compile this column as PostgreSQL
    JSONB.
    """

    return "JSON"


@pytest.fixture
def connection():

    engine = create_engine(
        "sqlite+pysqlite:///:memory:"
    )

    metadata.create_all(
        engine,
        tables=(
            athletes,
            athlete_snapshots,
        ),
    )

    with engine.connect() as connection:

        yield connection

        connection.rollback()

    engine.dispose()


@pytest.fixture
def repository(
    connection,
):

    return PostgreSQLAthleteRepository(
        connection
    )


def test_implements_athlete_repository_contract(
    repository,
):

    assert isinstance(
        repository,
        AthleteRepository,
    )


def test_saves_and_gets_complete_athlete(
    repository,
):

    athlete = Athlete(
        athlete_id="athlete-1",
        name="Pedro",
        weight=70,
        ftp=220,
    )

    repository.save(
        athlete
    )

    loaded = repository.get(
        " athlete-1 "
    )

    assert (
        loaded.athlete_id
        == "athlete-1"
    )
    assert loaded.name == "Pedro"
    assert loaded.weight == 70
    assert loaded.ftp == 220


def test_first_save_creates_version_one(
    connection,
    repository,
):

    repository.save(
        Athlete(
            athlete_id="athlete-1",
            name="Pedro",
        )
    )

    current_version = (
        connection.execute(
            select(
                athletes.c.current_version
            ).where(
                athletes.c.athlete_id
                == "athlete-1"
            )
        ).scalar_one()
    )

    versions = connection.execute(
        select(
            athlete_snapshots.c.version
        ).where(
            athlete_snapshots.c.athlete_id
            == "athlete-1"
        )
    ).scalars().all()

    assert current_version == 1
    assert versions == [
        1,
    ]


def test_subsequent_save_preserves_previous_snapshot(
    connection,
    repository,
):

    athlete = Athlete(
        athlete_id="athlete-1",
        name="Pedro",
        weight=70,
    )

    repository.save(
        athlete
    )

    athlete.weight = 69

    repository.save(
        athlete
    )

    current_version = (
        connection.execute(
            select(
                athletes.c.current_version
            ).where(
                athletes.c.athlete_id
                == "athlete-1"
            )
        ).scalar_one()
    )

    versions = connection.execute(
        select(
            athlete_snapshots.c.version
        ).where(
            athlete_snapshots.c.athlete_id
            == "athlete-1"
        ).order_by(
            athlete_snapshots.c.version
        )
    ).scalars().all()

    assert current_version == 2
    assert versions == [
        1,
        2,
    ]

    assert (
        repository.get(
            "athlete-1"
        ).weight
        == 69
    )


def test_list_returns_only_current_athlete_versions(
    repository,
):

    first = Athlete(
        athlete_id="athlete-2",
        name="Pedro",
        weight=70,
    )
    second = Athlete(
        athlete_id="athlete-1",
        name="Ana",
        weight=60,
    )

    repository.save(
        first
    )
    repository.save(
        second
    )

    first.weight = 69

    repository.save(
        first
    )

    loaded = repository.list()

    assert [
        athlete.athlete_id
        for athlete in loaded
    ] == [
        "athlete-1",
        "athlete-2",
    ]

    assert [
        athlete.weight
        for athlete in loaded
    ] == [
        60,
        69,
    ]


def test_delete_removes_athlete_and_snapshots(
    connection,
    repository,
):

    repository.save(
        Athlete(
            athlete_id="athlete-1",
            name="Pedro",
        )
    )

    repository.delete(
        "athlete-1"
    )

    athlete_count = (
        connection.execute(
            select(
                func.count()
            ).select_from(
                athletes
            )
        ).scalar_one()
    )

    snapshot_count = (
        connection.execute(
            select(
                func.count()
            ).select_from(
                athlete_snapshots
            )
        ).scalar_one()
    )

    assert athlete_count == 0
    assert snapshot_count == 0


def test_get_unknown_athlete_raises(
    repository,
):

    with pytest.raises(
        FileNotFoundError,
        match="does not exist",
    ):
        repository.get(
            "unknown-athlete"
        )


def test_delete_unknown_athlete_raises(
    repository,
):

    with pytest.raises(
        FileNotFoundError,
        match="does not exist",
    ):
        repository.delete(
            "unknown-athlete"
        )


def test_empty_repository_returns_empty_list(
    repository,
):

    assert repository.list() == []


def test_rejects_non_athlete_value(
    repository,
):

    with pytest.raises(
        TypeError,
        match=(
            "athlete must be an Athlete"
        ),
    ):
        repository.save(
            {
                "name": "Not an athlete",
            }
        )