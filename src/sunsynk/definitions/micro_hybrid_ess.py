"""Deye micro hybrid ESS sensor definitions (device type 0x0104).

Deye SUN-BK series (SUN-BK80/100/160/200/250-2.56KWH) balcony storage.
Mapped on a SUN-BK250-2.56KWH-EU-AM4-32L + 3x AE-F2.56 (control FW 0146-7350-0102,
comm FW C139-0000, protocol 2.4), checked against the Deye Cloud app.
The realtime block is at 1000+; the 500-700 block used by hybrids is all zeros.
Energy counters follow the AE-FS2.0-2H2 map (same OEM line, also 0x0104).
See https://github.com/davidrapan/ha-solarman/issues/1191
"""

from sunsynk import AMPS, CELSIUS, HZ, KWH, VOLT, WATT
from sunsynk.definitions import COMMON
from sunsynk.rwsensors import (
    NumberRWSensor,
    SelectRWSensor,
    SwitchRWSensor,
    SystemTimeRWSensor,
    TimeRWSensor,
)
from sunsynk.sensors import BinarySensor, EnumSensor, Sensor, TempSensor

SENSORS = COMMON.copy()

##########
# Battery
##########
SENSORS += (
    Sensor(1069, "Battery SOC", "%"),
    Sensor(1067, "Battery voltage", VOLT, 0.01),
    Sensor(1068, "Battery current", AMPS, -0.01),  # negative = charging
    Sensor(1071, "Battery power", WATT, -1),  # positive = discharging
    Sensor(1070, "Battery temperature", CELSIUS, -0.1),
    Sensor(408, "Battery cell voltage max", VOLT, 0.001),
    Sensor(409, "Battery cell voltage min", VOLT, 0.001),
    Sensor(410, "Battery cell temperature max", CELSIUS, -0.1),
    Sensor(411, "Battery cell temperature min", CELSIUS, -0.1),
    Sensor(412, "Battery modules"),
    Sensor(407, "Battery capacity", "Ah", 0.1),  # 50 Ah per 2.56 kWh module
    Sensor(392, "Battery SOH", "%"),
)

######
# BMS
######
SENSORS += (
    Sensor(372, "BMS charge voltage", VOLT, 0.01),
    Sensor(374, "Battery charge limit current", AMPS),  # drops near full
    Sensor(375, "Battery discharge limit current", AMPS),
    Sensor(376, "BMS SOC", "%"),
    Sensor(377, "BMS voltage", VOLT, 0.01),
    Sensor(378, "BMS current", AMPS, -1),
    Sensor(379, "BMS temperature", CELSIUS, -0.1),
)

#######
# Grid
#######
SENSORS += (
    Sensor(1034, "Grid voltage", VOLT, 0.1),
    Sensor(1035, "Grid frequency", HZ, 0.01),
    Sensor(1078, "Grid current", AMPS, 0.1),
    Sensor(1083, "Grid power", WATT, -1),  # negative = export
    BinarySensor(1080, "Grid connected", on=2),  # 2 = on-grid, 3 = off-grid
)

##################
# UPS (load) port
##################
SENSORS += (
    Sensor(1033, "Load voltage", VOLT, 0.1),
    Sensor(1037, "Load frequency", HZ, 0.01),
    Sensor(1087, "Load power", WATT),
)

###########
# Inverter
###########
SENSORS += (
    # negative while charging from the grid, positive on battery
    Sensor((1028, 1029), "Inverter power", WATT, -0.1),
    Sensor(1081, "Inverter current", AMPS, 0.1),
    TempSensor(1032, "Radiator temperature", CELSIUS, 0.01, offset=10),
    Sensor(1127, "Inverter temperature", CELSIUS),
    EnumSensor(1001, "Overall state", options={2: "ok"}, unknown="unknown {}"),
)

#########
# Energy
#########
# Totals: the high words (1075, 1077, 1092, 1094, 1100) are 0 so far, assumed 32-bit
# like the hybrids. 1093 already reads 8.3 kWh out of the box (factory test).
SENSORS += (
    Sensor(1073, "Day battery charge", KWH, 0.1),
    Sensor(1072, "Day battery discharge", KWH, 0.1),
    Sensor(1089, "Day grid import", KWH, 0.1),
    Sensor(1090, "Day grid export", KWH, 0.1),
    Sensor(1098, "Day load energy", KWH, 0.1),
    Sensor((1076, 1077), "Total battery charge", KWH, 0.1),
    Sensor((1074, 1075), "Total battery discharge", KWH, 0.1),
    Sensor((1091, 1092), "Total grid import", KWH, 0.1),
    Sensor((1093, 1094), "Total grid export", KWH, 0.1),
    Sensor((1099, 1100), "Total load energy", KWH, 0.1),
)

##########
# General
##########
RATED_POWER = Sensor(17, "Rated power", WATT, 0.1)

SENSORS += (
    RATED_POWER,
    SystemTimeRWSensor((22, 23, 24), "Date time", unit=""),
)

