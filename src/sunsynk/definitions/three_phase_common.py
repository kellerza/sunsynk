"""Sunsynk 5kW&8kW hybrid 3-phase inverter sensor definitions."""

from sunsynk import AMPS, CELSIUS, KWH, VOLT, WATT
from sunsynk.definitions import (
    COMMON,
    PROG_CHARGE_OPTIONS,
    PROG_MODE_OPTIONS,
)
from sunsynk.rwsensors import (
    NumberRWSensor,
    SelectRWSensor,
    SwitchRWSensor,
    SystemTimeRWSensor,
    TimeRWSensor,
)
from sunsynk.sensors import (
    BinarySensor,
    EnumSensor,
    FaultSensor,
    InverterStateSensor,
    MathSensor,
    Sensor,
    TempSensor,
)

SENSORS = COMMON.copy()

#################
# Inverter Power
#################
SENSORS += (
    Sensor(636, "Inverter power", WATT, -1),
    Sensor(633, "Inverter L1 power", WATT, -1),
    Sensor(634, "Inverter L2 power", WATT, -1),
    Sensor(635, "Inverter L3 power", WATT, -1),
    Sensor(627, "Inverter L1 voltage", VOLT, 0.1),
    Sensor(628, "Inverter L2 voltage", VOLT, 0.1),
    Sensor(629, "Inverter L3 voltage", VOLT, 0.1),
    Sensor(630, "Inverter L1 current", AMPS, -0.01),
    Sensor(631, "Inverter L2 current", AMPS, -0.01),
    Sensor(632, "Inverter L3 current", AMPS, -0.01),
    Sensor(638, "Inverter frequency", "Hz", 0.01),
)

#############
# Grid Power
#############
SENSORS += (
    Sensor(609, "Grid frequency", "Hz", 0.01),
    Sensor(625, "Grid power", WATT, -1),  # gridTotalPac
    Sensor(622, "Grid L1 power", WATT, -1),  # aPower
    Sensor(623, "Grid L2 power", WATT, -1),  # bPower
    Sensor(624, "Grid L3 power", WATT, -1),  # cPower
    Sensor(598, "Grid L1 voltage", VOLT, 0.1),  # aLineVolt
    Sensor(599, "Grid L2 voltage", VOLT, 0.1),  # bLineVolt
    Sensor(600, "Grid L3 voltage", VOLT, 0.1),  # cLineVolt
    Sensor(604, "A Phase Power on the Inner Side of the Grid", "W"),
    Sensor(605, "B Phase Power on the Inner Side of the Grid", "W"),
    Sensor(606, "C Phase Power on the Inner Side of the Grid", "W"),
    Sensor(607, "Total Active Power from Side to Side of the Grid", "W", -1),
    Sensor(608, "Grid Side - Inside Total Apparent Power", "W"),
    MathSensor(
        (610, 611, 612), "Grid current", AMPS, factors=(0.01, 0.01, 0.01)
    ),  # iac1,iac2,iac3
    Sensor(616, "Grid CT L1 power", WATT, -1),  # aPower
    Sensor(617, "Grid CT L2 power", WATT, -1),  # bPower
    Sensor(618, "Grid CT L3 power", WATT, -1),  # cPower
    Sensor(619, "Grid CT power", WATT, -1),  # totalPower
)

#############
# Load Power
#############
SENSORS += (
    Sensor(653, "Load power", WATT, -1),
    Sensor(650, "Load L1 power", WATT, -1),
    Sensor(651, "Load L2 power", WATT, -1),
    Sensor(652, "Load L3 power", WATT, -1),
    Sensor(644, "Load L1 voltage", VOLT, 0.1),
    Sensor(645, "Load L2 voltage", VOLT, 0.1),
    Sensor(646, "Load L3 voltage", VOLT, 0.1),
    Sensor(655, "Load frequency", "Hz", 0.01),
)

##############
# Solar Power
##############
SENSORS += (
    MathSensor(
        (672, 673, 674, 675), "PV power", WATT, factors=(1, 1, 1, 1)
    ),  # pv1,pv2,pv3,pv4 power
)

#####################
# MPPT 1 Solar Power
#####################
SENSORS += (
    Sensor(672, "PV1 power", WATT, -1),
    Sensor(676, "PV1 voltage", VOLT, 0.1),
    Sensor(677, "PV1 current", AMPS, 0.1),
)

