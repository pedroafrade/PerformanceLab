"""
PerformanceLab

Tests for GPX Importer.
"""

from datetime import date, timedelta
from io import BytesIO, StringIO

import pytest

from performancelab.importers import (
    GPXImporter,
    ImporterError,
    InvalidActivityError,
)


# ======================================================
# Sample GPX
# ======================================================

SAMPLE_GPX = """<?xml version="1.0" encoding="UTF-8"?>
<gpx
    version="1.1"
    creator="PerformanceLab Tests"
    xmlns="http://www.topografix.com/GPX/1/1">

    <metadata>
        <name>Test Activity</name>
    </metadata>

    <trk>
        <name>Morning Run</name>
        <type>running</type>

        <trkseg>
            <trkpt lat="38.7223" lon="-9.1393">
                <ele>20.0</ele>
                <time>2026-07-01T08:00:00Z</time>
            </trkpt>

            <trkpt lat="38.7233" lon="-9.1383">
                <ele>25.0</ele>
                <time>2026-07-01T08:05:00Z</time>
            </trkpt>

            <trkpt lat="38.7243" lon="-9.1373">
                <ele>30.0</ele>
                <time>2026-07-01T08:10:00Z</time>
            </trkpt>
        </trkseg>
    </trk>
</gpx>
"""


# ======================================================

def test_import_from_text():

    workout = GPXImporter().read(

        SAMPLE_GPX

    )

    assert workout.info.source == "gpx"

    assert workout.info.title == "Morning Run"

    assert workout.sport == "Running"

    assert workout.date == date(
        2026,
        7,
        1,
    )

    assert workout.duration == timedelta(

        minutes=10

    )

    assert workout.distance is not None

    assert workout.distance > 0

    assert workout.elevation_gain is not None

    assert workout.elevation_gain >= 0


# ======================================================

def test_route_is_stored():

    workout = GPXImporter().read(

        SAMPLE_GPX

    )

    route = workout.sensors.get("gps")

    assert len(route) == 3

    assert route[0]["latitude"] == pytest.approx(

        38.7223

    )

    assert route[0]["longitude"] == pytest.approx(

        -9.1393

    )

    assert route[0]["elevation"] == 20.0

    assert route[0]["time"] == (

        "2026-07-01T08:00:00+00:00"

    )


# ======================================================

def test_import_from_text_file_object():

    source = StringIO(SAMPLE_GPX)

    workout = GPXImporter().read(source)

    assert workout.info.title == "Morning Run"

    assert workout.sport == "Running"


# ======================================================

def test_import_from_binary_file_object():

    source = BytesIO(

        SAMPLE_GPX.encode("utf-8")

    )

    workout = GPXImporter().read(source)

    assert workout.info.source == "gpx"

    assert workout.duration == timedelta(

        minutes=10

    )


# ======================================================

def test_import_from_bytes():

    workout = GPXImporter().read(

        SAMPLE_GPX.encode("utf-8")

    )

    assert workout.info.title == "Morning Run"


# ======================================================

def test_import_from_path(tmp_path):

    path = tmp_path / "activity.gpx"

    path.write_text(

        SAMPLE_GPX,

        encoding="utf-8",

    )

    workout = GPXImporter().read(path)

    assert workout.info.title == "Morning Run"

    assert workout.sport == "Running"


# ======================================================

def test_default_sport():

    gpx_without_type = SAMPLE_GPX.replace(

        "<type>running</type>",

        "",

    )

    workout = GPXImporter(

        default_sport="Cycling",

    ).read(gpx_without_type)

    assert workout.sport == "Cycling"


# ======================================================

def test_invalid_gpx():

    with pytest.raises(ImporterError):

        GPXImporter().read(

            "<this-is-not-valid-gpx"

        )


# ======================================================

def test_gpx_without_track_points():

    empty_gpx = """<?xml version="1.0"?>
    <gpx
        version="1.1"
        creator="PerformanceLab"
        xmlns="http://www.topografix.com/GPX/1/1">
    </gpx>
    """

    with pytest.raises(InvalidActivityError):

        GPXImporter().read(empty_gpx)


# ======================================================

def test_invalid_source_type():

    with pytest.raises(TypeError):

        GPXImporter().read(123)