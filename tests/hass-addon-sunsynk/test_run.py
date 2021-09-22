"""Test run."""
import logging
import re
from pathlib import Path
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
    assert not run.OPT.mqtt_host

    testargs = ["run.py", "host1", "passw"]
    with patch.object(run.sys, "argv", testargs):
        run.startup()
    assert run.SENSORS
    assert run.OPT.mqtt_host == "host1"
    assert run.OPT.mqtt_password == "passw"


@pytest.mark.addon
def test_versions(run):
    """Test versions.

    config.json - contains the HASS addon version
    Dockerfile  - installs the specific sunsynk library from pypi
    setup.py    - sunsynk library on pypi
    """

    def _get_version(filename, regex):
        txt = Path(filename).read_text()
        res = re.compile(regex).search(txt)
        assert res, "version not found in setup.py"
        return res.group(1)

    v_setup = _get_version(
        filename="setup.py",
        regex=r'VERSION = "(.+)"',
    )

    v_docker = _get_version(
        filename="hass-addon-sunsynk/Dockerfile",
        regex=r"sunsynk==(.+)",
    )

    v_config = _get_version(
        filename="hass-addon-sunsynk/config.json",
        regex=r'"version": ".+-(.+)"',
    )

    assert v_setup == v_docker
    assert v_setup == v_config
