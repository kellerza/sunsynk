"""Sunsynk/Deye hybrid 3-phase LV inverter sensor definitions."""

from sunsynk import AMPS, CELSIUS, VOLT, WATT
from sunsynk.definitions.three_phase_common import SENSORS
from sunsynk.sensors import (
    Sensor,
    TempSensor,
)

SENSORS = SENSORS.copy()

##########
# Battery
##########
SENSORS += (
    TempSensor(586, "Battery temperature", CELSIUS, 0.1),
    Sensor(587, "Battery voltage", VOLT, 0.01),
    Sensor(588, "Battery SOC", "%"),
    Sensor(590, "Battery power", WATT, -1),
    Sensor(591, "Battery current", AMPS, -0.01),
)

SENSORS.deprecated.update(
    {
        "grid_voltage": "grid_l1_voltage",
        "battery_activate": "battery_wake_up",
        "grid_connected_status": "grid_status",
    }
)
