"""Test run."""
import logging
import re
from pathlib import Path

ADDON_PATH = "hass-addon-sunsynk-multi"

_LOGGER = logging.getLogger(__name__)


def test_versions() -> None:
    """Test versions.

    config.json - contains the HASS addon version
    Dockerfile  - installs the specific sunsynk library from pypi
    setup.py    - sunsynk library on pypi
    """
    v_setup = _get_version(
        filename="src/sunsynk/__init__.py",
        regex=r'VERSION = "(.+)"',
    )

    v_docker = _get_version(
        filename=f"{ADDON_PATH}/Dockerfile",
        regex=r"sunsynk(?:\[[^\]]+\])?==([0-9.]+)",
    )

    v_config = _get_version(
        filename=f"{ADDON_PATH}/config.yaml",
        regex=r"version: v(.+)",
    )

    v_changelog = _get_version(
        filename=f"{ADDON_PATH}/CHANGELOG.md",
        regex=r"\*\*(.+)\*\*",
    )

    if v_setup != v_docker or v_setup != v_config or v_setup != v_changelog:
        _LOGGER.error(
            "versions do not match\n%s\n%s\n%s config.yml\n%s CHANGELOG.md",
            v_setup,
            v_docker,
            v_config,
            v_changelog,
        )

    assert v_setup == v_docker
    assert v_setup == v_config
    assert v_setup == v_changelog


def _get_version(filename: str, regex: str) -> str:
    txt = Path(filename).read_text()
    res = re.compile(regex).search(txt)
    assert res, f"version not found in {filename}"
    _LOGGER.info("\t%s\t%s", res.group(1), filename)
    return res.group(1)
