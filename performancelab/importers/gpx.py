"""
PerformanceLab

GPX Importer

Imports a GPX activity as a Workout.
"""

from datetime import date, timedelta
from pathlib import Path

import gpxpy

from performancelab import Workout

from .base import (
    ImporterError,
    ImporterSource,
    InvalidActivityError,
    WorkoutImporter,
)


# ======================================================
# GPX Importer
# ======================================================

class GPXImporter(WorkoutImporter):

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

            gpx = gpxpy.parse(content)

        except Exception as error:

            raise ImporterError(

                "Unable to parse GPX data."

            ) from error

        points = self._points(gpx)

        if not points:

            raise InvalidActivityError(

                "The GPX file does not contain track points."

            )

        workout = Workout()

        workout.info.source = "gpx"
        workout.info.title = self._title(gpx)
        workout.info.sport = self._sport(gpx)
        workout.info.date = self._start_time(points)
        workout.info.distance = self._distance(gpx)
        workout.info.duration = self._duration(gpx, points)
        workout.info.elevation_gain = (
            self._elevation_gain(gpx)
        )

        workout.sensors.add(

            "gps",

            self._route(points),

        )

        return workout

    # ======================================================
    # Source reading
    # ======================================================

    @staticmethod
    def _read_source(
        source: ImporterSource,
    ) -> str:

        if isinstance(source, Path):

            return source.read_text(

                encoding="utf-8",

            )

        if isinstance(source, (bytes, bytearray)):

            return bytes(source).decode(

                "utf-8-sig",

            )

        if isinstance(source, str):

            possible_path = Path(source)

            if possible_path.exists():

                return possible_path.read_text(

                    encoding="utf-8",

                )

            return source

        read = getattr(source, "read", None)

        if read is None:

            raise TypeError(

                "source must be a path, GPX text, "
                "bytes or a readable file object"

            )

        content = read()

        if isinstance(content, bytes):

            return content.decode("utf-8-sig")

        if isinstance(content, str):

            return content

        raise TypeError(

            "The supplied file object did not return "
            "text or bytes."

        )

    # ======================================================
    # Track points
    # ======================================================

    @staticmethod
    def _points(gpx):

        return [

            point

            for track in gpx.tracks

            for segment in track.segments

            for point in segment.points

        ]

    # ======================================================
    # Title
    # ======================================================

    @staticmethod
    def _title(gpx) -> str:

        for track in gpx.tracks:

            if track.name:

                return track.name

        if (

            gpx.metadata is not None

            and gpx.metadata.name

        ):

            return gpx.metadata.name

        return ""

    # ======================================================
    # Sport
    # ======================================================

    def _sport(self, gpx) -> str:

        for track in gpx.tracks:

            track_type = getattr(

                track,

                "type",

                None,

            )

            if track_type:

                return self._normalize_sport(

                    track_type

                )

        return self.default_sport

    # ======================================================

    @staticmethod
    def _normalize_sport(
        value: str,
    ) -> str:

        normalized = value.strip().lower()

        aliases = {

            "run": "Running",
            "running": "Running",

            "bike": "Cycling",
            "biking": "Cycling",
            "cycling": "Cycling",

            "swim": "Swimming",
            "swimming": "Swimming",

            "walk": "Walking",
            "walking": "Walking",

            "hike": "Hiking",
            "hiking": "Hiking",

        }

        return aliases.get(

            normalized,

            value.strip().title(),

        )

    # ======================================================
    # Start date
    # ======================================================

    @staticmethod
    def _start_time(
        points,
    ) -> date | None:

        times = [

            point.time

            for point in points

            if point.time is not None

        ]

        if not times:

            return None

        return min(times).date()

    # ======================================================
    # Distance
    # ======================================================

    @staticmethod
    def _distance(gpx) -> float | None:

        distance_metres = gpx.length_3d()

        if not distance_metres:

            distance_metres = gpx.length_2d()

        if not distance_metres:

            return None

        return distance_metres / 1000

    # ======================================================
    # Duration
    # ======================================================

    @staticmethod
    def _duration(
        gpx,
        points,
    ) -> timedelta | None:

        duration_seconds = gpx.get_duration()

        if (

            duration_seconds is not None

            and duration_seconds > 0

        ):

            return timedelta(

                seconds=duration_seconds,

            )

        times = sorted(

            point.time

            for point in points

            if point.time is not None

        )

        if len(times) < 2:

            return None

        elapsed = times[-1] - times[0]

        if elapsed.total_seconds() <= 0:

            return None

        return elapsed

    # ======================================================
    # Elevation gain
    # ======================================================

    @staticmethod
    def _elevation_gain(
        gpx,
    ) -> float | None:

        uphill_downhill = (

            gpx.get_uphill_downhill()

        )

        uphill = getattr(

            uphill_downhill,

            "uphill",

            None,

        )

        if uphill is None:

            return None

        return max(

            0.0,

            float(uphill),

        )

    # ======================================================
    # Route
    # ======================================================

    @staticmethod
    def _route(points) -> list[dict]:

        return [

            {

                "latitude": point.latitude,

                "longitude": point.longitude,

                "elevation": point.elevation,

                "time": (
                    point.time.isoformat()
                    if point.time is not None
                    else None
                ),

            }

            for point in points

        ]

    # ======================================================

    def __repr__(self):

        return (

            f"GPXImporter("

            f"default_sport='{self.default_sport}')"

        )