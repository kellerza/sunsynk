"""Sunsynk/Deye hybrid 3-phase high voltage (HV) inverter sensor definitions."""
from sunsynk import AMPS, CELSIUS, VOLT, WATT
from sunsynk.definitions.three_phase_common import SENSORS
from sunsynk.rwsensors import (
    NumberRWSensor,
    SelectRWSensor,
    SwitchRWSensor,
)
from sunsynk.sensors import (
    BinarySensor,
    EnumSensor,
    HVFaultSensor,
    MathSensor,
    SDStatusSensor,
    Sensor,
    SerialSensor,
    TempSensor,
)

SENSORS = SENSORS.copy()

##########
# Battery
##########
SENSORS += (
    TempSensor(586, "Battery 1 temperature", CELSIUS, 0.1),
    Sensor(587, "Battery 1 voltage", VOLT, 0.1),
    Sensor(588, "Battery 1 SOC", "%"),
    Sensor(590, "Battery 1 power", WATT, -10),
    Sensor(591, "Battery 1 current", AMPS, -0.01),
    Sensor(589, "Battery 2 SOC", "%"),
    Sensor(593, "Battery 2 voltage", VOLT, 0.1),
    Sensor(594, "Battery 2 current", AMPS, -0.01),
    Sensor(595, "Battery 2 power", WATT, -10),
    TempSensor(596, "Battery 2 temperature", CELSIUS, 0.1),
)

#############
# Grid Power
#############
SENSORS += (
    Sensor(604, "A Phase Power on the Inner Side of the Grid", "W"),
    Sensor(605, "B Phase Power on the Inner Side of the Grid", "W"),
    Sensor(606, "C Phase Power on the Inner Side of the Grid", "W"),
    Sensor(607, "Total Active Power from Side to Side of the Grid", "W"),
    Sensor(608, "Grid Side - Inside Total Apparent Power", "W"),
)

##############
# Solar Power
##############
SENSORS += (
    MathSensor(
        (672, 673, 674, 675), "PV power", WATT, factors=(10, 10, 10, 10)
    ),  # pv1,pv2,pv3,pv4 power
)

################
# MPPT 1-4 Solar Power
################
SENSORS += (
    Sensor(672, "PV1 power", WATT, 10),
    Sensor(673, "PV2 power", WATT, 10),
    Sensor(674, "PV3 power", WATT, 10),
    Sensor(675, "PV4 power", WATT, 10),
)


###################
# Power on Outputs (aka GEN - which has multiple modes on the deye 3 Phase )
###################
SENSORS += (
    Sensor(661, "Gen L1 volts", VOLT, 0.1),
    Sensor(662, "Gen L2 volts", VOLT, 0.1),
    Sensor(663, "Gen L3 volts", VOLT, 0.1),
)


##########
# General
##########
RATED_POWER = Sensor((20, 21), "Rated power", WATT, 0.1)

SENSORS += (
    HVFaultSensor((555, 556, 557, 558), "Fault"),
    EnumSensor(
        553, "Fan Warning", options={0: "No Warning", 1 << 1: "Warning"}, bitmask=1 << 1
    ),
    EnumSensor(
        553,
        "Grid Phase Warning",
        options={0: "No Warning", 1 << 2: "Warning"},
        bitmask=1 << 2,
    ),
    EnumSensor(
        554,
        "Lithium Battery Loss Warning",
        options={0: "No Warning", 1 << 14: "Warning"},
        bitmask=1 << 14,
    ),
    EnumSensor(
        554,
        "Parallel Communication Quality Warning",
        options={0: "No Warning", 1 << 15: "Warning"},
        bitmask=1 << 15,
    ),
    SDStatusSensor(0, "SD Status", ""),  # type: ignore
    SerialSensor((3, 4, 5, 6, 7), "Serial"),
    BinarySensor(552, "Grid Connected", bitmask=1 << 2),
)

###########
# Settings
###########
SENSORS += (
    NumberRWSensor(143, "Export Limit power", WATT, 10, max=RATED_POWER),
    NumberRWSensor(191, "Grid Peak Shaving power", WATT, 10, max=100000),
    NumberRWSensor(340, "Max Solar power", WATT, 10, max=65000),
)

