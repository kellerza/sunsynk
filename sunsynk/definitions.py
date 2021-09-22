"""Sunsynk hybrid inverter sensor definitions."""
from typing import Dict, Final

from sunsynk.sensor import HSensor, Sensor, negative, offset100, sd_status

CELSIUS: Final = "°C"
KWH: Final = "kWh"

serial = Sensor((3, 4, 5, 6, 7), "Serial")
overall_state = HSensor(59, "Overall state")
day_active_power = HSensor(60, "Day Active Power", KWH, 0.1)
day_reactive_power = HSensor(61, "Day Reactive Power", "kVarh", 0.1)
total_active_power = HSensor((63, 64), "Total Active Power", KWH, 0.1)
day_battery_charge = HSensor(70, "Day Battery Charge", KWH, 0.1)
day_battery_discharge = HSensor(71, "Day Battery discharge", KWH, 0.1)
total_battery_charge = HSensor((72, 73), "Total Battery Charge", KWH, 0.1)
total_battery_discharge = HSensor((74, 75), "Total Battery Discharge", KWH, 0.1)
day_grid_import = HSensor(76, "Day Grid Import", KWH, 0.1)
day_grid_export = HSensor(77, "Day Grid Export", KWH, 0.1)
total_grid_import = HSensor((78, 80), "Total Grid Import", KWH, 0.1)
grid_frequency = HSensor(79, "Grid frequency", "Hz", 0.01)
total_grid_export = HSensor((81, 82), "Total Grid Export", KWH, 0.1)
total_load_power = HSensor((85, 86), "Total Load Power", KWH, 0.1)
year_load_power = HSensor((87, 88), "Year Load Power", KWH, 0.1)
temp_dc_transformer = HSensor(90, "Temp DC transformer", CELSIUS, 0.1, func=offset100)
temp_radiator = HSensor(91, "Temp Radiator", CELSIUS, 0.1, func=offset100)
sd_status = Sensor(92, "SD Status", "", func=sd_status)  # type: ignore
temp_environment = HSensor(95, "Temp Environment", CELSIUS, 0.1, func=offset100)
total_pv_power = HSensor((96, 97), "Total PV Power", KWH, 0.1)
year_grid_export = HSensor((98, 99), "Year Grid Export", KWH, 0.1)
day_pv_energy = HSensor(108, "Day PV Energy", KWH, 0.1)
pv1_voltage = HSensor(109, "PV1 Voltage", "V", 0.1)
pv1_current = HSensor(110, "PV1 Current", "A", 0.1)
pv2_voltage = HSensor(111, "PV2 Voltage", "V", 0.1)
pv2_current = HSensor(112, "PV2 Current", "A", 0.1)
inverter_voltage = HSensor(154, "Inverter Voltage", "V", 0.1)
grid_inverter_load = HSensor(167, "Grid Inverter load", "W", 1, func=negative)
grid_ct_load = HSensor(172, "Grid CT load", "W", 1, func=negative)
total_load = HSensor(178, "Total load", "W", 1, func=negative)
temp_battery = HSensor(182, "Temp Battery", CELSIUS, 0.1, func=offset100)
battery_voltage = HSensor(183, "Battery voltage", "V", 0.01)
battery_soc = HSensor(184, "Battery SOC", "%", 1)
pv1_power = HSensor(186, "PV1 power", "W", 1, func=negative)
pv2_power = HSensor(187, "PV2 power", "W", 1, func=negative)
battery_output_power = HSensor(190, "Battery output power", "W", 1, func=negative)
battery_output_current = HSensor(191, "Battery output current", "A", 0.1, func=negative)
battery_grid_charge = HSensor(230, "Battery Grid Charge", "A", 1, func=negative)
battery_charge = HSensor(312, "Battery charge", "V", 0.01)


def all_sensors() -> Dict[str, Sensor]:
    """Get all defined sensors."""
    return {n: v for n, v in globals().items() if isinstance(v, Sensor)}