#####################
# MPPT2 Solar Power
#####################
SENSORS += (
    Sensor(673, "PV2 power", WATT, -1),
    Sensor(678, "PV2 voltage", VOLT, 0.1),
    Sensor(679, "PV2 current", AMPS, 0.1),
)

#####################
# MPPT 3 Solar Power
#####################
SENSORS += (  # Deye 3 Phase  only has 2 MPPT)
    Sensor(674, "PV3 power", WATT, -1),
    Sensor(680, "PV3 voltage", VOLT, 0.1),
    Sensor(681, "PV3 current", AMPS, 0.1),
)

#####################
# MPPT 4 Solar Power
#####################
SENSORS += (  # Deye 3 Phase  only has 2 MPPT)
    Sensor(675, "PV4 power", WATT, -1),
    Sensor(682, "PV4 voltage", VOLT, 0.1),
    Sensor(683, "PV4 current", AMPS, 0.1),
)


###################
# Power on Outputs (aka GEN - which has multiple modes on the deye 3 Phase )
###################
SENSORS += (
    Sensor(661, "Gen L1 volts", VOLT, 0.1),
    Sensor(662, "Gen L2 volts", VOLT, 0.1),
    Sensor(663, "Gen L3 volts", VOLT, 0.1),
    Sensor(664, "Gen L1 power", WATT, -1),
    Sensor(665, "Gen L2 power", WATT, -1),
    Sensor(666, "Gen L3 power", WATT, -1),
    Sensor(667, "Gen power", WATT, -1),
)

###################
# Energy
###################
SENSORS += (
    Sensor(502, "Day Active Energy", KWH, -0.1),
    Sensor(514, "Day Battery Charge", KWH, 0.1),
    Sensor(515, "Day Battery discharge", KWH, 0.1),
    Sensor(521, "Day Grid Export", KWH, 0.1),
    Sensor(520, "Day Grid Import", KWH, 0.1),
    Sensor(536, "Day Gen Energy", KWH, 0.1),
    Sensor(526, "Day Load Energy", KWH, 0.1),  # I guess "used" = load?
    Sensor(529, "Day PV Energy", KWH, 0.1),
    Sensor((506, 507), "Total Active Energy", KWH, 0.1),  # signed?
    Sensor((516, 517), "Total Battery Charge", KWH, 0.1),
    Sensor((518, 519), "Total Battery Discharge", KWH, 0.1),
    Sensor((524, 525), "Total Grid Export", KWH, 0.1),
    Sensor((522, 523), "Total Grid Import", KWH, 0.1),
    Sensor((527, 528), "Total Load Energy", KWH, 0.1),
    Sensor((534, 535), "Total PV Energy", KWH, 0.1),
)

##########
# General
##########
RATED_POWER = Sensor((20, 21), "Rated power", WATT, 0.1)

SENSORS += (
    RATED_POWER,
    FaultSensor((555, 556, 557, 558), "Fault"),
    InverterStateSensor(500, "Overall state"),
    # SDStatusSensor(0, "SD Status", ""),  # type: ignore        # 3 Phase does not have SD Card but crashes when removed
    TempSensor(540, "DC transformer temperature", CELSIUS, 0.1),
    TempSensor(541, "Radiator temperature", CELSIUS, 0.1),
    BinarySensor(552, "Grid Connected", bitmask=1 << 2),
    SystemTimeRWSensor((62, 63, 64), "Date Time", unit=""),
)

##############
# AC Relay status
##############
SENSORS += (
    BinarySensor(552, "INV Relay Status", bitmask=1 << 0),
    BinarySensor(552, "Undefined Load Relay Status", bitmask=1 << 1),
    BinarySensor(552, "Grid Relay Status", bitmask=1 << 2),
    BinarySensor(552, "Generator Relay Status", bitmask=1 << 3),
    BinarySensor(552, "Grid Give Power to Relay Status", bitmask=1 << 4),
    BinarySensor(552, "Dry Contact1 Status", bitmask=1 << 5),
    BinarySensor(552, "Dry Contact2 Status", bitmask=1 << 6),
)

