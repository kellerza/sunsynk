"""Sunsynk high voltage hybrid 3-phase inverter sensor definitions."""
# pylint: disable=duplicate-code
from sunsynk import AMPS, CELSIUS, KWH, VOLT, WATT
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
    HVFaultSensor,
    InverterStateSensor,
    MathSensor,
    SDStatusSensor,
    Sensor,
    SensorDefinitions,
    SerialSensor,
    TempSensor,
)

SENSORS = SensorDefinitions()

##########
# Battery
##########
SENSORS += (
    Sensor(586, "Battery 1 temperature", CELSIUS, 0.1),
    Sensor(587, "Battery 1 voltage", VOLT, 0.1),
    Sensor(588, "Battery 1 SOC", "%"),
    Sensor(590, "Battery 1 power", WATT, -10),
    Sensor(591, "Battery 1 current", AMPS, -0.01),
    Sensor(589, "Battery 2 SOC", "%"),
    Sensor(593, "Battery 2 voltage", VOLT, 0.1),
    Sensor(594, "Battery 2 current", AMPS, -0.01),
    Sensor(595, "Battery 2 power", WATT, -10),
    Sensor(596, "Battery 2 temperature", CELSIUS, 0.1), #this one seems to not follow the convention of other temperatures. 290 = 29c
)

#################
# Inverter Power
#################
SENSORS += (
    Sensor(636, "Inverter power", WATT, -1),
    Sensor(633, "Inverter L1 power", WATT, -1),
    Sensor(634, "Inverter L2 power", WATT, -1),
    Sensor(635, "Inverter L3 power", WATT, -1),
    Sensor(627, "Inverter voltage", VOLT, 0.1),
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
    MathSensor(
        (610, 611, 612), "Grid current", AMPS, factors=(0.01, 0.01, 0.01)
    ),  # iac1,iac2,iac3
    Sensor(619, "Grid CT power", WATT, -1),  # totalPower
    Sensor(616, "Grid CT L1 power", WATT, -1),  # aPower
    Sensor(617, "Grid CT L2 power", WATT, -1),  # bPower
    Sensor(618, "Grid CT L3 power", WATT, -1),  # cPower
    Sensor(604, "A Phase Power on the Inner Side of the Grid", "W"),
    Sensor(605, "B Phase Power on the Inner Side of the Grid", "W"),
    Sensor(606, "C Phase Power on the Inner Side of the Grid", "W"),
    Sensor(607, "Total Active Power from Side to Side of the Grid", "W"),
    Sensor(608, "Grid Side - Inside Total Apparent Power", "W"),
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
)

#
################
# Solar Power
################
SENSORS += (
    MathSensor((672, 673, 674, 675), "PV power", WATT, factors=(10, 10, 10, 10)),  # pv1 power,pv2 power
)
################
# MPPT 1 Solar Power
################
SENSORS += (
    Sensor(672, "PV1 power", WATT, 10),
    Sensor(676, "PV1 voltage", VOLT, 0.1),
    Sensor(677, "PV1 current", AMPS, 0.1),
)

################
# MPPT2 Solar Power
################
SENSORS += (
    Sensor(673, "PV2 power", WATT, 10),
    Sensor(678, "PV2 voltage", VOLT, 0.1),
    Sensor(679, "PV2 current", AMPS, 0.1),
)

################
# MPPT3 Solar Power
################
SENSORS += (
    Sensor(674, "PV3 power", WATT, 10),
    Sensor(680, "PV3 voltage", VOLT, 0.1),
    Sensor(681, "PV3 current", AMPS, 0.1),
)

################
# MPPT4 Solar Power
################
SENSORS += (
    Sensor(675, "PV4 power", WATT, 10),
    Sensor(682, "PV4 voltage", VOLT, 0.1),
    Sensor(683, "PV4 current", AMPS, 0.1),
)


