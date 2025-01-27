"""Sunsynk / Deye 16kW hybrid inverter sensor definitions."""

from sunsynk import AMPS, CELSIUS, KWH, VOLT, WATT
from sunsynk.definitions.single_phase import SENSORS as COMMON
from sunsynk.rwsensors import (
    NumberRWSensor,
    SelectRWSensor,
    SwitchRWSensor,
    SystemTimeRWSensor,
    TimeRWSensor,
)
from sunsynk.sensors import (
    BinarySensor,
    FaultSensor,
    InverterStateSensor,
    MathSensor,
    SDStatusSensor,
    Sensor,
    TempSensor,
)

SENSORS = COMMON.copy()


#######
# Grid
#######
SENSORS += (
    Sensor(169, "Grid power", WATT, -10),  # L1(167) + L2(168)
    Sensor(172, "Grid CT power", WATT, -10),
)
   
#############
# Inverter settings
#############
SENSORS += NumberRWSensor(230, "Grid Charge Battery current", AMPS, min=0, max=140)
SENSORS += NumberRWSensor(210, "Battery Max Charge current", AMPS, min=0, max=290)
SENSORS += NumberRWSensor(211, "Battery Max Discharge current", AMPS, min=0, max=290)

)
