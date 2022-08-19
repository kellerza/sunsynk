"""Sunsynk hybrid inverter sensor definitions."""
from typing import Dict, Final, List

from sunsynk.sensor import (
    FaultSensor,
    InverterStateSensor,
    MathSensor,
    NumberRWSensor,
    RWSensor,
    SDStatusSensor,
    SelectRWSensor,
    Sensor,
    SerialSensor,
    TempSensor,
    TimeRWSensor,
)

CELSIUS: Final = "°C"
KWH: Final = "kWh"
AMPS: Final = "A"
VOLT: Final = "V"
WATT: Final = "W"

_SENSORS: List[Sensor] = []
DEPRECATED: Dict[str, Sensor] = {}

##########
# Battery
##########
_SENSORS += (
    TempSensor(182, "Battery temperature", CELSIUS, 0.1),
    Sensor(183, "Battery voltage", VOLT, 0.01),
    Sensor(184, "Battery SOC", "%"),
    Sensor(190, "Battery power", WATT, -1),
    Sensor(191, "Battery current", AMPS, -0.01),
)

#################
# Inverter Power
#################
_SENSORS += (
    Sensor(175, "Inverter power", WATT, -1),
    Sensor(154, "Inverter voltage", VOLT, 0.1),
    Sensor(193, "Inverter frequency", "Hz", 0.01),
)

#############
# Grid Power
#############
_SENSORS += (
    Sensor(79, "Grid frequency", "Hz", 0.01),
    Sensor(169, "Grid power", WATT, -1),  # L1(167) + L2(168)
    Sensor(167, "Grid LD power", WATT, -1),  # L1 seems to be LD
    Sensor(168, "Grid L2 power", WATT, -1),
    Sensor(150, "Grid voltage", VOLT, 0.1),
    MathSensor((160, 161), "Grid current", AMPS, factors=(0.01, 0.01)),
    Sensor(172, "Grid CT power", WATT, -1),
)
# LD power?

#############
# Load Power
#############
_SENSORS += (
    Sensor(178, "Load power", WATT, -1),  # L1(176) + L2(177)
    Sensor(176, "Load L1 power", WATT, -1),
    Sensor(177, "Load L2 power", WATT, -1),
)

################
# Solar Power 1
################
_SENSORS += (
    Sensor(186, "PV1 power", WATT, -1),
    Sensor(109, "PV1 voltage", VOLT, 0.1),
    Sensor(110, "PV1 current", AMPS, 0.1),
)

################
# Solar Power 2
################
_SENSORS += (
    Sensor(187, "PV2 power", WATT, -1),
    Sensor(111, "PV2 voltage", VOLT, 0.1),
    Sensor(112, "PV2 current", AMPS, 0.1),
)

###################
# Power on Outputs
###################
_SENSORS += (
    Sensor(166, "AUX power", WATT, -1),
    MathSensor((175, 167, 166), "Essential power", WATT, factors=(1, 1, -1)),
    MathSensor(
        (172, 167), "Non-Essential power", WATT, factors=(1, -1), no_negative=True
    ),
)

###################
# Energy
###################
_SENSORS += (
    Sensor(60, "Day Active Energy", KWH, -0.1),
    Sensor(70, "Day Battery Charge", KWH, 0.1),
    Sensor(71, "Day Battery discharge", KWH, 0.1),
    Sensor(77, "Day Grid Export", KWH, 0.1),
    Sensor(76, "Day Grid Import", KWH, 0.1),
    # Sensor(200, "Day Load Power", KWH, 0.01),
    Sensor(84, "Day Load Energy", KWH, 0.1),
    Sensor(108, "Day PV Energy", KWH, 0.1),
    Sensor(61, "Day Reactive Energy", "kVarh", -0.1),
    # Sensor((201, 202), "History Load Power", KWH, 0.1),
    Sensor(67, "Month Grid Energy", KWH, 0.1),
    Sensor(66, "Month Load Energy", KWH, 0.1),
    Sensor(65, "Month PV Energy", KWH, 0.1),
    Sensor((63, 64), "Total Active Energy", KWH, 0.1),  # signed?
    Sensor((72, 73), "Total Battery Charge", KWH, 0.1),
    Sensor((74, 75), "Total Battery Discharge", KWH, 0.1),
    Sensor((81, 82), "Total Grid Export", KWH, 0.1),
    Sensor((78, 80), "Total Grid Import", KWH, 0.1),
    Sensor((85, 86), "Total Load Energy", KWH, 0.1),
    Sensor((96, 97), "Total PV Energy", KWH, 0.1),
    Sensor((98, 99), "Year Grid Export", KWH, 0.1),
    Sensor((87, 88), "Year Load Energy", KWH, 0.1),
    Sensor((68, 69), "Year PV Energy", KWH, 0.1),
)

