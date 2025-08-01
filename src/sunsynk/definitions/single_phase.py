"""Sunsynk 5kW&8kW hybrid inverter sensor definitions."""

from sunsynk import AMPS, CELSIUS, HZ, KWH, VOLT, WATT
from sunsynk.definitions import COMMON, PROG_CHARGE_OPTIONS, PROG_MODE_OPTIONS
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

##########
# Battery
##########
SENSORS += (
    TempSensor(182, "Battery temperature", CELSIUS, 0.1),
    Sensor(183, "Battery voltage", VOLT, 0.01),
    Sensor(184, "Battery SOC", "%"),
    Sensor(190, "Battery power", WATT, -1),
    Sensor(191, "Battery current", AMPS, -0.01),
    # Charge and Discharge limit vary based on temperature and SoC
    Sensor(314, "Battery charge limit current", AMPS, -1),  # #327
    Sensor(315, "Battery discharge limit current", AMPS, -1),  # #327
)

###########
# Inverter
###########
SENSORS += (
    Sensor(175, "Inverter power", WATT, -1),
    Sensor(154, "Inverter voltage", VOLT, 0.1),
    Sensor(164, "Inverter current", AMPS, 0.01),
    Sensor(193, "Inverter frequency", HZ, 0.01),
)

#######
# Grid
#######
SENSORS += (
    Sensor(79, "Grid frequency", HZ, 0.01),
    Sensor(169, "Grid power", WATT, -1),  # L1(167) + L2(168)
    Sensor(167, "Grid LD power", WATT, -1),  # L1 seems to be LD
    Sensor(168, "Grid L2 power", WATT, -1),
    Sensor(150, "Grid voltage", VOLT, 0.1),
    MathSensor((160, 161), "Grid current", AMPS, factors=(0.01, 0.01)),
    Sensor(172, "Grid CT power", WATT, -1),
)

#######
# Load
#######
SENSORS += (
    Sensor(178, "Load power", WATT, -1),  # L1(176) + L2(177)
    Sensor(176, "Load L1 power", WATT, -1),
    Sensor(177, "Load L2 power", WATT, -1),
    Sensor(192, "Load frequency", HZ, 0.01),
)

#################
# AUX / Generator
#################
SENSORS += (
    Sensor(166, "AUX power", WATT, -1),
    # Sensor(166, "Generator Power", WATT, -1),
    Sensor(181, "AUX voltage", VOLT, 0.1),
    Sensor(196, "AUX frequency", HZ, 0.1),
)

#############
# Solar PV 1
#############
SENSORS += (
    Sensor(186, "PV1 power", WATT, -1),
    Sensor(109, "PV1 voltage", VOLT, 0.1),
    Sensor(110, "PV1 current", AMPS, 0.1),
)

#############
# Solar PV 2
#############
SENSORS += (
    Sensor(187, "PV2 power", WATT, -1),
    Sensor(111, "PV2 voltage", VOLT, 0.1),
    Sensor(112, "PV2 current", AMPS, 0.1),
)

#############
# Solar PV 3
#############
SENSORS += (
    Sensor(188, "PV3 power", WATT, -1),
    Sensor(113, "PV3 voltage", VOLT, 0.1),
    Sensor(114, "PV3 current", AMPS, 0.1),
)

###################
# Power on Outputs
###################
SENSORS += (
    # Essential power
    # - https://powerforum.co.za/topic/8646-my-sunsynk-8kw-data-collection-setup/?do=findComment&comment=147591
    # Essential 1 power
    # - dev & normal version, see https://github.com/kellerza/sunsynk/issues/134
    # Essential 2 power
    # - early-2023 see https://github.com/kellerza/sunsynk/issues/75
    MathSensor((175, 169, 166), "Essential power", WATT, factors=(1, 1, -1)),
    MathSensor((175, 167, 166), "Essential 1 power", WATT, factors=(1, 1, -1)),
    MathSensor(
        (175, 169, 166), "Essential 2 power", WATT, factors=(1, 1, -1), absolute=True
    ),
    MathSensor(
        (172, 167), "Non-essential power", WATT, factors=(1, -1), no_negative=True
    ),
)

