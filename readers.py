"""
PerformanceLab v1.0

readers.py

Funções de leitura de sensores.

Atualmente suporta:

- Apple Watch GPX
- Polar Flow CSV
"""

import pandas as pd
import numpy as np
import gpxpy

from PerformanceLab.sensor import SensorData


# ==========================================================
# Apple Watch GPX
# ==========================================================

def read_apple_gpx(filename):

    """
    Lê um ficheiro GPX exportado do Apple Watch.
    """

    records = []

    with open(filename, "r", encoding="utf-8") as f:

        gpx = gpxpy.parse(f)

    for track in gpx.tracks:

        for segment in track.segments:

            for point in segment.points:

                hr = np.nan

                for extension in point.extensions:

                    for child in extension:

                        if child.tag.lower().endswith("hr"):

                            try:
                                hr = int(child.text)

                            except Exception:
                                pass

                records.append({

                    "timestamp": pd.Timestamp(point.time),

                    "hr": hr,

                    "lat": point.latitude,

                    "lon": point.longitude,

                    "ele": point.elevation

                })

    sensor_df = pd.DataFrame(records)

    sensor_df.sort_values("timestamp", inplace=True)

    sensor_df.reset_index(drop=True, inplace=True)

    return SensorData(

        manufacturer="Apple",

        model="Apple Watch",

        data=sensor_df

    )


# ==========================================================
# Polar Verity Sense CSV
# ==========================================================

def read_polar_csv(filename):

    """
    Lê um CSV exportado do Polar Flow.
    """

    raw = pd.read_csv(filename, header=None)

    activity_date = str(raw.iloc[1, 2])

    activity_start = str(raw.iloc[1, 3])

    start_datetime = (

        pd.Timestamp(

            f"{activity_date} {activity_start}"

        )

        .tz_localize("Europe/Lisbon")

        .tz_convert("UTC")

    )

    headers = raw.iloc[2].tolist()

    sensor_df = raw.iloc[3:].copy()

    sensor_df.columns = headers

    sensor_df.reset_index(drop=True, inplace=True)

    time_col = next(

        c for c in sensor_df.columns

        if "Time" in str(c)

    )

    hr_col = next(

        c for c in sensor_df.columns

        if "HR" in str(c)

    )

    speed_col = next(

        c for c in sensor_df.columns

        if "Speed" in str(c)

    )

    dist_col = next(

        c for c in sensor_df.columns

        if "Distance" in str(c)

    )

    elapsed = pd.to_timedelta(

        sensor_df[time_col]

    )

    sensor_df["timestamp"] = (

        start_datetime + elapsed

    )

    sensor_df["hr"] = pd.to_numeric(

        sensor_df[hr_col],

        errors="coerce"

    )

    sensor_df["speed"] = pd.to_numeric(

        sensor_df[speed_col],

        errors="coerce"

    )

    sensor_df["distance"] = pd.to_numeric(

        sensor_df[dist_col],

        errors="coerce"

    )

    sensor_df = sensor_df[

        [

            "timestamp",

            "hr",

            "speed",

            "distance"

        ]

    ]

    sensor_df.sort_values(

        "timestamp",

        inplace=True

    )

    sensor_df.reset_index(

        drop=True,

        inplace=True

    )

    return SensorData(

        manufacturer="Polar",

        model="Verity Sense",

        data=sensor_df

    )