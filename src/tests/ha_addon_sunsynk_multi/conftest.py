"""Addon fixtures."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from mqtt_entity import MQTTDevice

from ha_addon_sunsynk_multi.a_inverter import AInverter, InverterOptions
from ha_addon_sunsynk_multi.timer_schedule import Schedule
from sunsynk.sunsynk import InverterState

NOSCHEDULE = Schedule("no_unit", read_every=1, report_every=1)


def ist_factory(serial: str, ha_prefix: str, modbus_id: int) -> AInverter:
    """Return an inverter test instance."""
    res = MagicMock(spec_set=AInverter)
    res.inv.connect = AsyncMock()
    res.inv.state = MagicMock(spec_set=InverterState)
    res.opt = InverterOptions(
        ha_prefix=ha_prefix, serial_nr=serial, modbus_id=modbus_id
    )
    res.mqtt_dev = MQTTDevice(identifiers=[serial], components={})
    return res


@pytest.fixture
def ist() -> AInverter:
    """Return an MQTT device and ensure there is a HA prefix for create_entities."""
    return ist_factory("888", "ss1", 1)