#########
# Energy
#########
SENSORS += (
    Sensor(60, "Day active energy", KWH, -0.1),
    Sensor(70, "Day battery charge", KWH, 0.1),
    Sensor(71, "Day battery Discharge", KWH, 0.1),
    Sensor(76, "Day grid import", KWH, 0.1),
    Sensor(77, "Day grid export", KWH, 0.1),
    Sensor(84, "Day load energy", KWH, 0.1),
    Sensor(108, "Day PV energy", KWH, 0.1),
    Sensor(61, "Day reactive energy", "kVarh", -0.1),
    Sensor(67, "Month grid energy", KWH, 0.1),
    Sensor(66, "Month load energy", KWH, 0.1),
    Sensor(65, "Month PV energy", KWH, 0.1),
    Sensor((63, 64), "Total active energy", KWH, 0.1),  # signed?
    Sensor((72, 73), "Total battery charge", KWH, 0.1),
    Sensor((74, 75), "Total battery discharge", KWH, 0.1),
    Sensor((81, 82), "Total grid export", KWH, 0.1),
    Sensor((78, 80), "Total grid import", KWH, 0.1),
    Sensor((85, 86), "Total load energy", KWH, 0.1),
    Sensor((96, 97), "Total PV energy", KWH, 0.1),
    Sensor((98, 99), "Year grid export", KWH, 0.1),
    Sensor((87, 88), "Year load energy", KWH, 0.1),
    Sensor((68, 69), "Year PV energy", KWH, 0.1),
)

##########
# General
##########
RATED_POWER = Sensor((16, 17), "Rated power", WATT, 0.1)

SENSORS += (
    RATED_POWER,
    FaultSensor((103, 104, 105, 106), "Fault"),
    InverterStateSensor(59, "Overall state"),
    SDStatusSensor(92, "SD status", ""),
    TempSensor(90, "DC transformer temperature", CELSIUS, 0.1),
    TempSensor(95, "Environment temperature", CELSIUS, 0.1),
    TempSensor(91, "Radiator temperature", CELSIUS, 0.1),
    BinarySensor(194, "Grid connected"),
    SystemTimeRWSensor((22, 23, 24), "Date time", unit=""),
)

###########
# Settings
###########
SENSORS += (
    SwitchRWSensor(43, "Inverter enabled", on=1),  # 0=off, 1=on
    Sensor(200, "Control mode"),
    SwitchRWSensor(232, "Grid charge enabled", "", bitmask=1),
    SelectRWSensor(
        235, "Generator input", "", options={0: "Disable", 1: "Output", 2: "Input"}
    ),
    Sensor(312, "Battery charging voltage", VOLT, 0.01),
    Sensor(603, "Bat1 SOC", "%"),
    Sensor(611, "Bat1 Cycle"),
)

# Battery capacity (if managed by BMS)
BATTERY_LOW_CAP = NumberRWSensor(219, "Battery low capacity", "%", max=50)
BATTERY_SHUTDOWN_CAP = NumberRWSensor(
    217, "Battery shutdown capacity", "%", max=BATTERY_LOW_CAP
)
BATTERY_LOW_CAP.min = BATTERY_SHUTDOWN_CAP
BATTERY_RESTART_CAP = NumberRWSensor(
    218, "Battery restart capacity", "%", min=BATTERY_SHUTDOWN_CAP
)

# Absolute min and max voltage based on Deye inverter
MIN_VOLT = 41
MAX_VOLT = 60

# Battery voltage (if managed by voltage only)
BATTERY_SHUTDOWN_VOLT = NumberRWSensor(
    220, "Battery shutdown voltage", VOLT, 0.01, min=MIN_VOLT
)
BATTERY_LOW_VOLT = NumberRWSensor(
    222, "Battery low voltage", VOLT, 0.01, min=BATTERY_SHUTDOWN_VOLT, max=MAX_VOLT
)
BATTERY_RESTART_VOLT = NumberRWSensor(
    221, "Battery restart voltage", VOLT, 0.01, max=MAX_VOLT, min=BATTERY_SHUTDOWN_VOLT
)


BATTERY_EQUALIZATION_VOLT = NumberRWSensor(
    201, "Battery Equalization voltage", VOLT, 0.01, min=MIN_VOLT, max=MAX_VOLT
)
BATTERY_ABSORPTION_VOLT = NumberRWSensor(
    202, "Battery Absorption voltage", VOLT, 0.01, min=MIN_VOLT, max=MAX_VOLT
)
BATTERY_FLOAT_VOLT = NumberRWSensor(
    203, "Battery Float voltage", VOLT, 0.01, min=MIN_VOLT, max=MAX_VOLT
)