###########
# Settings
###########
SENSORS += (
    NumberRWSensor(128, "Grid Charge Battery current", AMPS, max=240),
    NumberRWSensor(127, "Grid Charge Start Battery SOC", "%"),
    SwitchRWSensor(130, "Grid Charge enabled", on=1),
    SwitchRWSensor(146, "Use Timer"),
    SwitchRWSensor(145, "Solar Export", on=1),
    NumberRWSensor(143, "Export Limit power", WATT, max=RATED_POWER),
    NumberRWSensor(108, "Battery Max Charge current", AMPS, max=240),
    NumberRWSensor(109, "Battery Max Discharge current", AMPS, max=240),
    NumberRWSensor(102, "Battery Capacity current", AMPS, max=2000),
    NumberRWSensor(191, "Grid Peak Shaving power", WATT, max=100000),
    NumberRWSensor(340, "Max Solar power", WATT, max=12000),
)

# Additional optional sensors
SENSORS += (
    NumberRWSensor(
        103, "Battery low voltage", VOLT, -0.1
    ),  # interesting perhaps not available in menu. default 4500 (45V)
    NumberRWSensor(104, "System Zero Export power", WATT, -1, min=-500, max=500),
    NumberRWSensor(105, "Battery Equalization Days", "days", -1),
    NumberRWSensor(106, "Battery Equalization Hours", "h", -1),  # 1 = 0.5 hours
    SwitchRWSensor(129, "Generator Charge enabled"),
    SelectRWSensor(
        111,
        "Battery Type",
        options={0: "Use Battery Voltage", 1: "Lithium (Use BMS)", 2: "No Battery"},
    ),
    SelectRWSensor(
        112,
        "Battery Wake Up",
        options={0: "Enabled", 1 << 0: "Disabled"},
        bitmask=1 << 0,
    ),  # according to docs, 0 is enabled for this one
    NumberRWSensor(113, "Battery Resistance", "mΩ", max=6000),
    Sensor(114, "Battery Charge Efficiency", "%", 0.1),
    SelectRWSensor(
        133,
        "Generator Port Usage",
        options={0: "Generator", 1: "Smartload", 2: "Micro Inverter"},
    ),
)

# Absolute min and max voltage based on Deye inverter
MIN_VOLT = 41
MAX_VOLT = 60

BATTERY_EQUALIZATION_VOLT = NumberRWSensor(
    99, "Battery Equalization voltage", VOLT, 0.01, min=MIN_VOLT, max=MAX_VOLT
)
BATTERY_ABSORPTION_VOLT = NumberRWSensor(
    100, "Battery Absorption voltage", VOLT, 0.01, min=MIN_VOLT, max=MAX_VOLT
)
BATTERY_FLOAT_VOLT = NumberRWSensor(
    101, "Battery Float voltage", VOLT, 0.01, min=MIN_VOLT, max=MAX_VOLT
)

BATTERY_SHUTDOWN_CAP = NumberRWSensor(115, "Battery Shutdown Capacity", "%")
BATTERY_RESTART_CAP = NumberRWSensor(116, "Battery Restart Capacity", "%")
BATTERY_LOW_CAP = NumberRWSensor(
    117,
    "Battery Low Capacity",
    "%",
    min=BATTERY_SHUTDOWN_CAP,
    max=BATTERY_RESTART_CAP,
)
BATTERY_SHUTDOWN_CAP.max = BATTERY_LOW_CAP
BATTERY_RESTART_CAP.min = BATTERY_LOW_CAP

BATTERY_SHUTDOWN_VOLT = NumberRWSensor(
    118, "Battery Shutdown voltage", VOLT, 0.01, min=MIN_VOLT
)
BATTERY_LOW_VOLT = NumberRWSensor(
    120, "Battery Low voltage", VOLT, 0.01, min=BATTERY_SHUTDOWN_VOLT, max=MAX_VOLT
)
BATTERY_RESTART_VOLT = NumberRWSensor(
    119, "Battery Restart voltage", VOLT, 0.01, max=MAX_VOLT
)
BATTERY_SHUTDOWN_VOLT.max = BATTERY_LOW_VOLT
BATTERY_RESTART_VOLT.min = BATTERY_LOW_VOLT

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

SENSORS += SwitchRWSensor(141, "Priority Load")

SENSORS += SelectRWSensor(
    142,
    "Load Limit",
    options={0: "Allow Export", 1: "Essentials", 2: "Zero Export"},
)

