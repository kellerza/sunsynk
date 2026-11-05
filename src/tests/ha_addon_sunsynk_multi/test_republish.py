"""Tests for re-sending states when Home Assistant comes back online."""

from unittest.mock import MagicMock

from ha_addon_sunsynk_multi.a_inverter import AInverter
from ha_addon_sunsynk_multi.a_sensor import ASensor
from ha_addon_sunsynk_multi.options import Options
from ha_addon_sunsynk_multi.sensor_options import SensorOption
from ha_addon_sunsynk_multi.timer_schedule import Schedule
from sunsynk.sensors import Sensor
from sunsynk.sunsynk import ValType

from .conftest import ist_factory

SLOW = Schedule("slow", read_every=5, report_every=60)
FAST = Schedule("fast", read_every=5, report_every=5)


def _asensor(
    name: str,
    value: ValType,
    *,
    schedule: Schedule = SLOW,
    retain: bool = False,
    entity: bool = True,
) -> ASensor:
    """Return an ASensor whose last published value is `value`."""
    return ASensor(
        opt=SensorOption(sensor=Sensor(1, name, "W"), schedule=schedule, visible=True),
        entity=MagicMock() if entity else None,
        retain=retain,
        _last=value,
    )


def _ist() -> AInverter:
    ist = ist_factory()
    ist.ss = {
        "energy": _asensor("energy", 12.3),
        "power": _asensor("power", 100, schedule=FAST),
        "never": _asensor("never", None),
        "rw": _asensor("rw", 50, retain=True),
        "hidden": _asensor("hidden", 7, entity=False),
    }
    return ist


async def test_republish_cached_sensors() -> None:
    """Only slow, non-retained sensors with an entity and a published value."""
    ist = _ist()

    await ist.republish_cached_sensors()

    ist.publish_sensors.assert_awaited_once_with(  # type: ignore[attr-defined]
        states={ist.ss["energy"]: 12.3}
    )


async def test_republish_cached_sensors_nothing_to_send() -> None:
    """No publish call when no sensor qualifies."""
    ist = _ist()
    del ist.ss["energy"]

    await ist.republish_cached_sensors()

    ist.publish_sensors.assert_not_awaited()  # type: ignore[attr-defined]


def test_mqtt_republish_enabled_by_default() -> None:
    """on_ha_connected must run again once HA has subscribed to the state topics."""
    assert Options().mqtt_republish > 0
