"""Tests for retained sensor states."""

from ha_addon_sunsynk_multi.sensor_options import SensorOption, SensorOptions
from ha_addon_sunsynk_multi.timer_schedule import Schedule
from sunsynk.sensors import Sensor
from .conftest import ist_factory

def test_init_sensors_retains_every_state() -> None:
    """HA gets each state from the broker when it subscribes after discovery."""
    sensor = Sensor(1, "energy", "kWh")
    soptions = SensorOptions()
    soptions[sensor] = SensorOption(
        sensor=sensor, schedule=Schedule("slow", read_every=5, report_every=60)
    )
    ist = ist_factory()

    ist.init_sensors(soptions)

    assert ist.ss[sensor.id].retain