PROG1_TIME = TimeRWSensor(148, "Prog1 Time")
PROG2_TIME = TimeRWSensor(149, "Prog2 Time", min=PROG1_TIME)
PROG3_TIME = TimeRWSensor(150, "Prog3 Time", min=PROG2_TIME)
PROG4_TIME = TimeRWSensor(151, "Prog4 Time", min=PROG3_TIME)
PROG5_TIME = TimeRWSensor(152, "Prog5 Time", min=PROG4_TIME)
PROG6_TIME = TimeRWSensor(153, "Prog6 Time", min=PROG5_TIME)
PROG1_TIME.min = PROG6_TIME
PROG1_TIME.max = PROG2_TIME
PROG2_TIME.max = PROG3_TIME
PROG3_TIME.max = PROG4_TIME
PROG4_TIME.max = PROG5_TIME
PROG5_TIME.max = PROG6_TIME
PROG6_TIME.max = PROG1_TIME
SENSORS += (PROG1_TIME, PROG2_TIME, PROG3_TIME, PROG4_TIME, PROG5_TIME, PROG6_TIME)

SENSORS += (
    SwitchRWSensor(
        146,
        "Prog Time Of Use Enabled",
        on=1 << 0,
        bitmask=1 << 0,
    ),
    SwitchRWSensor(146, "Prog Monday Enabled", on=1 << 1, bitmask=1 << 1),
    SwitchRWSensor(146, "Prog Tuesday Enabled", on=1 << 2, bitmask=1 << 2),
    SwitchRWSensor(146, "Prog Wednesday Enabled", on=1 << 3, bitmask=1 << 3),
    SwitchRWSensor(146, "Prog Thursday Enabled", on=1 << 4, bitmask=1 << 4),
    SwitchRWSensor(146, "Prog Friday Enabled", on=1 << 5, bitmask=1 << 5),
    SwitchRWSensor(146, "Prog Saturday Enabled", on=1 << 6, bitmask=1 << 6),
    SwitchRWSensor(146, "Prog Sunday Enabled", on=1 << 7, bitmask=1 << 7),
)

SENSORS += (
    NumberRWSensor(154, "Prog1 power", WATT, max=RATED_POWER),
    NumberRWSensor(155, "Prog2 power", WATT, max=RATED_POWER),
    NumberRWSensor(156, "Prog3 power", WATT, max=RATED_POWER),
    NumberRWSensor(157, "Prog4 power", WATT, max=RATED_POWER),
    NumberRWSensor(158, "Prog5 power", WATT, max=RATED_POWER),
    NumberRWSensor(159, "Prog6 power", WATT, max=RATED_POWER),
    NumberRWSensor(166, "Prog1 Capacity", "%", min=BATTERY_LOW_CAP),
    NumberRWSensor(167, "Prog2 Capacity", "%", min=BATTERY_LOW_CAP),
    NumberRWSensor(168, "Prog3 Capacity", "%", min=BATTERY_LOW_CAP),
    NumberRWSensor(169, "Prog4 Capacity", "%", min=BATTERY_LOW_CAP),
    NumberRWSensor(170, "Prog5 Capacity", "%", min=BATTERY_LOW_CAP),
    NumberRWSensor(171, "Prog6 Capacity", "%", min=BATTERY_LOW_CAP),
    SelectRWSensor(172, "Prog1 charge", options=PROG_CHARGE_OPTIONS, bitmask=0x03),
    SelectRWSensor(173, "Prog2 charge", options=PROG_CHARGE_OPTIONS, bitmask=0x03),
    SelectRWSensor(174, "Prog3 charge", options=PROG_CHARGE_OPTIONS, bitmask=0x03),
    SelectRWSensor(175, "Prog4 charge", options=PROG_CHARGE_OPTIONS, bitmask=0x03),
    SelectRWSensor(176, "Prog5 charge", options=PROG_CHARGE_OPTIONS, bitmask=0x03),
    SelectRWSensor(177, "Prog6 charge", options=PROG_CHARGE_OPTIONS, bitmask=0x03),
    SelectRWSensor(172, "Prog1 mode", options=PROG_MODE_OPTIONS, bitmask=0x1C),
    SelectRWSensor(173, "Prog2 mode", options=PROG_MODE_OPTIONS, bitmask=0x1C),
    SelectRWSensor(174, "Prog3 mode", options=PROG_MODE_OPTIONS, bitmask=0x1C),
    SelectRWSensor(175, "Prog4 mode", options=PROG_MODE_OPTIONS, bitmask=0x1C),
    SelectRWSensor(176, "Prog5 mode", options=PROG_MODE_OPTIONS, bitmask=0x1C),
    SelectRWSensor(177, "Prog6 mode", options=PROG_MODE_OPTIONS, bitmask=0x1C),
)


