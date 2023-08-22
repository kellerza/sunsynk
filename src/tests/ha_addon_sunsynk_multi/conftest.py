"""Addon fixtures."""
from unittest.mock import MagicMock, Mock

import pytest
from mqtt_entity import Device  # type: ignore

from ha_addon_sunsynk_multi.a_inverter import AInverter, InverterOptions
from ha_addon_sunsynk_multi.timer_schedule import Schedule
from sunsynk.sunsynk import InverterState

NOSCHEDULE = Schedule("no_unit", read_every=1, report_every=1)


@pytest.fixture
def mqtt_device() -> Device:
    """Return an MQTT device and ensure there is a HA prefix for create_entities."""
    dev = Device(["888"])
    # SENSOR_PREFIX[dev.id] = "ss1"
    return dev


@pytest.fixture
def ist() -> AInverter:
    """Return an MQTT device and ensure there is a HA prefix for create_entities."""
    ist = MagicMock(spec_set=AInverter)
    ist.inv = Mock()
    ist.inv.state = MagicMock(spec_set=InverterState)
    ist.opt = InverterOptions(ha_prefix="ss1")
    return ist
    # inv = Mock()
    # inv.state = {}
    # return AInverter(inv=inv, opt=InverterOptions(ha_prefix="ss1"), ss={})
