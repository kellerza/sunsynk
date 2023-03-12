"""Test run."""
import logging
import re
from pathlib import Path
from types import ModuleType

import pytest

from tests.conftest import import_module

_LOGGER = logging.getLogger(__name__)


@pytest.fixture
def mod_folder() -> str:
    """Return the folder from __init__."""
    init = import_module("__init__", Path(__file__).parent)
    return init.MOD_FOLDER


@pytest.fixture
def run(mod_folder) -> ModuleType:
    """Import the module."""
    return import_module("run", mod_folder)


def test_run(run):
    """Test Run."""
    assert not run.STATES
    assert not run.OPT.mqtt_host

    # testargs = ["run.py", "host1", "passw"]
    # with patch.object(run.sys, "argv", testargs):
    #     run.startup()
    # assert run.STATES
    # assert run.OPT.mqtt_host == "host1"
    # assert run.OPT.mqtt_password == "passw"

    # run.STATES.clear()
    # run.OPT.mqtt_host = ""


def test_versions(run, mod_folder):
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
        filename=f"{mod_folder}/Dockerfile",
        regex=r"sunsynk(?:\[[^\]]+\])?==([0-9.]+)",
    )

    v_config = _get_version(
        filename=f"{mod_folder}/config.yaml",
        regex=r"version: .+-(.+)",
    )

    assert v_setup == v_docker
    assert v_setup == v_config