# Additional optional sensors
SENSORS += (
    NumberRWSensor(104, "System Zero Export power", WATT, -10, min=-500, max=500),
    NumberRWSensor(124, "Generator Charge Start Battery SOC", "%"),
    NumberRWSensor(125, "Generator Charge Battery current", AMPS),
    SwitchRWSensor(110, "Parallel Battery 1 and 2"),
    SelectRWSensor(
        112,
        "Battery 1 Wake Up",
        options={0: "Enabled", 1 << 0: "Disabled"},
        bitmask=1 << 0,
    ),  # according to docs, 0 is enabled for this one
    SelectRWSensor(
        112,
        "Battery 2 Wake Up",
        options={0: "Enabled", 1 << 8: "Disabled"},
        bitmask=1 << 8,
    ),  # according to docs, 0 is enabled for this one
    Sensor(114, "Battery Charge Efficiency", "%", 0.1),
)


SENSORS += SelectRWSensor(
    111,
    "Battery Type",
    options={0: "Use Battery Voltage", 1: "Lithium (Use BMS)", 2: "No Battery"},
)


#################
# System program
#################
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
    NumberRWSensor(154, "Prog1 power", WATT, 10, max=RATED_POWER),
    NumberRWSensor(155, "Prog2 power", WATT, 10, max=RATED_POWER),
    NumberRWSensor(156, "Prog3 power", WATT, 10, max=RATED_POWER),
    NumberRWSensor(157, "Prog4 power", WATT, 10, max=RATED_POWER),
    NumberRWSensor(158, "Prog5 power", WATT, 10, max=RATED_POWER),
    NumberRWSensor(159, "Prog6 power", WATT, 10, max=RATED_POWER),
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
# Advanced Battery Configuration Settings/Info
#################
hv_battery_manufacturers = {
    0: "No HV battery",
    1: "PYLON_HV",
    2: "DynessHV_HV",
    3: "UZENERGY_HV",
    4: "SOLAX_HV",
    5: "Deye_HV",
    6: "BYD_HV",
    7: "JINKOBSS_HV",
}
SENSORS += (
    SelectRWSensor(
        223,
        "Lithium HV BMS Protocol",
        options={
            0: "PYLON SOLAX (CAN)",
            # according to supported battery documents, this is also set to 1 for BYD CAN
            1: "Tianbanda RS485 Modbus Protocol (BYD CAN)",
            2: "KOK Protocol",
            3: "Keith",
            4: "Topai Protocol",
            5: "Pai Energy 485 Protocol",
            6: "Jelis 485 Protocol",
            7: "Xinwangda 485 Protocol",
            8: "Xinruineng 485 Protocol",
            9: "Tianbanda 485 Protocol",
            10: "Shenggao Electrical CAN Protocol",
        },
    ),
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
    SwitchRWSensor(
        222,
        "Battery 1 BMS other flag - Battery 1 Force charge",
        on=1 << 1,
        bitmask=1 << 1,
    ),
    SwitchRWSensor(
        222,
        "Battery 1 BMS other flag - Battery 2 Force charge",
        on=1 << 2,
        bitmask=1 << 2,
    ),
    SwitchRWSensor(
        222,
        "Battery 1 BMS other flag - Battery 1 Sleep",
        on=1 << 3,
        bitmask=1 << 3,
    ),
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
    SwitchRWSensor(
        253,
        "Battery 2 BMS other flag - Battery 1 Force charge",
        on=1 << 1,
        bitmask=1 << 1,
    ),
    SwitchRWSensor(
        253,
        "Battery 2 BMS other flag - Battery 2 Force charge",
        on=1 << 2,
        bitmask=1 << 2,
    ),
    SwitchRWSensor(
        253,
        "Battery 2 BMS other flag - Battery 1 Sleep",
        on=1 << 3,
        bitmask=1 << 3,
    ),
    Sensor(254, "Battery 2 BMS type", ""),
    Sensor(255, "Battery 2 BMS SOH", "%"),
    Sensor(256, "Battery 2 BMS software version", ""),
    Sensor(257, "Battery 2 BMS rated AH", "Ah"),
    Sensor(258, "Battery 2 BMS hardware version", ""),
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
        "battery_temperature": "battery_1_temperature",
        "battery voltage": "battery_1_voltage",
        "battery_soc": "battery_1_soc",
        "battery_power": "battery_1_power",
        "battery_current": "battery_1_current",
    }
)
