"""Sunsynk hybrid inverter sensor definitions."""
from typing import Dict, Final

from sunsynk.sensor import (
    HSensor,
    RWSensor,
    Sensor,
    decode_fault,
    decode_serial,
    inv_state,
    offset100,
    sd_status,
    signed,
    timef,
)

CELSIUS: Final = "°C"
KWH: Final = "kWh"

device_type = Sensor(0, "Device Type")
serial = Sensor((3, 4, 5, 6, 7), "Serial", func=decode_serial)
overall_state = HSensor(59, "Overall state", func=inv_state)
day_active_power = HSensor(60, "Day Active Power", KWH, 0.1, func=signed)
day_reactive_power = HSensor(61, "Day Reactive Power", "kVarh", 0.1, func=signed)
total_active_power = HSensor((63, 64), "Total Active Power", KWH, 0.1)  # signed?
month_pv_power = HSensor(65, "Month PV Power", KWH, 1)
month_load_power = HSensor(66, "Month Load Power", KWH, 1)
month_grid_power = HSensor(67, "Month Grid Power", KWH, 1)
year_pv_power = HSensor((68, 69), "Year PV Power", KWH, 0.1)
day_battery_charge = HSensor(70, "Day Battery Charge", KWH, 0.1)
day_battery_discharge = HSensor(71, "Day Battery discharge", KWH, 0.1)
total_battery_charge = HSensor((72, 73), "Total Battery Charge", KWH, 0.1)
total_battery_discharge = HSensor((74, 75), "Total Battery Discharge", KWH, 0.1)
day_grid_import = HSensor(76, "Day Grid Import", KWH, 0.1)
day_grid_export = HSensor(77, "Day Grid Export", KWH, 0.1)
total_grid_import = HSensor((78, 80), "Total Grid Import", KWH, 0.1)
grid_frequency = HSensor(79, "Grid frequency", "Hz", 0.01)
total_grid_export = HSensor((81, 82), "Total Grid Export", KWH, 0.1)
day_load_power = HSensor(84, "Day Load Power", KWH, 0.1)
total_load_power = HSensor((85, 86), "Total Load Power", KWH, 0.1)
year_load_power = HSensor((87, 88), "Year Load Power", KWH, 0.1)
temp_dc_transformer = HSensor(90, "Temp DC transformer", CELSIUS, 0.1, func=offset100)
temp_radiator = HSensor(91, "Temp Radiator", CELSIUS, 0.1, func=offset100)
sd_status = Sensor(92, "SD Status", "", func=sd_status)  # type: ignore
temp_environment = HSensor(95, "Temp Environment", CELSIUS, 0.1, func=offset100)
total_pv_power = HSensor((96, 97), "Total PV Power", KWH, 0.1)
year_grid_export = HSensor((98, 99), "Year Grid Export", KWH, 0.1)
fault = Sensor((103, 104, 105, 106, 107), "Fault", func=decode_fault)
day_pv_energy = HSensor(108, "Day PV Energy", KWH, 0.1)
pv1_voltage = HSensor(109, "PV1 Voltage", "V", 0.1)
pv1_current = HSensor(110, "PV1 Current", "A", 0.1)
pv2_voltage = HSensor(111, "PV2 Voltage", "V", 0.1)
pv2_current = HSensor(112, "PV2 Current", "A", 0.1)
grid_voltage = HSensor(150, "Grid Voltage", "V", 0.1)
inverter_voltage = HSensor(154, "Inverter Voltage", "V", 0.1)
# Sunsynk 5Kw: 169,172 are the same
grid_load = HSensor(169, "Grid load", "W", 1, func=signed)  # L1(167) + L2(168)
grid_ct_load = HSensor(172, "Grid CT load", "W", 1, func=signed)
inverter_output = HSensor(175, "Inverter Output", "W", 1, func=signed)
load_power = HSensor(178, "Load Power", "W", 1, func=signed)  # L1(176) + L2(177)
temp_battery = HSensor(182, "Temp Battery", CELSIUS, 0.1, func=offset100)
battery_voltage = HSensor(183, "Battery voltage", "V", 0.01)
battery_soc = HSensor(184, "Battery SOC", "%", 1)
pv1_power = HSensor(186, "PV1 power", "W", 1, func=signed)
pv2_power = HSensor(187, "PV2 power", "W", 1, func=signed)
battery_power = HSensor(190, "Battery power", "W", 1, func=signed)
battery_current = HSensor(191, "Battery current", "A", 0.01, func=signed)
history_load_power = HSensor((201, 202), "History Load Power", "A", 0.01, func=signed)
battery_grid_charge = HSensor(230, "Battery Grid Charge", "A", 1, func=signed)
battery_charge = HSensor(312, "Battery charge", "V", 0.01)

bat1_soc = HSensor(603, "Bat1 SOC", "%", 1)
bat1_cycle = HSensor(611, "Bat1 Cycle")

prog1_time = RWSensor(250, "Prog1 Time", func=timef)
prog2_time = RWSensor(251, "Prog2 Time", func=timef)
prog3_time = RWSensor(252, "Prog3 Time", func=timef)
prog4_time = RWSensor(253, "Prog4 Time", func=timef)
prog5_time = RWSensor(254, "Prog5 Time", func=timef)
prog6_time = RWSensor(255, "Prog6 Time", func=timef)

prog1_power = RWSensor(256, "Prog1 Power", "W", 1)
prog2_power = RWSensor(257, "Prog2 Power", "W", 1)
prog3_power = RWSensor(258, "Prog3 Power", "W", 1)
prog4_power = RWSensor(259, "Prog4 Power", "W", 1)
prog5_power = RWSensor(260, "Prog5 Power", "W", 1)
prog6_power = RWSensor(261, "Prog6 Power", "W", 1)

prog1_voltage = RWSensor(262, "Prog1 Voltage", "V", 0.1)

prog1_capacity = RWSensor(268, "Prog1 Capacity", "%", 1)
prog2_capacity = RWSensor(269, "Prog2 Capacity", "%", 1)
prog3_capacity = RWSensor(270, "Prog3 Capacity", "%", 1)
prog4_capacity = RWSensor(271, "Prog4 Capacity", "%", 1)
prog5_capacity = RWSensor(272, "Prog5 Capacity", "%", 1)
prog6_capacity = RWSensor(273, "Prog6 Capacity", "%", 1)

# 1- Grid, 2- Gen
prog1_charge = RWSensor(274, "Prog1 Charge")
prog2_charge = RWSensor(275, "Prog2 Charge")
prog3_charge = RWSensor(276, "Prog3 Charge")
prog4_charge = RWSensor(277, "Prog4 Charge")
prog5_charge = RWSensor(278, "Prog5 Charge")
prog6_charge = RWSensor(279, "Prog6 Charge")


def all_sensors() -> Dict[str, Sensor]:
    """Get all defined sensors."""
    return {n: v for n, v in globals().items() if isinstance(v, Sensor)}