##########
# General
##########
RATED_POWER = Sensor((16, 17), "Rated power", WATT, 0.1)
_SENSORS.append(RATED_POWER)
_SENSORS += (
    Sensor(0, "Device Type"),
    FaultSensor((103, 104, 105, 106, 107), "Fault"),
    InverterStateSensor(59, "Overall state"),
    SDStatusSensor(92, "SD Status", ""),  # type: ignore
    SerialSensor((3, 4, 5, 6, 7), "Serial"),
    TempSensor(90, "DC transformer temperature", CELSIUS, 0.1),
    TempSensor(95, "Environment temperature", CELSIUS, 0.1),
    TempSensor(91, "Radiator temperature", CELSIUS, 0.1),
    Sensor(194, "Grid Connected Status"),
)
###########
# Settings
###########
_SENSORS += (
    Sensor(200, "Control Mode"),
    Sensor(201, "Equalization voltage", VOLT, 0.01),
    Sensor(202, "Absorption voltage", VOLT, 0.01),
    Sensor(230, "Grid Charge Battery current", AMPS, -1),
    Sensor(232, "Grid Charge enabled", "", -1),
    Sensor(312, "Battery charging voltage", VOLT, 0.01),
    Sensor(603, "Bat1 SOC", "%"),
    Sensor(611, "Bat1 Cycle"),
)
BATTERY_SHUTDOWN_CAPACITY = Sensor(217, "Battery Shutdown Capacity", "%")
BATTERY_RESTART_CAPACITY = Sensor(218, "Battery Restart Capacity", "%")
BATTERY_LOW_CAPACITY = Sensor(219, "Battery Low Capacity", "%")
_SENSORS += (BATTERY_SHUTDOWN_CAPACITY, BATTERY_RESTART_CAPACITY, BATTERY_LOW_CAPACITY)

#################
# System program
#################
_SENSORS.append(
    SelectRWSensor(243, "Priority Mode", options={0: "Battery first", 1: "Load first"})
)
PROG1_TIME = TimeRWSensor(250, "Prog1 Time")
PROG2_TIME = TimeRWSensor(251, "Prog2 Time", min=PROG1_TIME)
PROG3_TIME = TimeRWSensor(252, "Prog3 Time", min=PROG2_TIME)
PROG4_TIME = TimeRWSensor(253, "Prog4 Time", min=PROG3_TIME)
PROG5_TIME = TimeRWSensor(254, "Prog5 Time", min=PROG4_TIME)
PROG6_TIME = TimeRWSensor(255, "Prog6 Time", min=PROG5_TIME)
PROG1_TIME.min = PROG6_TIME
PROG1_TIME.max = PROG2_TIME
PROG2_TIME.max = PROG3_TIME
PROG3_TIME.max = PROG4_TIME
PROG4_TIME.max = PROG5_TIME
PROG5_TIME.max = PROG6_TIME
PROG6_TIME.max = PROG1_TIME

