"""Addon helpers."""

import logging
import os
import traceback
from pathlib import Path
from typing import Any

from sunsynk.utils import import_module

_LOGGER = logging.getLogger(__name__)


def get_root(create: bool = False) -> Path:
    """Get the root folder for data and mysensors."""
    root = (
        Path("/share/hass-addon-sunsynk/")
        if os.name != "nt"
        else Path(__name__).parent / ".data"
    )
    if create and not root.exists():
        root.mkdir(parents=True)
    return root


def import_mysensors() -> dict[str, Any] | None:
    """Import my sensors."""
    root = get_root()
    modn = "mysensors"
    pth = root / f"{modn}.py"
    if not pth.exists():
        return None
    _LOGGER.info("Importing %s...", pth)
    try:
        mod = import_module("mysensors", str(root))
    except Exception as err:
        traceback.print_exc()
        _LOGGER.error("Error importing %s: %s", pth, err)
        return None
    sensors = getattr(mod, "SENSORS", None)
    if not sensors:
        _LOGGER.error("No SENSORS variable found in mysensors.py")
        return None
    res: dict[str, Any] = getattr(sensors, "all", {})
    if res:
        _LOGGER.info("  custom sensors: %s", ", ".join(res))
    else:
        _LOGGER.warning("  no custom sensors")
    return res
