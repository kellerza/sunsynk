"""Sensor definitions."""

import logging

from sunsynk import EnumSensor, SensorDefinitions
from sunsynk.sensors import ProtocolVersionSensor, SerialSensor
from sunsynk.utils import import_module

COMMON = SensorDefinitions()

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

COMMON += (
    EnumSensor(
        0,
        "Device type",
        options={
            2: "Inverter",
            3: "Single phase hybrid",
            4: "Microinverter",
            5: "Low voltage three phase hybrid",
            6: "High voltage three phase hybrid",
            512: "Single phase LV hybrid (3x MTTP)",
        },
    ),
    ProtocolVersionSensor(2, "Protocol"),
    SerialSensor((3, 4, 5, 6, 7), "Serial"),
)


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