PROGRAM = (
    PROG1_TIME,
    PROG2_TIME,
    PROG3_TIME,
    PROG4_TIME,
    PROG5_TIME,
    PROG6_TIME,
    NumberRWSensor(256, "Prog1 power", WATT, max=RATED_POWER),
    NumberRWSensor(257, "Prog2 power", WATT, max=RATED_POWER),
    NumberRWSensor(258, "Prog3 power", WATT, max=RATED_POWER),
    NumberRWSensor(259, "Prog4 power", WATT, max=RATED_POWER),
    NumberRWSensor(260, "Prog5 power", WATT, max=RATED_POWER),
    NumberRWSensor(261, "Prog6 power", WATT, max=RATED_POWER),
    NumberRWSensor(268, "Prog1 Capacity", "%", min=BATTERY_LOW_CAPACITY),
    NumberRWSensor(269, "Prog2 Capacity", "%", min=BATTERY_LOW_CAPACITY),
    NumberRWSensor(270, "Prog3 Capacity", "%", min=BATTERY_LOW_CAPACITY),
    NumberRWSensor(271, "Prog4 Capacity", "%", min=BATTERY_LOW_CAPACITY),
    NumberRWSensor(272, "Prog5 Capacity", "%", min=BATTERY_LOW_CAPACITY),
    NumberRWSensor(273, "Prog6 Capacity", "%", min=BATTERY_LOW_CAPACITY),
    # 1- Grid, 2- Gen
    RWSensor(274, "Prog1 Charge"),
    RWSensor(275, "Prog2 Charge"),
    RWSensor(276, "Prog3 Charge"),
    RWSensor(277, "Prog4 Charge"),
    RWSensor(278, "Prog5 Charge"),
    RWSensor(279, "Prog6 Charge"),
)
_SENSORS.extend(PROGRAM)
PROG_VOLT = (
    RWSensor(262, "Prog1 voltage", VOLT, 0.1),
    RWSensor(263, "Prog2 voltage", VOLT, 0.1),
    RWSensor(264, "Prog3 voltage", VOLT, 0.1),
    RWSensor(265, "Prog4 voltage", VOLT, 0.1),
    RWSensor(266, "Prog5 voltage", VOLT, 0.1),
    RWSensor(267, "Prog6 voltage", VOLT, 0.1),
)
_SENSORS.extend(PROG_VOLT)


#############
# Deprecated
#############
ALL_SENSORS: Dict[str, Sensor] = {s.id: s for s in _SENSORS}


def _deprecated() -> None:
    """Populate the deprecated sensors."""
    dep_map: Dict[str, Sensor] = {
        "aux_power": Sensor(166, "AUX load", WATT, -1),
        "battery_temperature": TempSensor(182, "Temp Battery", CELSIUS, 0.1),
        "dc_transformer_temperature": TempSensor(
            90, "Temp DC transformer", CELSIUS, 0.1
        ),
        "environment_temperature": TempSensor(95, "Temp Environment", CELSIUS, 0.1),
        "grid_charge_battery_current": Sensor(230, "Battery Grid Charge", AMPS, -1),
        "grid_ct_power": Sensor(172, "Grid CT load", WATT, -1),
        "grid_l2_power": Sensor(168, "Grid L2 load", WATT, -1),
        "grid_ld_power": Sensor(167, "Grid L1 load", WATT, -1),
        "grid_power": Sensor(169, "Grid load", WATT, -1),
        "inverter_power": Sensor(175, "Inverter Output", WATT, -1),
        "radiator_temperature": TempSensor(91, "Temp Radiator", CELSIUS, 0.1),
        "day_active_energy": Sensor(60, "Day Active Power", KWH, -0.1),
        "day_reactive_energy": Sensor(61, "Day Reactive Power", "kVarh", -0.1),
        "total_active_energy": Sensor((63, 64), "Total Active Power", KWH, 0.1),
        "month_pv_energy": Sensor(65, "Month PV Power", KWH),
        "month_load_energy": Sensor(66, "Month Load Power", KWH),
        "month_grid_energy": Sensor(67, "Month Grid Power", KWH),
        "year_pv_energy": Sensor((68, 69), "Year PV Power", KWH, 0.1),
        "day_load_energy": Sensor(84, "Day Load Power", KWH, 0.1),
        "total_load_energy": Sensor((85, 86), "Total Load Power", KWH, 0.1),
        "year_load_energy": Sensor((87, 88), "Year Load Power", KWH, 0.1),
        "total_pv_energy": Sensor((96, 97), "Total PV Power", KWH, 0.1),
    }

    for newname, sen in dep_map.items():
        DEPRECATED[sen.id] = ALL_SENSORS[newname]
        ALL_SENSORS[sen.id] = sen


_deprecated()
