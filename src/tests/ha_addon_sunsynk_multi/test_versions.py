"""Test run."""

import logging
import re
from pathlib import Path

from sunsynk import VERSION

ADDON_PATH = "hass-addon-sunsynk-multi"

_LOG = logging.getLogger(__name__)


def test_versions() -> None:
    """Test versions.

    config.json - contains the HASS addon version
    setup.py    - sunsynk library on pypi
    """
    v_setup = VERSION

    v_config = _get_version(
        filename=f"{ADDON_PATH}/config.yaml",
        regex=r"version: \"(.+)\"",
    )[0]

    if v_setup != v_config:
        _LOG.error(
            "versions do not match\n%s\n%s config.yml",
            v_setup,
            v_config,
        )


def _get_version(filename: str, regex: str) -> list[str]:
    txt = Path(filename).read_text(encoding="utf-8")
    reg = re.compile(regex, re.I)
    res = [str(r.group(1)) for r in reg.finditer(txt)]
    assert res, f"pattern not found in {filename}"
    _LOG.info("\t%s\t%s", res[0], filename)
    return res
