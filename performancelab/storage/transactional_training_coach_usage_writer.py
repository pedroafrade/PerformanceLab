"""Persist one Training Coach usage event in its own short transaction."""

from sqlalchemy.engine import Engine

from performancelab.storage.postgresql_training_coach_usage_repository import (
    PostgreSQLTrainingCoachUsageRepository,
)


class TransactionalTrainingCoachUsageWriter:
    """Avoid holding the application's main transaction across provider calls."""

    def __init__(self, engine: Engine):
        if not isinstance(engine, Engine):
            raise TypeError("A SQLAlchemy Engine is required")
        self.engine = engine

    def save(self, event):
        with self.engine.begin() as connection:
            PostgreSQLTrainingCoachUsageRepository(connection).save(event)