SENSORS += (
    NumberRWSensor(
        160, "Prog1 voltage", VOLT, 0.01, min=BATTERY_LOW_VOLT, max=BATTERY_FLOAT_VOLT
    ),
    NumberRWSensor(
        161, "Prog2 voltage", VOLT, 0.01, min=BATTERY_LOW_VOLT, max=BATTERY_FLOAT_VOLT
    ),
    NumberRWSensor(
        162, "Prog3 voltage", VOLT, 0.01, min=BATTERY_LOW_VOLT, max=BATTERY_FLOAT_VOLT
    ),
    NumberRWSensor(
        163, "Prog4 voltage", VOLT, 0.01, min=BATTERY_LOW_VOLT, max=BATTERY_FLOAT_VOLT
    ),
    NumberRWSensor(
        164, "Prog5 voltage", VOLT, 0.01, min=BATTERY_LOW_VOLT, max=BATTERY_FLOAT_VOLT
    ),
    NumberRWSensor(
        165, "Prog6 voltage", VOLT, 0.01, min=BATTERY_LOW_VOLT, max=BATTERY_FLOAT_VOLT
    ),
)

########
# Other
########
SENSORS += (
    SelectRWSensor(
        178,
        "Microinverter export to grid cutoff",
        options={0b10 << 0: "Disable", 0b11 << 0: "Enable"},
        bitmask=0b11 << 0,
    ),
    SelectRWSensor(
        178,
        "Gen peak-shaving",
        options={0b10 << 2: "Disable", 0b11 << 2: "Enable"},
        bitmask=0b11 << 2,
    ),
    SelectRWSensor(
        178,
        "Grid peak-shaving",
        options={0b10 << 4: "Disable", 0b11 << 4: "Enable"},
        bitmask=0b11 << 4,
    ),
    SelectRWSensor(
        178,
        "On Grid always on",
        options={0b10 << 6: "Disable", 0b11 << 6: "Enable"},
        bitmask=0b11 << 6,
    ),
    SelectRWSensor(
        178,
        "External relay",
        options={0b10 << 8: "Disable", 0b11 << 8: "Enable"},
        bitmask=0b11 << 8,
    ),
    SelectRWSensor(
        178,
        "Loss of lithium battery report fault",
        options={0b10 << 10: "Disable", 0b11 << 10: "Enable"},
        bitmask=0b11 << 10,
    ),
    SelectRWSensor(
        178,
        "DRM",
        options={0b10 << 12: "Disable", 0b11 << 12: "Enable"},
        bitmask=0b11 << 12,
    ),
    SelectRWSensor(
        178,
        "US version grounding fault",
        options={0b10 << 14: "Disable", 0b11 << 14: "Enable"},
        bitmask=0b11 << 14,
    ),
)

SENSORS += (
    NumberRWSensor(131, "Generator AC Couple Frz High", "Hz", 0.01),
    NumberRWSensor(135, "Generator Off SOC", "%"),
    NumberRWSensor(137, "Generator On SOC", "%"),
    NumberRWSensor(121, "Generator Max Operating Time", "Hours", 0.1),
    NumberRWSensor(122, "Generator Cooling Time", "Hours", 0.1),
    NumberRWSensor(139, "Min PV Power for Gen Start", WATT),
    SwitchRWSensor(140, "Grid Signal On", on=1 << 0, bitmask=1 << 0),
    SwitchRWSensor(140, "Gen Signal On", on=1 << 1, bitmask=1 << 1),
)

