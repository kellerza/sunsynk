"""States."""

import logging

import pytest
from mqtt_entity import MQTTEntity
from mqtt_entity.helpers import hass_abbreviate

from ha_addon_sunsynk_multi.a_inverter import STATE
from ha_addon_sunsynk_multi.a_sensor import ASensor
from ha_addon_sunsynk_multi.sensor_options import (
    DEFS,
    OPT,
    SOPT,
    SensorOption,
    import_definitions,
)
from sunsynk.helpers import slug
from sunsynk.sensors import Sensor

from .conftest import NOSCHEDULE, ist_factory

_LOG = logging.getLogger(__name__)


def test_create_entity() -> None:
    """Create entity."""
    serial, ha_prefix = "888", "ss1"
    ist = ist_factory(serial, ha_prefix, 1)
    STATE.append(ist)

    st = ASensor(
        opt=SensorOption(
            sensor=Sensor(1, "one", "W"), schedule=NOSCHEDULE, visible=True
        ),
    )

    assert st.name == "one"

    # Create the mqtt entity
    ent: MQTTEntity = st.create_entity(ist)
    entd: dict = hass_abbreviate(ent.as_discovery_dict)
    assert entd == {
        "p": "sensor",
        "name": "one",
        "def_ent_id": f"sensor.{ha_prefix}_one",
        "stat_cla": "measurement",
        "stat_t": f"SS/{ha_prefix}/one",
        "sug_dsp_prc": 1,
        "uniq_id": f"{serial}_one",
        "unit_of_meas": "W",
        "dev_cla": "power",
    }


def test_create_entity2() -> None:
    """Create entity."""
    serial, ha_prefix = "888", "ss1"
    ist = ist_factory(serial, ha_prefix, 1)

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
    ent: MQTTEntity = st.create_entity(ist)
    entd: dict = hass_abbreviate(ent.as_discovery_dict)
    assert entd == {
        "p": "sensor",
        "name": nme,
        "def_ent_id": f"sensor.{ha_prefix}_{slugn}",
        "stat_t": f"SS/{ha_prefix}/{slugn}",
        "sug_dsp_prc": 1,
        "uniq_id": f"{serial}_{slugn}",
        "unit_of_meas": "kWh",
        "stat_cla": "total_increasing",
        "dev_cla": "energy",
    }


def test_alias_in_sensors_discovery_uses_alias_id() -> None:
    """SENSORS alias resolves to the alias copy; discovery unique_id is that slug."""
    OPT.sensor_definitions = "single-phase"
    import_definitions()
    OPT.sensors = ["AUX power"]
    OPT.sensors_first_inverter = []
    SOPT.init_sensors()

    sen = next(s for s in SOPT if s.id == "aux_power")
    assert sen.name == "AUX power"
    assert sen.address == DEFS.all["gen_power"].address
    assert "gen_power" not in {s.id for s in SOPT if SOPT[s].visible}

    serial, ha_prefix = "888", "ss1"
    ist = ist_factory(serial, ha_prefix, 1)
    STATE.append(ist)
    entd = hass_abbreviate(ASensor(opt=SOPT[sen]).create_entity(ist).as_discovery_dict)
    assert entd == {
        "p": "sensor",
        "name": "AUX power",
        "def_ent_id": f"sensor.{ha_prefix}_aux_power",
        "stat_cla": "measurement",
        "stat_t": f"SS/{ha_prefix}/aux_power",
        "sug_dsp_prc": 1,
        "uniq_id": f"{serial}_aux_power",
        "unit_of_meas": "W",
        "dev_cla": "power",
    }


def test_create_fail() -> None:
    """Create entity."""
    serial, ha_prefix = "888", "ss1"
    ist = ist_factory(serial, ha_prefix, 1)
    STATE.append(ist)

    st = ASensor(
        opt=SensorOption(
            sensor=Sensor(1, "one", "W"), schedule=NOSCHEDULE, visible=True, first=True
        ),
    )
    assert st.name == "one"

    # Create the mqtt entity
    ist.index = 0
    st.create_entity(ist)

    ist.index = 1
    with pytest.raises(ValueError):
        st.create_entity(ist)