###########
# Settings
###########
BATTERY_LOW_CAP = NumberRWSensor(321, "Battery low capacity", "%", max=50)
BATTERY_SHUTDOWN_CAP = NumberRWSensor(
    319, "Battery shutdown capacity", "%", max=BATTERY_LOW_CAP
)
BATTERY_LOW_CAP.min = BATTERY_SHUTDOWN_CAP
BATTERY_RESTART_CAP = NumberRWSensor(
    320, "Battery restart capacity", "%", min=BATTERY_LOW_CAP
)

SENSORS += (
    BATTERY_SHUTDOWN_CAP,
    BATTERY_RESTART_CAP,
    BATTERY_LOW_CAP,
    NumberRWSensor(312, "Battery Max Charge current", AMPS, 0.01, min=5, max=50),
    NumberRWSensor(313, "Battery Max Discharge current", AMPS, 0.01, min=5, max=50),
    SelectRWSensor(
        334,
        "Work mode",
        options={0: "Green Power", 2: "Full Charge", 3: "Customized"},
    ),
    # Only stored outside Full Charge; selecting Full Charge resets it to 0
    SwitchRWSensor(335, "Use Timer", on=1),
    SwitchRWSensor(328, "Grid charge enabled", on=1),
    SelectRWSensor(329, "Priority Load", options={0: "Battery first", 1: "Load first"}),
    SwitchRWSensor(333, "Solar Export", on=1),
    NumberRWSensor(331, "Max Sell power", WATT, min=0, max=RATED_POWER),
    # Read-only on purpose, this is the export guard
    EnumSensor(
        330,
        "Load Limit",
        options={
            0: "Allow Export",
            1: "Zero Export To UPS Load",
            2: "Zero Export To CT",
            3: "Zero Export To Wireless CT",
        },
    ),
)

#################
# System program
#################
# Used in Customized mode with Use Timer on. Slot N ends where slot N+1 starts.
# Prog power does not cap battery-to-load discharge (tested 2500/200/0 W).
PROG1_TIME = TimeRWSensor(336, "Prog1 Time")
PROG2_TIME = TimeRWSensor(337, "Prog2 Time", min=PROG1_TIME)
PROG3_TIME = TimeRWSensor(338, "Prog3 Time", min=PROG2_TIME)
PROG4_TIME = TimeRWSensor(339, "Prog4 Time", min=PROG3_TIME)
PROG5_TIME = TimeRWSensor(340, "Prog5 Time", min=PROG4_TIME)
PROG6_TIME = TimeRWSensor(341, "Prog6 Time", min=PROG5_TIME)
PROG1_TIME.min = PROG6_TIME
PROG1_TIME.max = PROG2_TIME
PROG2_TIME.max = PROG3_TIME
PROG3_TIME.max = PROG4_TIME
PROG4_TIME.max = PROG5_TIME
PROG5_TIME.max = PROG6_TIME
PROG6_TIME.max = PROG1_TIME
SENSORS += (PROG1_TIME, PROG2_TIME, PROG3_TIME, PROG4_TIME, PROG5_TIME, PROG6_TIME)

SENSORS += (
    NumberRWSensor(342, "Prog1 power", WATT, max=RATED_POWER),
    NumberRWSensor(343, "Prog2 power", WATT, max=RATED_POWER),
    NumberRWSensor(344, "Prog3 power", WATT, max=RATED_POWER),
    NumberRWSensor(345, "Prog4 power", WATT, max=RATED_POWER),
    NumberRWSensor(346, "Prog5 power", WATT, max=RATED_POWER),
    NumberRWSensor(347, "Prog6 power", WATT, max=RATED_POWER),
    # 348-353 read 49.00 V and are not shown in the app
    NumberRWSensor(354, "Prog1 Capacity", "%", min=BATTERY_LOW_CAP),
    NumberRWSensor(355, "Prog2 Capacity", "%", min=BATTERY_LOW_CAP),
    NumberRWSensor(356, "Prog3 Capacity", "%", min=BATTERY_LOW_CAP),
    NumberRWSensor(357, "Prog4 Capacity", "%", min=BATTERY_LOW_CAP),
    NumberRWSensor(358, "Prog5 Capacity", "%", min=BATTERY_LOW_CAP),
    NumberRWSensor(359, "Prog6 Capacity", "%", min=BATTERY_LOW_CAP),
    SwitchRWSensor(360, "Prog1 charge", on=1),
    SwitchRWSensor(361, "Prog2 charge", on=1),
    SwitchRWSensor(362, "Prog3 charge", on=1),
    SwitchRWSensor(363, "Prog4 charge", on=1),
    SwitchRWSensor(364, "Prog5 charge", on=1),
    SwitchRWSensor(365, "Prog6 charge", on=1),
)

####################
# Function settings
####################
# Read-only on purpose: grid code and safety settings
SENSORS += (
    Sensor(32, "Grid reconnect delay", "s"),
    BinarySensor(34, "Inverter enabled"),
    BinarySensor(35, "Island mode"),
    BinarySensor(36, "Insulation check"),
    BinarySensor(38, "Neutral to earth"),
)
