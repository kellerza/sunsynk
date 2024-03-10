"""Sunsynk/Deye 5kW&8kW hybrid 3-phase LV inverter sensor definitions."""
# pylint: disable=duplicate-code
from sunsynk.definitions3ph import SENSORS

SENSORS = SENSORS.copy()

##########
# General
##########


SENSORS.deprecated.update(
    {
        "grid_voltage": "grid_l1_voltage",
        "battery_activate": "battery_wake_up",
    }
)
