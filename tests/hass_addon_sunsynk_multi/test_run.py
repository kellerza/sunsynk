"""Test run."""
import logging
import re
from pathlib import Path
from types import ModuleType

import pytest

from tests.conftest import import_module
from tests.hass_addon_sunsynk_multi import MOD_FOLDER

_LOGGER = logging.getLogger(__name__)


@pytest.fixture
def run() -> ModuleType:
    """Import the module."""
    return import_module("run", MOD_FOLDER)


def test_run(run):
    """Test Run."""
    assert not run.STATES
    assert not run.OPT.mqtt_host


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
        _LOGGER.warning("\t%s\t%s", res.group(1), filename)
        return res.group(1)

    v_setup = _get_version(
        filename="sunsynk/__init__.py",
        regex=r'VERSION = "(.+)"',
    )

    v_docker = _get_version(
        filename=f"{MOD_FOLDER}/Dockerfile",
        regex=r"sunsynk(?:\[[^\]]+\])?==([0-9.]+)",
    )

    v_config = _get_version(
        filename=f"{MOD_FOLDER}/config.yaml",
        regex=r"version: .+-(.+)",
    )

    assert v_setup == v_docker
    assert v_setup == v_config
