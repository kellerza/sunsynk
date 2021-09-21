"""Test run."""
import logging
from types import ModuleType
from unittest.mock import patch

import pytest

from tests.conftest import import_module

_LOGGER = logging.getLogger(__name__)


@pytest.fixture
def run() -> ModuleType:
    """Import the run module."""
    runmod = import_module("run", "hass-addon-sunsynk")
    _LOGGER.warning("Module run: %s", dir(runmod))
    return runmod


@pytest.mark.addon
def test_run(run):
    """Test Run."""
    assert not run.SENSORS
    assert not run.OPTIONS.mqtt_host

    testargs = ["run.py", "host1", "passw"]
    with patch.object(run.sys, "argv", testargs):
        run.startup()
    assert run.SENSORS
    assert run.OPTIONS.mqtt_host == "host1"
    assert run.OPTIONS.mqtt_password == "passw"
