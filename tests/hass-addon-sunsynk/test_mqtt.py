"""Test MQTT class."""
import logging
from types import ModuleType

import pytest

from tests.conftest import import_module

_LOGGER = logging.getLogger(__name__)


@pytest.fixture
def mqtt() -> ModuleType:
    """Import the mqtt module."""
    mqttmod = import_module("mqtt", "hass-addon-sunsynk")
    _LOGGER.warning("Module mqtt: %s", dir(mqttmod))
    return mqttmod


@pytest.mark.addon
def test_mqtt(mqtt):
    """Test MQTT."""
    assert mqtt.hass_device_class(unit="kWh") == "energy"
