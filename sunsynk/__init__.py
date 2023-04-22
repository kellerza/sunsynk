"""Sunsynk library."""
from typing import Final

# flake8: noqa
from .sensors import Sensor  # pylint: disable=unused-import
from .sunsynk import Sunsynk  # pylint: disable=unused-import

VERSION = "0.3.3"

CELSIUS: Final = "°C"
KWH: Final = "kWh"
AMPS: Final = "A"
VOLT: Final = "V"
WATT: Final = "W"
