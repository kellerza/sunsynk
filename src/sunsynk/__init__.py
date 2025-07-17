"""Sunsynk library."""

from typing import Final

from sunsynk.helpers import NumType, ValType
from sunsynk.rwsensors import RWSensor
from sunsynk.sensors import Sensor, SensorDefinitions
from sunsynk.sunsynk import Sunsynk

VERSION = "0.8.2"

AMPS: Final = "A"
CELSIUS: Final = "°C"
HZ: Final = "Hz"
KWH: Final = "kWh"
VOLT: Final = "V"
WATT: Final = "W"

__all__ = [
    "NumType",
    "RWSensor",
    "Sensor",
    "SensorDefinitions",
    "Sunsynk",
    "ValType",
]
