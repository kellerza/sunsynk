"""Sunsynk library."""

from typing import Final

from .helpers import NumType, ValType
from .rwsensors import RWSensor

# pylint: disable=unused-import
# flake8: noqa
from .sensors import Sensor
from .sunsynk import Sunsynk

# pylint: enable=unused-import

VERSION = "0.8.2"

AMPS: Final = "A"
CELSIUS: Final = "°C"
HZ: Final = "Hz"
KWH: Final = "kWh"
VOLT: Final = "V"
WATT: Final = "W"