###################
# Power on Outputs (aka GEN - which has multiple modes on the deye 3 Phase )
###################
SENSORS += (
    Sensor(667, "Gen power", WATT, -1),
    Sensor(664, "Gen L1 power", WATT, -1),
    Sensor(665, "Gen L2 power", WATT, -1),
    Sensor(666, "Gen L3 power", WATT, -1),
    Sensor(661, "Gen L1 volts", VOLT, 0.1),
    Sensor(662, "Gen L2 volts", VOLT, 0.1),
    Sensor(663, "Gen L3 volts", VOLT, 0.1),
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
SENSORS += RATED_POWER

SENSORS += (
    Sensor(
        0, "Device Type"
    ),  # {2: "Inverter", 3: "Hybrid Inverter", 4: "Micro Inverter", 5: "3 Phase Hybrid Inverter" }),
    HVFaultSensor((555, 556, 557, 558), "Fault"),
    EnumSensor(553, "Fan Warning", {0: "No Warning", 1: "Warning"}, bitmask=0x02),
    EnumSensor(553, "Grid Phase Warning", {0: "No Warning", 1: "Warning"}, bitmask=0x04),
    EnumSensor(554, "Lithium Battery Loss Warning", {0: "No Warning", 1: "Warning"}, bitmask=0x4000),
    EnumSensor(554, "Parallel Communication Quality Warning", {0: "No Warning", 1: "Warning"}, bitmask=0x8000),
    InverterStateSensor(500, "Overall state"),
    SDStatusSensor(0, "SD Status", ""),  # type: ignore
    SerialSensor((3, 4, 5, 6, 7), "Serial"),
    TempSensor(540, "DC transformer temperature", CELSIUS, 0.1),
    TempSensor(541, "Radiator temperature", CELSIUS, 0.1),
    Sensor(
        552, "Grid Connected Status"
    ),  # Bit 0 = INV Relay, 1 = Undef, 2 = Grid relay, 3 = Gen relay, 4 = Grid give, 5, Dry contact
    BinarySensor(194, "Grid Connected", bitmask=1 << 2),
    SystemTimeRWSensor((62, 63, 64), "Date Time", unit=""),
)

##############
# Relay status
##############
SENSORS += (
    EnumSensor(552, "INV Relay Status", {0: "Off", 1: "On"}, bitmask=0x01),
    EnumSensor(552, "Undefined Load Relay Status", {0: "Off", 1: "On"}, bitmask=0x02),
    EnumSensor(552, "Grid Relay Status", {0: "Off", 1: "On"}, bitmask=0x04),
    EnumSensor(552, "Generator Relay Status", {0: "Off", 1: "On"}, bitmask=0x08),
    EnumSensor(552, "Grid Give Power to Relay Status", {0: "Off", 1: "On"}, bitmask=0x10),
    EnumSensor(552, "Dry Contact1 Status", {0: "Off", 1: "On"}, bitmask=0x80),
    EnumSensor(552, "Dry Contact2 Status", {0: "Off", 1: "On"}, bitmask=0x100),
)

###########
# Settings
###########
SENSORS += (
    NumberRWSensor(128, "Grid Charge Battery current", AMPS, max=210),
    SwitchRWSensor(130, "Grid Charge enabled"),
    NumberRWSensor(127, "Grid Charge Start Battery SOC", "%"),
    SwitchRWSensor(146, "Use Timer", on=255),
    SwitchRWSensor(145, "Solar Export"),
    NumberRWSensor(143, "Export Limit power", WATT, max=RATED_POWER),
    NumberRWSensor(108, "Battery Max Charge current", AMPS, max=210),
    NumberRWSensor(109, "Battery Max Discharge current", AMPS, max=210),
    NumberRWSensor(102, "Battery Capacity current", "Ah", max=2000),
)

# Additional optional sensors
SENSORS += (
    NumberRWSensor(
        103, "Battery low voltage", VOLT, -0.1
    ),  # interesting perhaps not available in menu. default 4500 (45V)
    SelectRWSensor(
        133,
        "Generator Port Usage",
        options={0: "Generator", 1: "Smartload", 2: "Micro Inverter"},
    ),
    SelectRWSensor(129, "Generator Charge enabled", options={0: "Off", 1: "On"}),
    NumberRWSensor(124, "Generator Charge Start Battery SOC", "%"),
    NumberRWSensor(125, "Generator Charge Battery current", AMPS),
    SelectRWSensor(110, "Parallel Battery 1 and 2", options={0: "Off", 1: "On"}),
    SelectRWSensor(112, "Battery 1 Wake Up", options={0: "Enabled", 1: "Disabled"}, bitmask=0x01), #according to docs, 0 is enabled for this one
    SelectRWSensor(112, "Battery 2 Wake Up", options={0: "Enabled", 256: "Disabled"}, bitmask=0x0100), #according to docs, 0 is enabled for this one
    NumberRWSensor(113, "Battery Resistance", "mΩ", max=6000),
    Sensor(114, "Battery Charge Efficiency", "%", 0.1),
    NumberRWSensor(104, "System Zero Export power", WATT, -1),
    NumberRWSensor(105, "Battery Equalization Days", "days", -1),
    NumberRWSensor(106, "Battery Equalization Hours", "h", -1),  # 1 = 0.5 hours
    
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

BATTERY_MODE = SelectRWSensor(111, "Battery Type", options={0: "Use Battery Voltage", 1: "Lithium (Use BMS)", 2: "No Battery"})

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
    BATTERY_MODE,
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
    options={0: "Allow Export", 1: "Zero Export To Load", 2: "Zero Export To CT"},
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

PROG_CHARGE_OPTIONS = {
    0: "Off",
    1: "Grid Only",
    2: "Gen Only",
    3: "Grid and Gen",
}

SENSORS += (
    PROG1_TIME,
    PROG2_TIME,
    PROG3_TIME,
    PROG4_TIME,
    PROG5_TIME,
    PROG6_TIME,
    NumberRWSensor(154, "Prog1 power", WATT, 10, max=RATED_POWER),
    NumberRWSensor(155, "Prog2 power", WATT, 10, max=RATED_POWER),
    NumberRWSensor(156, "Prog3 power", WATT, 10, max=RATED_POWER),
    NumberRWSensor(157, "Prog4 power", WATT, 10, max=RATED_POWER),
    NumberRWSensor(158, "Prog5 power", WATT, 10, max=RATED_POWER),
    NumberRWSensor(159, "Prog6 power", WATT, 10, max=RATED_POWER),
    NumberRWSensor(166, "Prog1 Capacity", "%", min=BATTERY_LOW_CAP),
    NumberRWSensor(167, "Prog2 Capacity", "%", min=BATTERY_LOW_CAP),
    NumberRWSensor(168, "Prog3 Capacity", "%", min=BATTERY_LOW_CAP),
    NumberRWSensor(169, "Prog4 Capacity", "%", min=BATTERY_LOW_CAP),
    NumberRWSensor(170, "Prog5 Capacity", "%", min=BATTERY_LOW_CAP),
    NumberRWSensor(171, "Prog6 Capacity", "%", min=BATTERY_LOW_CAP),
    SelectRWSensor(172, "Prog1 charge", options=PROG_CHARGE_OPTIONS),
    SelectRWSensor(173, "Prog2 charge", options=PROG_CHARGE_OPTIONS),
    SelectRWSensor(174, "Prog3 charge", options=PROG_CHARGE_OPTIONS),
    SelectRWSensor(175, "Prog4 charge", options=PROG_CHARGE_OPTIONS),
    SelectRWSensor(176, "Prog5 charge", options=PROG_CHARGE_OPTIONS),
    SelectRWSensor(177, "Prog6 charge", options=PROG_CHARGE_OPTIONS),
)

SENSORS += (
    SelectRWSensor(146, "Prog Time Of Use Enabled", options={0: "off", 1: "on"}, bitmask=0x01),
    SelectRWSensor(146, "Prog Monday Enabled", options={0: "off", 2: "on"}, bitmask=0x02),
    SelectRWSensor(146, "Prog Tuesday Enabled", options={0: "off", 4: "on"}, bitmask=0x04),
    SelectRWSensor(146, "Prog Wednesday Enabled", options={0: "off", 8: "on"}, bitmask=0x08),
    SelectRWSensor(146, "Prog Thursday Enabled", options={0: "off", 16: "on"}, bitmask=0x10),
    SelectRWSensor(146, "Prog Friday Enabled", options={0: "off", 32: "on"}, bitmask=0x20),
    SelectRWSensor(146, "Prog Saturday Enabled", options={0: "off", 64: "on"}, bitmask=0x40),
    SelectRWSensor(146, "Prog Sunday Enabled", options={0: "off", 128: "on"}, bitmask=0x80),
)


SENSORS += (
    NumberRWSensor(
        160,
        "Prog1 voltage",
        VOLT,
        0.01,
        min=BATTERY_LOW_VOLT,
        max=BATTERY_FLOAT_VOLT,
    ),
    NumberRWSensor(
        161,
        "Prog2 voltage",
        VOLT,
        0.01,
        min=BATTERY_LOW_VOLT,
        max=BATTERY_FLOAT_VOLT,
    ),
    NumberRWSensor(
        162,
        "Prog3 voltage",
        VOLT,
        0.01,
        min=BATTERY_LOW_VOLT,
        max=BATTERY_FLOAT_VOLT,
    ),
    NumberRWSensor(
        163,
        "Prog4 voltage",
        VOLT,
        0.01,
        min=BATTERY_LOW_VOLT,
        max=BATTERY_FLOAT_VOLT,
    ),
    NumberRWSensor(
        164,
        "Prog5 voltage",
        VOLT,
        0.01,
        min=BATTERY_LOW_VOLT,
        max=BATTERY_FLOAT_VOLT,
    ),
    NumberRWSensor(
        165,
        "Prog6 voltage",
        VOLT,
        0.01,
        min=BATTERY_LOW_VOLT,
        max=BATTERY_FLOAT_VOLT,
    ),
)

SENSORS += (
    NumberRWSensor(131, "Generator AC Couple Frz High", "Hz", 0.01),
    NumberRWSensor(135, "Generator Off SOC", "%"),
    NumberRWSensor(137, "Generator On SOC", "%"),
    NumberRWSensor(121, "Generator Max Operating Time", "Hours", 0.1),
    NumberRWSensor(122, "Generator Cooling Time", "Hours", 0.1),
    NumberRWSensor(139, "Min PV Power for Gen Start", WATT),
    SelectRWSensor(140, "Grid Signal On", options={0: "Off", 1: "On"}, bitmask=0x01),
    SelectRWSensor(140, "Gen Signal On", options={0: "Off", 2: "On"}, bitmask=0x02),
  
)
#################
# Advanced Grid Configuration Settings
#################

SENSORS += (
    SelectRWSensor(182, "Grid Standard", options={
        0: "Generic",
        1: "IEEE1547",
        2: "RULE21",
        3: "SRD_UL1741",
        4: "CEI_0_21",
        5: "EN50549_CZ",  # Czech >16A
        6: "AS4777_A", # Australia A
        7: "AS4777_B", # Australia B
        8: "AS4777_C", # Australia C
        9: "AS4777_NewZealand",
        10: "VDE4105",  # Germany
        11: "OVE_Directive_R25",  # Austria
        12: "EN50549_CZ_PPDS_L16A",  # Czech <16A
    }),
    SelectRWSensor(183, "Configured Grid Frequency", options={0: "50Hz", 1: "60Hz"}),
    SelectRWSensor(184, "Configured Grid Phases", options={0: "Three Phase", 1: "Single Phase", 2: "Split Phase"}),
)

#################
# Advanced Battery Configuration Settings/Info
#################
hv_battery_manufacturers={
        0: "No HV battery",
        1: "PYLON_HV",
        2: "DynessHV_HV",
        3: "UZENERGY_HV",
        4: "SOLAX_HV",
        5: "Deye_HV",
        6: "BYD_HV",
        7: "JINKOBSS_HV"
    }
SENSORS += (
    SelectRWSensor(223, "Lithium HV BMS Protocol", options={
        0: "PYLON SOLAX (CAN)",
        1: "Tianbanda RS485 Modbus Protocol (Also BYD CAN)", #according to supported battery documents, this is also set to 1 for BYD CAN... I can confirm this is true as I have this battery/inverter
        2: "KOK Protocol",
        3: "Keith",
        4: "Topai Protocol",
        5: "Pai Energy 485 Protocol",
        6: "Jelis 485 Protocol",
        7: "Xinwangda 485 Protocol",
        8: "Xinruineng 485 Protocol",
        9: "Tianbanda 485 Protocol",
        10: "Shenggao Electrical CAN Protocol",
    }),
    EnumSensor(229, "Battery 1 Manufacturer", options=hv_battery_manufacturers),
    Sensor(210, "Battery 1 BMS charging voltage", VOLT, 0.01),
    Sensor(211, "Battery 1 BMS discharging voltage", VOLT, 0.01),
    Sensor(212, "Battery 1 BMS charging current limit", AMPS),
    Sensor(213, "Battery 1 BMS discharging current limit", AMPS),
    Sensor(214, "Battery 1 BMS SOC", "%"),
    Sensor(215, "Battery 1 BMS voltage", VOLT, 0.01),
    Sensor(216, "Battery 1 BMS current", AMPS),
    TempSensor(217, "Battery 1 BMS temperature", CELSIUS, 0.1),
    Sensor(218, "Battery 1 BMS max charge current limit", AMPS),
    Sensor(219, "Battery 1 BMS max discharge current limit", AMPS),
    Sensor(220, "Battery 1 BMS alarm flag", ""),
    Sensor(221, "Battery 1 BMS fault flag", ""),
    SelectRWSensor(222, "Battery 1 BMS other flag - NULL", options={0: "NULL"}, bitmask=0x01),
    SelectRWSensor(222, "Battery 1 BMS other flag - Battery 1 Force charge", options={0: "off", 1: "on"}, bitmask=0x02),
    SelectRWSensor(222, "Battery 1 BMS other flag - Battery 2 Force charge", options={0: "off", 1: "on"}, bitmask=0x04),
    SelectRWSensor(222, "Battery 1 BMS other flag - Battery 1 Sleep", options={0: "off", 1: "on"}, bitmask=0x08),
    Sensor(223, "Battery 1 BMS type", ""),
    Sensor(224, "Battery 1 BMS SOH", "%"),
    Sensor(225, "Battery 1 BMS software version", ""),
    Sensor(226, "Battery 1 BMS rated AH", "Ah"),
    Sensor(227, "Battery 1 BMS hardware version", ""),
    EnumSensor(230, "Battery 2 Manufacturer", options=hv_battery_manufacturers),
    Sensor(241, "Battery 2 BMS charging voltage", VOLT, 0.1),
    Sensor(242, "Battery 2 BMS discharging voltage", VOLT, 0.1),
    Sensor(243, "Battery 2 BMS charging current limit", AMPS),
    Sensor(244, "Battery 2 BMS discharging current limit", AMPS),
    Sensor(245, "Battery 2 BMS SOC", "%"),
    Sensor(246, "Battery 2 BMS voltage", VOLT, 0.1),
    Sensor(247, "Battery 2 BMS current", AMPS),
    TempSensor(248, "Battery 2 BMS temperature", CELSIUS, 0.1),
    Sensor(249, "Battery 2 BMS max charge current limit", AMPS),
    Sensor(250, "Battery 2 BMS max discharge current limit", AMPS),
    Sensor(251, "Battery 2 BMS alarm flag", ""),
    Sensor(252, "Battery 2 BMS fault flag", ""),
    SelectRWSensor(253, "Battery 2 BMS other flag - NULL", options={0: "NULL"}, bitmask=0x01),
    SelectRWSensor(253, "Battery 2 BMS other flag - Battery 1 Force charge", options={0: "off", 1: "on"}, bitmask=0x02),
    SelectRWSensor(253, "Battery 2 BMS other flag - Battery 2 Force charge", options={0: "off", 1: "on"}, bitmask=0x04),
    SelectRWSensor(253, "Battery 2 BMS other flag - Battery 2 Sleep", options={0: "off", 1: "on"}, bitmask=0x08),
    Sensor(254, "Battery 2 BMS type", ""),
    Sensor(255, "Battery 2 BMS SOH", "%"),
    Sensor(256, "Battery 2 BMS software version", ""),
    Sensor(257, "Battery 2 BMS rated AH", "Ah"),
    Sensor(258, "Battery 2 BMS hardware version", ""),
    
)

#################
# Advanced Inverter Software Configuration Settings
#################
SENSORS += (
    ### no idea why there is a "no work" option, but it's in the spec and for me, beep is set to No Work when I disabled in on the inverter...
    SelectRWSensor(228, "Time synchronization", options={0: "No work", 1: "No work", 2: "Disable", 3: "Enable"}, bitmask=0x03),
    SelectRWSensor(228, "Beep", options={0: "No work", 4: "No work", 8: "Disable", 12: "Enable"}, bitmask=0x0C), # mine was set to 4 after I disabled it on the inverter
    SelectRWSensor(228, "AM PM", options={0: "No work", 16: "No work", 32: "Disable", 48: "Enable"}, bitmask=0x30), #I guess this is 24 hour or AM/PM time display
    SelectRWSensor(228, "Auto dim", options={0: "No work", 64: "No work", 128: "Disable", 192: "Enable"}, bitmask=0xC0),
    SelectRWSensor(228, "Allow Remote", options={0: "No work", 16384: "No work", 32768: "Disable", 49152: "Enable"}, bitmask=0xC000), # mine was set to 32768 from factory (a "no work" option)
    NumberRWSensor(209, "UPS delay time", "s")
)

############
# DRM Codes (Australia only)
############
SENSORS += (
    # these are some Australian standard. Found a definition here https://www.gses.com.au/wp-content/uploads/2016/09/GC_AU8-2_4777-2016-updates.pdf
    EnumSensor(544, "DRM0 Code", {0: "Not Active", 1: "Shutdown Inverter"}, bitmask=0x01),
    EnumSensor(544, "DRM1 Code", {0: "Not Active", 1: "No Power Consumption"}, bitmask=0x02),
    EnumSensor(544, "DRM2 Code", {0: "Not Active", 1: "Max 50% Power Consumption"}, bitmask=0x04),
    EnumSensor(544, "DRM3 Code", {0: "Not Active", 1: "Max 75% Power Consumption, Source Reactive Power"}, bitmask=0x08),
    EnumSensor(544, "DRM4 Code", {0: "Not Active", 1: "Increase Power Consumption"}, bitmask=0x10),
    EnumSensor(544, "DRM5 Code", {0: "Not Active", 1: "No Power Generation"}, bitmask=0x20),
    EnumSensor(544, "DRM6 Code", {0: "Not Active", 1: "Max 50% Power Generation"}, bitmask=0x40),
    EnumSensor(544, "DRM7 Code", {0: "Not Active", 1: "Max 75% Power Generation, Sink Reactive Power"}, bitmask=0x80),
    EnumSensor(544, "DRM8 Code", {0: "Not Active", 1: "Increase Power Generation"}, bitmask=0x100)
)

SENSORS.deprecated.update(
    {
        "priority_mode": "priority_load",
        "Battery temperature": "Battery 1 temperature",
        "Battery voltage": "Battery 1 voltage",
        "Battery SOC": "Battery 1 SOC",
        "Battery power": "Battery 1 power",
        "Battery current": "Battery 1 current",
    }
)
