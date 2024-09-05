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
    )[0]

    # v_docker = _get_version(
    #     filename=f"{ADDON_PATH}/Dockerfile",
    #     regex=r"sunsynk(?:\[[^\]]+\])?==([0-9.]+)",
    # )[0]

    v_config = _get_version(
        filename=f"{ADDON_PATH}/config.yaml",
        regex=r"version: \"(.+)\"",
    )[0]

    if v_setup != v_config:
        _LOGGER.error(
            "versions do not match\n%s\n%s config.yml",
            v_setup,
            v_config,
        )

    # assert v_setup == v_docker
    # assert v_setup == v_config


def _get_version(filename: str, regex: str) -> list[str]:
    txt = Path(filename).read_text(encoding="utf-8")
    reg = re.compile(regex, re.I)
    res = [str(r.group(1)) for r in reg.finditer(txt)]
    assert res, f"pattern not found in {filename}"
    _LOGGER.info("\t%s\t%s", res[0], filename)
    return res


def test_deps() -> None:
    """Check deps."""
    regex = r"    ([^ ]+\d)(\s|$)"

    v_docker = _get_version(
        filename=f"{ADDON_PATH}/Dockerfile",
        regex=regex,
    )

    v_setup = _get_version(
        filename="setup.cfg",
        regex=regex,
    )

    assert " ".join(sorted(v_setup)) == " ".join(sorted(v_docker))
