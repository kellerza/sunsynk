"""Sunsynk library."""
# pylint: disable=unused-import
# flake8: noqa
from .sensor import Sensor, group_sensors, update_sensors
from .sunsynk import Sunsynk

try:
    import async_modbus
except ImportError:
    uSunsynk: Sunsynk = None  # type: ignore
else:
    from .usunsynk import uSunsynk  # type: ignore

try:
    import pymodbus
except ImportError:
    pySunsynk: Sunsynk = None  # type: ignore
else:
    from .pysunsynk import pySunsynk  # type: ignore

VERSION = "0.1.3"
