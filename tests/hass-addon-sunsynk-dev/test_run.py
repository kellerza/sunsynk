"""Test run."""
import logging
import re
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

import pytest

from tests.conftest import import_module

_LOGGER = logging.getLogger(__name__)
FOLDER = "hass-addon-sunsynk-dev"


@pytest.fixture
def run() -> ModuleType:
    """Import the module."""
    return import_module("run", FOLDER)


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

    run.SENSORS.clear()
    run.OPT.mqtt_host = ""


def test_versions(run):
    """Test versions.

    config.json - contains the HASS addon version
    Dockerfile  - installs the specific sunsynk library from pypi
    setup.py    - sunsynk library on pypi
    """

    def _get_version(filename, regex):
        txt = Path(filename).read_text()
        res = re.compile(regex).search(txt)
        assert res, f"version not found in {filename}"
        return res.group(1)

    v_setup = _get_version(
        filename="sunsynk/__init__.py",
        regex=r'VERSION = "(.+)"',
    )

    v_docker = _get_version(
        filename=f"{FOLDER}/Dockerfile",
        regex=r"sunsynk(?:\[[^\]]+\])?==([0-9.]+)",
    )

    v_config = _get_version(
        filename=f"{FOLDER}/config.yaml",
        regex=r"version: .+-(.+)",
    )

    assert v_setup == v_docker
    assert v_setup == v_config
