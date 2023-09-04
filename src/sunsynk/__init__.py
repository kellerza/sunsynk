"""Sunsynk library."""
from typing import Final

from .helpers import NumType, ValType
from .rwsensors import RWSensor

# pylint: disable=unused-import
# flake8: noqa
from .sensors import Sensor
from .sunsynk import Sunsynk

# pylint: enable=unused-import

VERSION = "0.5.8"

CELSIUS: Final = "°C"
KWH: Final = "kWh"
AMPS: Final = "A"
VOLT: Final = "V"
WATT: Final = "W"
