"""Sensor definitions."""

import logging

from sunsynk import SensorDefinitions
from sunsynk.utils import import_module

COMMON = SensorDefinitions()
"""Shared empty base; identity (regs 0-7) lives in ``sunsynk.identity.Identity``."""

PROG_CHARGE_OPTIONS = {
    0: "No Grid or Gen",
    1: "Allow Grid",
    2: "Allow Gen",
    3: "Allow Grid & Gen",
}
PROG_MODE_OPTIONS = {
    0 << 2: "None",
    1 << 2: "General",
    2 << 2: "Backup",
    3 << 2: "Charge",
}


def import_defs(name: str) -> SensorDefinitions:
    """Import defs."""
    libname = {"three-phase": "three_phase_lv"}.get(name) or name.replace("-", "_")
    logging.getLogger(__name__).info(
        "Importing sensor definitions %s (view the source online: "
        "https://github.com/kellerza/sunsynk/tree/main/src/sunsynk/definitions/%s.py )",
        name,
        libname,
    )
    mod = import_module(f"sunsynk.definitions.{libname}")
    return mod.SENSORS


# get this from config.yaml
ALL_DEFS = "single-phase|single-phase-16kw|three-phase|three-phase-hv".split("|")


def import_all_defs() -> dict[str, SensorDefinitions]:
    """Get all sensor definitions."""
    return {k: import_defs(k) for k in ALL_DEFS}