SENSORS += (
    BATTERY_EQUALIZATION_VOLT,
    BATTERY_ABSORPTION_VOLT,
    BATTERY_FLOAT_VOLT,
    BATTERY_SHUTDOWN_CAP,
    BATTERY_RESTART_CAP,
    BATTERY_LOW_CAP,
    BATTERY_SHUTDOWN_VOLT,
    BATTERY_RESTART_VOLT,
    BATTERY_LOW_VOLT,
)

#################
# System program
#################
SENSORS += (
    # 0: "Battery first", 1: "Load first"
    SwitchRWSensor(243, "Priority Load", bitmask=1),
    SelectRWSensor(
        244,
        "Load Limit",
        options={0: "Allow Export", 1: "Essentials", 2: "Zero Export"},
    ),
    NumberRWSensor(53, "Max Solar power", WATT, 1, min=0, max=RATED_POWER),
    NumberRWSensor(245, "Max Sell power", WATT, 1, min=0, max=RATED_POWER),
    # If disabled, does not allow the export of any excess solar.
    # If enabled, will export any excess, but will also draw a
    # constant ~40w at all times for an unknown reason
    # 0: "Don't Sell", 1: "Sell solar"
    SwitchRWSensor(247, "Solar Export", bitmask=1),
    SwitchRWSensor(248, "Use Timer", bitmask=1),
    # Grid peak shaving settings
    SwitchRWSensor(280, "Peak shaving", bitmask=0x0F, on=1),  # ?
    SwitchRWSensor(280, "Gen peak shaving", bitmask=0xF0, on=0x10),
    SwitchRWSensor(280, "Grid peak shaving", bitmask=0xF00, on=0x100),
    SwitchRWSensor(280, "Grid always on", bitmask=0xF000, on=0x1000),  # ?
    NumberRWSensor(292, "Gen peak shaving power", WATT, 1, min=0, max=RATED_POWER),
    NumberRWSensor(293, "Grid peak shaving power", WATT, 1, min=0, max=RATED_POWER),
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
SENSORS += (PROG1_TIME, PROG2_TIME, PROG3_TIME, PROG4_TIME, PROG5_TIME, PROG6_TIME)


SENSORS += (
    # The max power that can be used from the battery
    NumberRWSensor(256, "Prog1 power", WATT, max=RATED_POWER),
    NumberRWSensor(257, "Prog2 power", WATT, max=RATED_POWER),
    NumberRWSensor(258, "Prog3 power", WATT, max=RATED_POWER),
    NumberRWSensor(259, "Prog4 power", WATT, max=RATED_POWER),
    NumberRWSensor(260, "Prog5 power", WATT, max=RATED_POWER),
    NumberRWSensor(261, "Prog6 power", WATT, max=RATED_POWER),
    NumberRWSensor(268, "Prog1 Capacity", "%", min=BATTERY_LOW_CAP),
    NumberRWSensor(269, "Prog2 Capacity", "%", min=BATTERY_LOW_CAP),
    NumberRWSensor(270, "Prog3 Capacity", "%", min=BATTERY_LOW_CAP),
    NumberRWSensor(271, "Prog4 Capacity", "%", min=BATTERY_LOW_CAP),
    NumberRWSensor(272, "Prog5 Capacity", "%", min=BATTERY_LOW_CAP),
    NumberRWSensor(273, "Prog6 Capacity", "%", min=BATTERY_LOW_CAP),
    SelectRWSensor(274, "Prog1 charge", options=PROG_CHARGE_OPTIONS, bitmask=0x03),
    SelectRWSensor(275, "Prog2 charge", options=PROG_CHARGE_OPTIONS, bitmask=0x03),
    SelectRWSensor(276, "Prog3 charge", options=PROG_CHARGE_OPTIONS, bitmask=0x03),
    SelectRWSensor(277, "Prog4 charge", options=PROG_CHARGE_OPTIONS, bitmask=0x03),
    SelectRWSensor(278, "Prog5 charge", options=PROG_CHARGE_OPTIONS, bitmask=0x03),
    SelectRWSensor(279, "Prog6 charge", options=PROG_CHARGE_OPTIONS, bitmask=0x03),
    SelectRWSensor(274, "Prog1 mode", options=PROG_MODE_OPTIONS, bitmask=0x1C),
    SelectRWSensor(275, "Prog2 mode", options=PROG_MODE_OPTIONS, bitmask=0x1C),
    SelectRWSensor(276, "Prog3 mode", options=PROG_MODE_OPTIONS, bitmask=0x1C),
    SelectRWSensor(277, "Prog4 mode", options=PROG_MODE_OPTIONS, bitmask=0x1C),
    SelectRWSensor(278, "Prog5 mode", options=PROG_MODE_OPTIONS, bitmask=0x1C),
    SelectRWSensor(279, "Prog6 mode", options=PROG_MODE_OPTIONS, bitmask=0x1C),
)
SENSORS += (
    NumberRWSensor(
        262, "Prog1 voltage", VOLT, 0.01, min=BATTERY_LOW_VOLT, max=BATTERY_FLOAT_VOLT
    ),
    NumberRWSensor(
        263, "Prog2 voltage", VOLT, 0.01, min=BATTERY_LOW_VOLT, max=BATTERY_FLOAT_VOLT
    ),
    NumberRWSensor(
        264, "Prog3 voltage", VOLT, 0.01, min=BATTERY_LOW_VOLT, max=BATTERY_FLOAT_VOLT
    ),
    NumberRWSensor(
        265, "Prog4 voltage", VOLT, 0.01, min=BATTERY_LOW_VOLT, max=BATTERY_FLOAT_VOLT
    ),
    NumberRWSensor(
        266, "Prog5 voltage", VOLT, 0.01, min=BATTERY_LOW_VOLT, max=BATTERY_FLOAT_VOLT
    ),
    NumberRWSensor(
        267, "Prog6 voltage", VOLT, 0.01, min=BATTERY_LOW_VOLT, max=BATTERY_FLOAT_VOLT
    ),
)

#############
# Inverter settings
#############
SENSORS += NumberRWSensor(230, "Grid Charge Battery current", AMPS, min=0, max=185)
SENSORS += NumberRWSensor(210, "Battery Max Charge current", AMPS, min=0, max=185)
SENSORS += NumberRWSensor(211, "Battery Max Discharge current", AMPS, min=0, max=185)


BMS_protocol = {
    0: "PYLON CAN",
    1: "SACRED SUN RS485",
    2: "02",
    3: "DYNESS CAN",
    4: "04",
    5: "05",
    6: "GenixGreen RS485",
    7: "07",
    8: "08",
    9: "09",
    10: "10",
    11: "11",
    12: "PYLON RS485",
    13: "VISION CAN",
    14: "WATTSONIC RS485",
    15: "UNIPOWER RS485",
    16: "16",
    17: "LD RS485",
    18: "18",
    19: "UNKNOWN RS485",
}

SENSORS += SelectRWSensor(325, "BMS Protocol", options=BMS_protocol)

#############
# Deprecated
#############
SENSORS.deprecated.update(
    {
        "grid_connected_status": "grid_connected",
        "absorption_voltage": "battery_absorption_voltage",
        "aux_load": "aux_power",
        "battery_grid_charge": "grid_charge_battery_current",
        "day_active_power": "day_active_energy",
        "day_load_power": "day_load_energy",
        "day_reactive_power": "day_reactive_energy",
        "equalization_voltage": "battery_equalization_voltage",
        "grid_ct_load": "grid_ct_power",
        "grid_l1_load": "grid_ld_power",
        "grid_l2_load": "grid_l2_power",
        "grid_load": "grid_power",
        "inverter_output": "inverter_power",
        "month_grid_power": "month_grid_energy",
        "month_load_power": "month_load_energy",
        "month_pv_power": "month_pv_energy",
        "priority_mode": "priority_load",
        "temp_battery": "battery_temperature",
        "temp_dc_transformer": "dc_transformer_temperature",
        "temp_environment": "environment_temperature",
        "temp_radiator": "radiator_temperature",
        "total_active_power": "total_active_energy",
        "total_load_power": "total_load_energy",
        "total_pv_power": "total_pv_energy",
        "year_load_power": "year_load_energy",
        "year_pv_power": "year_pv_energy",
    }
)
