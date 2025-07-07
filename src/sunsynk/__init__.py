"""Sunsynk library."""

from typing import Final

# pylint: disable=unused-import
# flake8: noqa

from sunsynk.helpers import NumType, ValType
from sunsynk.rwsensors import RWSensor
from sunsynk.sensors import Sensor
from sunsynk.sunsynk import Sunsynk

# pylint: enable=unused-import

VERSION = "0.8.2"

AMPS: Final = "A"
CELSIUS: Final = "°C"
HZ: Final = "Hz"
KWH: Final = "kWh"
VOLT: Final = "V"
WATT: Final = "W"
