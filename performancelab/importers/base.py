"""
PerformanceLab

Importer Base

Shared interfaces and errors for workout importers.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO, TextIO

from performancelab import Workout


# ======================================================
# Import errors
# ======================================================

class ImporterError(Exception):

    """
    Base exception raised by PerformanceLab importers.
    """


# ======================================================

class UnsupportedSourceError(ImporterError):

    """
    Raised when an importer cannot read the supplied source.
    """


# ======================================================

class InvalidActivityError(ImporterError):

    """
    Raised when a source does not contain a valid activity.
    """


# ======================================================
# Source types
# ======================================================

ImporterSource = (
    str
    | Path
    | bytes
    | bytearray
    | TextIO
    | BinaryIO
)


# ======================================================
# Workout importer
# ======================================================

class WorkoutImporter(ABC):

    """
    Base interface for importers that produce one Workout.
    """

    # ======================================================

    @abstractmethod
    def read(
        self,
        source: ImporterSource,
    ) -> Workout:

        """
        Reads a source and returns one Workout.
        """

        raise NotImplementedError