"""Addon helpers."""
import logging
import os
import sys
import traceback
from importlib import import_module as _import_module
from pathlib import Path
from types import ModuleType
from typing import Any, Optional

_LOGGER = logging.getLogger(__name__)


def import_module(mod_name: str, folder: str) -> ModuleType:
    """import_module."""
    here = Path(os.getcwd()) / folder
    sys.path.insert(0, str(here))
    try:
        mod_obj = _import_module(mod_name)
        return mod_obj
    finally:
        sys.path.pop(0)


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


def import_mysensors() -> Optional[dict[str, Any]]:
    """Import my sensors."""
    root = get_root()
    modn = "mysensors"
    pth = root / f"{modn}.py"
    if not pth.exists():
        return None
    _LOGGER.info("Importing %s...", pth)
    try:
        mod = import_module("mysensors", str(root))
    except Exception as err:  # pylint:disable=broad-except
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
