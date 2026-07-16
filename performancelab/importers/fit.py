"""
PerformanceLab

FIT Importer

Imports a FIT activity as a Workout.
"""

from datetime import date, datetime, timedelta
from io import BytesIO
from pathlib import Path

import fitdecode

from performancelab import Workout

from .base import (
    ImporterError,
    ImporterSource,
    InvalidActivityError,
    WorkoutImporter,
)


# ======================================================
# FIT Importer
# ======================================================

class FITImporter(WorkoutImporter):

    # ======================================================

    def __init__(
        self,
        default_sport: str = "Unknown",
    ):

        self.default_sport = default_sport

    # ======================================================
    # Public API
    # ======================================================

    def read(
        self,
        source: ImporterSource,
    ) -> Workout:

        content = self._read_source(source)

        try:

            messages = self._read_messages(content)

        except Exception as error:

            raise ImporterError(
                "Unable to parse FIT data."
            ) from error

        records = messages["records"]
        sessions = messages["sessions"]
        activities = messages["activities"]

        if not records and not sessions:

            raise InvalidActivityError(
                "The FIT file does not contain "
                "activity data."
            )

        session = sessions[0] if sessions else {}
        activity = activities[0] if activities else {}

        workout = Workout()

        workout.info.source = "fit"
        workout.info.title = self._title(session)
        workout.info.sport = self._sport(session)
        workout.info.date = self._start_date(
            records,
            session,
            activity,
        )
        workout.info.distance = self._distance(
            records,
            session,
        )
        workout.info.duration = self._duration(
            records,
            session,
        )
        workout.info.elevation_gain = (
            self._elevation_gain(
                records,
                session,
            )
        )

        route = self._route(records)

        if route:

            workout.sensors.add(
                "gps",
                route,
            )

        heart_rate = self._heart_rate(records)

        if heart_rate:

            workout.sensors.add(
                "heart_rate",
                heart_rate,
            )

        power = self._power(records)

        if power:

            workout.sensors.add(
                "power",
                power,
            )

        cadence = self._cadence(records)

        if cadence:

            workout.sensors.add(
                "cadence",
                cadence,
            )

        return workout

    # ======================================================
    # Source reading
    # ======================================================

    @staticmethod
    def _read_source(
        source: ImporterSource,
    ) -> bytes:

        if isinstance(source, Path):

            return source.read_bytes()

        if isinstance(source, (bytes, bytearray)):

            return bytes(source)

        if isinstance(source, str):

            path = Path(source)

            if not path.exists():

                raise FileNotFoundError(
                    f"FIT file not found: {path}"
                )

            return path.read_bytes()

        read = getattr(source, "read", None)

        if read is None:

            raise TypeError(
                "source must be a path, bytes "
                "or a readable binary file object"
            )

        content = read()

        if isinstance(content, str):

            raise TypeError(
                "FIT files must be read as binary data."
            )

        if not isinstance(
            content,
            (bytes, bytearray),
        ):

            raise TypeError(
                "The supplied file object did not "
                "return bytes."
            )

        return bytes(content)

    # ======================================================
    # Message reading
    # ======================================================

    @staticmethod
    def _read_messages(content: bytes) -> dict:

        result = {
            "records": [],
            "sessions": [],
            "activities": [],
        }

        with fitdecode.FitReader(
            BytesIO(content)
        ) as fit:

            for frame in fit:

                if not isinstance(
                    frame,
                    fitdecode.FitDataMessage,
                ):

                    continue

                data = {
                    field.name: field.value
                    for field in frame.fields
                }

                if frame.name == "record":

                    result["records"].append(data)

                elif frame.name == "session":

                    result["sessions"].append(data)

                elif frame.name == "activity":

                    result["activities"].append(data)

        return result

    # ======================================================
    # Title
    # ======================================================

    @staticmethod
    def _title(session: dict) -> str:

        sport = session.get("sport")

        if sport:

            return str(sport).replace(
                "_",
                " ",
            ).title()

        return ""

    # ======================================================
    # Sport
    # ======================================================

    def _sport(self, session: dict) -> str:

        value = session.get("sport")

        if value is None:

            return self.default_sport

        normalized = str(value).strip().lower()

        aliases = {
            "running": "Running",
            "cycling": "Cycling",
            "swimming": "Swimming",
            "walking": "Walking",
            "hiking": "Hiking",
            "strength_training": "Strength",
        }

        return aliases.get(
            normalized,
            normalized.replace(
                "_",
                " ",
            ).title(),
        )

    # ======================================================
    # Start date
    # ======================================================

    @staticmethod
    def _start_date(
        records: list[dict],
        session: dict,
        activity: dict,
    ) -> date | None:

        candidates = [
            session.get("start_time"),
            activity.get("timestamp"),
        ]

        candidates.extend(
            record.get("timestamp")
            for record in records
        )

        times = [
            value
            for value in candidates
            if isinstance(value, datetime)
        ]

        if not times:

            return None

        return min(times).date()

    # ======================================================
    # Distance
    # ======================================================

    @staticmethod
    def _distance(
        records: list[dict],
        session: dict,
    ) -> float | None:

        total_distance = session.get(
            "total_distance"
        )

        if total_distance is not None:

            return float(total_distance) / 1000

        distances = [
            record.get("distance")
            for record in records
            if record.get("distance") is not None
        ]

        if not distances:

            return None

        return float(max(distances)) / 1000

    # ======================================================
    # Duration
    # ======================================================

    @staticmethod
    def _duration(
        records: list[dict],
        session: dict,
    ) -> timedelta | None:

        elapsed = session.get(
            "total_elapsed_time"
        )

        if elapsed is not None and elapsed > 0:

            return timedelta(
                seconds=float(elapsed)
            )

        timestamps = sorted(
            record["timestamp"]
            for record in records
            if isinstance(
                record.get("timestamp"),
                datetime,
            )
        )

        if len(timestamps) < 2:

            return None

        result = (
            timestamps[-1]
            - timestamps[0]
        )

        if result.total_seconds() <= 0:

            return None

        return result

    # ======================================================
    # Elevation gain
    # ======================================================

    @staticmethod
    def _elevation_gain(
        records: list[dict],
        session: dict,
    ) -> float | None:

        total_ascent = session.get(
            "total_ascent"
        )

        if total_ascent is not None:

            return max(
                0.0,
                float(total_ascent),
            )

        elevations = [
            record.get(
                "enhanced_altitude",
                record.get("altitude"),
            )
            for record in records
        ]

        elevations = [
            float(value)
            for value in elevations
            if value is not None
        ]

        if len(elevations) < 2:

            return None

        gain = 0.0

        for previous, current in zip(
            elevations,
            elevations[1:],
        ):

            difference = current - previous

            if difference > 0:

                gain += difference

        return gain

    # ======================================================
    # Coordinates
    # ======================================================

    @staticmethod
    def _semicircles_to_degrees(
        value,
    ) -> float | None:

        if value is None:

            return None

        return float(value) * (
            180 / 2**31
        )

    # ======================================================
    # Route
    # ======================================================

    def _route(
        self,
        records: list[dict],
    ) -> list[dict]:

        route = []

        for record in records:

            latitude = (
                self._semicircles_to_degrees(
                    record.get(
                        "position_lat"
                    )
                )
            )

            longitude = (
                self._semicircles_to_degrees(
                    record.get(
                        "position_long"
                    )
                )
            )

            if latitude is None or longitude is None:

                continue

            elevation = record.get(
                "enhanced_altitude",
                record.get("altitude"),
            )

            timestamp = record.get("timestamp")

            route.append(
                {
                    "latitude": latitude,
                    "longitude": longitude,
                    "elevation": elevation,
                    "time": (
                        timestamp.isoformat()
                        if isinstance(
                            timestamp,
                            datetime,
                        )
                        else None
                    ),
                }
            )

        return route

    # ======================================================
    # Heart rate
    # ======================================================

    @staticmethod
    def _heart_rate(
        records: list[dict],
    ) -> list[dict]:

        return [
            {
                "time": (
                    record["timestamp"].isoformat()
                    if isinstance(
                        record.get("timestamp"),
                        datetime,
                    )
                    else None
                ),
                "value": record["heart_rate"],
            }
            for record in records
            if record.get("heart_rate") is not None
        ]

    # ======================================================
    # Power
    # ======================================================

    @staticmethod
    def _power(
        records: list[dict],
    ) -> list[dict]:

        return [
            {
                "time": (
                    record["timestamp"].isoformat()
                    if isinstance(
                        record.get("timestamp"),
                        datetime,
                    )
                    else None
                ),
                "value": record["power"],
            }
            for record in records
            if record.get("power") is not None
        ]

    # ======================================================
    # Cadence
    # ======================================================

    @staticmethod
    def _cadence(
        records: list[dict],
    ) -> list[dict]:

        return [
            {
                "time": (
                    record["timestamp"].isoformat()
                    if isinstance(
                        record.get("timestamp"),
                        datetime,
                    )
                    else None
                ),
                "value": record["cadence"],
            }
            for record in records
            if record.get("cadence") is not None
        ]

    # ======================================================

    def __repr__(self):

        return (
            f"FITImporter("
            f"default_sport='{self.default_sport}')"
        )