"""Sunsynk/Deye 5kW&8kW hybrid 3-phase LV inverter sensor definitions."""
# pylint: disable=duplicate-code
from sunsynk.definitions3ph import SENSORS
from sunsynk.sensors import BinarySensor

SENSORS = SENSORS.copy()

##########
# General
##########
SENSORS += (BinarySensor(194, "Grid Connected", bitmask=1 << 2),)
