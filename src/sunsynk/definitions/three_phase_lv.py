"""Sunsynk/Deye hybrid 3-phase LV inverter sensor definitions."""

from sunsynk import AMPS, CELSIUS, VOLT, WATT
from sunsynk.definitions.three_phase_common import SENSORS
from sunsynk.rwsensors import SelectRWSensor
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

lv_battery_manufacturers = {
    0: "HereYin",
    1: "PYLON",
    2: "SOLAX",
    3: "DYNESS_L",
    4: "CCGX",
    5: "Alpha_ESS",
    6: "SUNGO_CAN",
    7: "VISION_CAN",
    8: "WATTSONIC_CAN",
    9: "KUNLAN",
    10: "GSEnergy",
    11: "GS_HUB",
    12: "BYD_LV",
    13: "AOBO",
    14: "DEYE",
    15: "CFE",
    16: "DMEGC",
    17: "UZENERGY",
    18: "GROWATT",
}

SENSORS += (
    SelectRWSensor(229, "Battery 1 Manufacturer", options=lv_battery_manufacturers),
)
