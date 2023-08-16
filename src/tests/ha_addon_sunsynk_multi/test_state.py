"""States."""
import logging
from unittest.mock import Mock

import pytest
from mqtt_entity import Device, Entity  # type: ignore

from ha_addon_sunsynk_multi.a_inverter import STATE, AInverter, InverterOptions
from ha_addon_sunsynk_multi.a_sensor import ASensor
from ha_addon_sunsynk_multi.sensor_options import SensorOption
from sunsynk.helpers import slug
from sunsynk.sensors import Sensor

_LOGGER = logging.getLogger(__name__)


@pytest.fixture
def mqdev() -> Device:
    """Return an MQTT device and ensure there is a HA prefix for create_entities."""
    dev = Device(["888"])
    # SENSOR_PREFIX[dev.id] = "ss1"
    return dev


@pytest.fixture
def ist() -> AInverter:
    """Return an MQTT device and ensure there is a HA prefix for create_entities."""
    inv = Mock()
    inv.state = {}
    return AInverter(inv=inv, opt=InverterOptions(ha_prefix="ss1"), ss={})


def test_create_entity(mqdev: Device, ist: AInverter) -> None:
    """Create entity."""
    STATE.append(ist)

    st = ASensor(
        opt=SensorOption(sensor=Sensor(1, "one", "W")),
    )

    assert st.name == "one"

    # Create the mqtt entity
    ent: Entity = st.create_entity(dev=mqdev, ist=ist)
    entd: dict = ent.asdict
    assert entd == {
        "device": {"identifiers": ["888"]},
        "name": "one",
        "object_id": "ss1_one",
        "state_topic": "SUNSYNK/status/888/one",
        "unique_id": "888_one",
        "unit_of_measurement": "W",
        "device_class": "power",
    }


def test_create_entity2(mqdev: Device, ist: AInverter) -> None:
    """Create entity."""
    # Create the state
    nme = "the energy"
    slugn = slug(nme)

    STATE.append(ist)

    st = ASensor(
        opt=SensorOption(sensor=Sensor(1, nme, "kWh")),
        # istate=0,
    )

    # Create the mqtt entity
    ent: Entity = st.create_entity(mqdev, ist=ist)
    entd: dict = ent.asdict
    assert entd == {
        "device": {"identifiers": ["888"]},
        "name": nme,
        "object_id": f"ss1_{slugn}",
        "state_topic": f"SUNSYNK/status/888/{slugn}",
        "unique_id": f"888_{slugn}",
        "unit_of_measurement": "kWh",
        "state_class": "total_increasing",
        "device_class": "energy",
    }