#################
# Advanced Grid Configuration Settings
#################
SENSORS += (
    SelectRWSensor(
        182,
        "Grid Standard",
        options={
            0: "Generic",
            1: "IEEE1547",
            2: "RULE21",
            3: "SRD_UL1741",
            4: "CEI_0_21",
            5: "EN50549_CZ",  # Czech >16A
            6: "AS4777_A",  # Australia A
            7: "AS4777_B",  # Australia B
            8: "AS4777_C",  # Australia C
            9: "AS4777_NewZealand",
            10: "VDE4105",  # Germany
            11: "OVE_Directive_R25",  # Austria
            12: "EN50549_CZ_PPDS_L16A",  # Czech <16A
        },
    ),
    SelectRWSensor(183, "Configured Grid Frequency", options={0: "50Hz", 1: "60Hz"}),
    SelectRWSensor(
        184,
        "Configured Grid Phases",
        options={0: "Three Phase", 1: "Single Phase", 2: "Split Phase"},
    ),
)
#################
# Advanced Inverter Software Configuration Settings
#################
SENSORS += (  ### no idea why there is a "no work" option, but it's in the spec
    SelectRWSensor(
        228,
        "Time synchronization",
        options={
            # 0: "No work",
            0b01 << 0: "No work",
            0b10 << 0: "Disable",
            0b11 << 0: "Enable",
        },
        bitmask=0b11 << 0,
    ),
    SelectRWSensor(
        228,
        "Beep",
        options={
            # 0: "No work",
            0b01 << 2: "No work",
            0b10 << 2: "Disable",
            0b11 << 2: "Enable",
        },
        bitmask=0b11 << 2,
    ),
    SelectRWSensor(
        228,
        "AM PM",
        options={
            # 0: "No work",
            0b01 << 4: "No work",
            0b10 << 4: "Disable",
            0b11 << 4: "Enable",
        },
        bitmask=0b11 << 4,
    ),
    SelectRWSensor(
        228,
        "Auto dim",
        options={
            # 0: "No work",
            0b01 << 6: "No work",
            0b10 << 6: "Disable",
            0b11 << 6: "Enable",
        },
        bitmask=0b11 << 6,
    ),
    SelectRWSensor(
        228,
        "Allow Remote",
        options={
            # 0: "No work",
            0b01 << 14: "No work",
            0b10 << 14: "Disable",
            0b11 << 14: "Enable",
        },
        bitmask=0b11 << 14,
    ),
    NumberRWSensor(209, "UPS delay time", "s"),
)
############
# DRM Codes (Australia only)
############
SENSORS += (
    # these are some Australian standard. Found a definition here
    # https://www.gses.com.au/wp-content/uploads/2016/09/GC_AU8-2_4777-2016-updates.pdf
    EnumSensor(
        544,
        "DRM0 Code",
        options={0: "Not Active", 1 << 0: "Shutdown Inverter"},
        bitmask=1 << 0,
    ),
    EnumSensor(
        544,
        "DRM1 Code",
        options={0: "Not Active", 1 << 1: "No Power Consumption"},
        bitmask=1 << 1,
    ),
    EnumSensor(
        544,
        "DRM2 Code",
        options={0: "Not Active", 1 << 2: "Max 50% Power Consumption"},
        bitmask=1 << 2,
    ),
    EnumSensor(
        544,
        "DRM3 Code",
        options={
            0: "Not Active",
            1 << 3: "Max 75% Power Consumption, Source Reactive Power",
        },
        bitmask=1 << 3,
    ),
    EnumSensor(
        544,
        "DRM4 Code",
        options={0: "Not Active", 1 << 4: "Increase Power Consumption"},
        bitmask=1 << 4,
    ),
    EnumSensor(
        544,
        "DRM5 Code",
        options={0: "Not Active", 1 << 5: "No Power Generation"},
        bitmask=1 << 5,
    ),
    EnumSensor(
        544,
        "DRM6 Code",
        options={0: "Not Active", 1 << 6: "Max 50% Power Generation"},
        bitmask=1 << 6,
    ),
    EnumSensor(
        544,
        "DRM7 Code",
        options={
            0: "Not Active",
            1 << 7: "Max 75% Power Generation, Sink Reactive Power",
        },
        bitmask=1 << 7,
    ),
    EnumSensor(
        544,
        "DRM8 Code",
        options={0: "Not Active", 1 << 8: "Increase Power Generation"},
        bitmask=1 << 8,
    ),
)

SENSORS.deprecated.update(
    {
        "priority_mode": "priority_load",
    }
)
