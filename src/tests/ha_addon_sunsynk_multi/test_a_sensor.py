"""States."""

import logging

import pytest
from mqtt_entity import MQTTDevice, MQTTEntity
from mqtt_entity.helpers import discovery_dict

from ha_addon_sunsynk_multi.a_inverter import STATE, AInverter
from ha_addon_sunsynk_multi.a_sensor import ASensor
from ha_addon_sunsynk_multi.sensor_options import SensorOption
from sunsynk.helpers import slug
from sunsynk.sensors import Sensor

from .conftest import NOSCHEDULE

_LOGGER = logging.getLogger(__name__)


def test_create_entity(mqtt_device: MQTTDevice, ist: AInverter) -> None:
    """Create entity."""
    STATE.append(ist)

    st = ASensor(
        opt=SensorOption(
            sensor=Sensor(1, "one", "W"), schedule=NOSCHEDULE, visible=True
        ),
    )

    assert st.name == "one"

    serial = "888"

    # Create the mqtt entity
    ent: MQTTEntity = st.create_entity(serial, ist=ist)
    entd: dict = discovery_dict(ent)
    assert entd == {
        "p": "sensor",
        "name": "one",
        "obj_id": "ss1_one",
        "stat_cla": "measurement",
        "stat_t": f"SS/{serial}/one",
        "sug_dsp_prc": 1,
        "uniq_id": f"{serial}_one",
        "unit_of_meas": "W",
        "dev_cla": "power",
    }


def test_create_entity2(mqtt_device: MQTTDevice, ist: AInverter) -> None:
    """Create entity."""
    # Create the state
    nme = "the energy"
    slugn = slug(nme)

    STATE.append(ist)

    st = ASensor(
        opt=SensorOption(
            sensor=Sensor(1, nme, "kWh"), schedule=NOSCHEDULE, visible=True
        )
    )

    serial = "888"

    # Create the mqtt entity
    ent: MQTTEntity = st.create_entity(serial, ist=ist)
    entd: dict = discovery_dict(ent)
    assert entd == {
        "p": "sensor",
        "name": nme,
        "obj_id": f"ss1_{slugn}",
        "stat_t": f"SS/888/{slugn}",
        "sug_dsp_prc": 1,
        "uniq_id": f"888_{slugn}",
        "unit_of_meas": "kWh",
        "stat_cla": "total_increasing",
        "dev_cla": "energy",
    }


def test_create_fail(mqtt_device: MQTTDevice, ist: AInverter) -> None:
    """Create entity."""
    STATE.append(ist)

    st = ASensor(
        opt=SensorOption(
            sensor=Sensor(1, "one", "W"), schedule=NOSCHEDULE, visible=True, first=True
        ),
    )
    assert st.name == "one"
    serial = "888"

    # Create the mqtt entity
    ist.index = 0
    st.create_entity(serial, ist=ist)

    ist.index = 1
    with pytest.raises(ValueError):
        st.create_entity(serial, ist=ist)
