"""
PerformanceLab

Tests for Sensor Card presentation.
"""

from performancelab import Workout

from performancelab.presentation import (
    SensorCard,
    cadence_card,
    heart_rate_card,
    power_card,
    sensor_card,
)


# ======================================================
# Helpers
# ======================================================

def create_workout_with_sensors():

    workout = Workout()

    workout.sensors.add(

        "heart_rate",

        [
            {
                "time": (
                    "2026-07-01T08:00:00+00:00"
                ),
                "value": 140,
            },
            {
                "time": (
                    "2026-07-01T08:01:00+00:00"
                ),
                "value": 150,
            },
            {
                "time": (
                    "2026-07-01T08:02:00+00:00"
                ),
                "value": 160,
            },
        ],

    )

    workout.sensors.add(

        "power",

        [
            {
                "time": (
                    "2026-07-01T08:00:00+00:00"
                ),
                "value": 200,
            },
            {
                "time": (
                    "2026-07-01T08:01:00+00:00"
                ),
                "value": 250,
            },
        ],

    )

    workout.sensors.add(

        "cadence",

        [
            {
                "time": (
                    "2026-07-01T08:00:00+00:00"
                ),
                "value": 80,
            },
            {
                "time": (
                    "2026-07-01T08:01:00+00:00"
                ),
                "value": 90,
            },
        ],

    )

    return workout


# ======================================================
# Generic card
# ======================================================

def test_sensor_card():

    workout = create_workout_with_sensors()

    card = sensor_card(

        workout=workout,

        sensor_name="heart_rate",

        title="Heart rate",

        unit="bpm",

    )

    assert isinstance(
        card,
        SensorCard,
    )

    assert card.sensor_name == "heart_rate"

    assert card.title == "Heart rate"

    assert card.unit == "bpm"

    assert card.samples == 3

    assert card.average == 150

    assert card.minimum == 140

    assert card.maximum == 160

    assert card.available is True


# ======================================================
# Chart data
# ======================================================

def test_card_chart_data():

    workout = create_workout_with_sensors()

    card = heart_rate_card(workout)

    data = card.chart_data

    assert len(data) == 3

    assert data[0]["elapsed_seconds"] == 0

    assert data[0]["elapsed_minutes"] == 0

    assert data[0]["value"] == 140

    assert data[1]["elapsed_minutes"] == 1

    assert data[2]["elapsed_minutes"] == 2


# ======================================================
# Labels
# ======================================================

def test_card_labels():

    workout = create_workout_with_sensors()

    card = heart_rate_card(workout)

    assert card.average_label == "150 bpm"

    assert card.minimum_label == "140 bpm"

    assert card.maximum_label == "160 bpm"


# ======================================================
# Custom formatting
# ======================================================

def test_format_value():

    card = SensorCard(

        sensor_name="temperature",

        title="Temperature",

        unit="°C",

    )

    assert card.format_value(
        18.456,
        decimals=1,
    ) == "18.5 °C"

    assert card.format_value(
        None
    ) == "—"


# ======================================================
# Heart rate card
# ======================================================

def test_heart_rate_card():

    workout = create_workout_with_sensors()

    card = heart_rate_card(workout)

    assert card.title == "Heart rate"

    assert card.unit == "bpm"

    assert card.samples == 3

    assert card.average == 150


# ======================================================
# Power card
# ======================================================

def test_power_card():

    workout = create_workout_with_sensors()

    card = power_card(workout)

    assert card.title == "Power"

    assert card.unit == "W"

    assert card.samples == 2

    assert card.average == 225

    assert card.minimum == 200

    assert card.maximum == 250


# ======================================================
# Cadence card
# ======================================================

def test_cadence_card():

    workout = create_workout_with_sensors()

    card = cadence_card(workout)

    assert card.title == "Cadence"

    assert card.unit == "rpm"

    assert card.samples == 2

    assert card.average == 85

    assert card.maximum == 90


# ======================================================
# Missing sensor
# ======================================================

def test_missing_sensor_card():

    workout = Workout()

    card = heart_rate_card(workout)

    assert card.available is False

    assert card.samples == 0

    assert card.average is None

    assert card.minimum is None

    assert card.maximum is None

    assert card.series == []

    assert card.chart_data == []

    assert card.average_label == "—"