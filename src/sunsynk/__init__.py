"""Sunsynk library."""

from importlib import metadata
from typing import Final

from sunsynk.helpers import NumType, ValType
from sunsynk.rwsensors import RWSensor
from sunsynk.sensors import EnumSensor, Sensor, SensorDefinitions
from sunsynk.sunsynk import Sunsynk

AMPS: Final = "A"
CELSIUS: Final = "°C"
HZ: Final = "Hz"
KWH: Final = "kWh"
VOLT: Final = "V"
WATT: Final = "W"

VERSION = metadata.version("sunsynk")

__all__ = [
    "VERSION",
    "EnumSensor",
    "NumType",
    "RWSensor",
    "Sensor",
    "SensorDefinitions",
    "Sunsynk",
    "ValType",
]
