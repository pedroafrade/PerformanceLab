"""
Tests for SensorCollection.
"""

from performancelab.workout import SensorCollection


def test_sensor_collection():

    sensors = SensorCollection()

    sensors.add("heart_rate", object())

    assert len(sensors) == 1

    assert "heart_rate" in sensors

    sensors.remove("heart_rate")

    assert len(sensors) == 0