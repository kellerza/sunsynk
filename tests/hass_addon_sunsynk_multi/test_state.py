"""States."""
import logging

import pytest
from mqtt_entity import Device, Entity

from sunsynk.helpers import slug
from tests.hass_addon_sunsynk_multi import filter, state

_LOGGER = logging.getLogger(__name__)


@pytest.fixture
def mqdev() -> Device:
    """Return an MQTT device and ensure there is a HA prefix for create_entities."""
    dev = Device(["888"])
    state.SENSOR_PREFIX[dev.id] = "ss1"
    return dev


def test_create_entity(mqdev):
    """Create entity."""
    # Create the state
    st = state.State(
        filter=filter.Filter(),
        sensor=filter.Sensor(1, "one", "W"),
    )

    # The name is a combination of the sensor name & filter
    assert st.name == "one:mean"

    # Create the mqtt entity
    ent: Entity = st.create_entity(mqdev)
    entd: dict = ent.asdict
    assert entd == {
        "device": {"identifiers": ["888"]},
        "name": "ss1 one",
        "state_topic": "SUNSYNK/status/888/one",
        "unique_id": "888_one",
        "unit_of_measurement": "W",
        "device_class": "power",
    }


def test_create_entity2(mqdev):
    """Create entity."""
    # Create the state
    nme = "the energy"
    slugn = slug(nme)
    st = state.State(
        filter=filter.Filter(),
        sensor=filter.Sensor(1, nme, "kWh"),
    )

    # Create the mqtt entity
    ent: Entity = st.create_entity(mqdev)
    entd: dict = ent.asdict
    assert entd == {
        "device": {"identifiers": ["888"]},
        "name": f"ss1 {nme}",
        "state_topic": f"SUNSYNK/status/888/{slugn}",
        "unique_id": f"888_{slugn}",
        "unit_of_measurement": "kWh",
        "state_class": "total_increasing",
        "device_class": "energy",
    }
