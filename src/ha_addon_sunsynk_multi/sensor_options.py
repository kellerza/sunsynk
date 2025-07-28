"""Parse sensors from options."""

import logging
import traceback
from collections.abc import Generator, Iterable

import attrs

from sunsynk.definitions import import_defs
from sunsynk.helpers import slug
from sunsynk.rwsensors import RWSensor
from sunsynk.sensors import Sensor, SensorDefinitions

from .helpers import import_mysensors
from .options import OPT
from .timer_schedule import SCHEDULES, Schedule, get_schedule

_LOGGER = logging.getLogger(__name__)

DEFS = SensorDefinitions()
"""Sensor definitions (1ph / 3ph)."""


@attrs.define(slots=True)
class SensorOption:
    """Options for a sensor."""

    sensor: Sensor
    schedule: Schedule
    visible: bool = False
    affects: set[Sensor] = attrs.field(factory=set)
    """Affect sensors due to dependencies."""
    first: bool = False
    """Only on the first inverter."""

    def __hash__(self) -> int:
        """Hash the sensor id."""
        return self.sensor.__hash__()


@attrs.define(slots=True)
class SensorOptions(dict[Sensor, SensorOption]):
    """A dict of sensors from the configuration."""

    startup: list[Sensor] = attrs.field(factory=list)
    _deps: set[Sensor] = attrs.field(factory=set)

    def _add_sensor(
        self,
        sensor: Sensor,
        *,
        visible: bool = False,
        first: bool = False,
    ) -> None:
        """Add a sensor. Keep dependencies for later."""
        if sensor in self:
            return
        self[sensor] = SensorOption(
            sensor=sensor,
            schedule=get_schedule(sensor, SCHEDULES),
            visible=visible,
            first=first,
        )
        if isinstance(sensor, RWSensor):
            self._deps.update(sensor.dependencies)

    def init_sensors(self) -> None:
        """Parse options and get the various sensor lists."""
        if not DEFS.all:
            import_definitions()
        self.clear()

        self.startup = [DEFS.device_type, DEFS.protocol, DEFS.serial]
        sensors_all = list(get_sensors(target=self, names=OPT.sensors))
        sensors_1st = list(get_sensors(target=self, names=OPT.sensors_first_inverter))

        # 1. Add startup sensors to all inverters. Visible if configured anywhere.
        for sen in self.startup:
            visible = sen in sensors_1st or sen in sensors_all
            self._add_sensor(sen, visible=visible)

        # 2. Add sensors configured for all inverters
        for sen in sensors_all:
            self._add_sensor(sen, visible=True)

        # 3. Add deps, usually hidden, but visible if configured on 1st inverter
        while self._deps:
            sen = self._deps.pop()
            self._add_sensor(sen, visible=sen in sensors_1st)

        # 4. Add sensors configured for the 1st inverter
        for sen in sensors_1st:
            if sen not in self:
                self._add_sensor(sen, visible=True, first=True)

        # 5. Add deps for the 1st inverter, always hidden
        while self._deps:
            sen = self._deps.pop()
            self._add_sensor(sen, first=True)

        # Display hidden sensors
        if hidden := [s.sensor.name for s in self.values() if not s.visible]:
            _LOGGER.info(
                "Added hidden sensors as other sensors depend on it: %s",
                ", ".join(hidden),
            )

        # Add Affects
        for sen in self:
            if isinstance(sen, RWSensor):
                for dep in sen.dependencies:
                    self[dep].affects.add(sen)


def import_definitions() -> None:
    """Load definitions according to options."""
    defs = import_defs(OPT.sensor_definitions)
    DEFS.all = defs.all
    DEFS.deprecated = defs.deprecated

    # Add custom sensors to DEFS
    try:
        mysensors = import_mysensors()
        if mysensors:
            DEFS.all.update(mysensors)
            SENSOR_GROUPS["mysensors"] = list(mysensors)
    except ImportError:
        _LOGGER.error("Unable to import import mysensors.py")
        traceback.print_exc()


SOPT = SensorOptions()
"""A dict of all options related to sensors."""

SENSOR_GROUPS: dict[str, list[str]] = {
    # https://kellerza.github.io/sunsynk/guide/energy-management
    "energy_management": [
        "total_battery_charge",
        "total_battery_discharge",
        "total_grid_export",
        "total_grid_import",
        "total_pv_energy",
    ],
    # https://kellerza.github.io/sunsynk/examples/lovelace#sunsynk-power-flow-card
    "power_flow_card": [
        "aux_power",
        "battery_1_soc",  # 3PH HV
        "battery_1_voltage",  # 3PH HV
        "battery_current",
        "battery_power",
        "battery_soc",  # 1PH & 3PH LV
        "battery_voltage",  # 1PH & 3PH LV
        "day_battery_charge",
        "day_battery_discharge",
        "day_grid_export",
        "day_grid_import",
        "day_load_energy",
        "day_pv_energy",
        "essential_power",
        "grid_connected",
        "grid_ct_power",
        "grid_frequency",
        "grid_l1_power",  # 3PH LV & HV
        "grid_l2_power",  # 3PH LV & HV
        "grid_l3_power",  # 3PH LV & HV
        "grid_power",
        "grid_voltage",
        "grid_current",
        "inverter_current",
        "inverter_power",
        "inverter_voltage",
        "load_frequency",
        "load_power",
        "load_l1_power",
        "load_l2_power",
        "load_l3_power",
        "load_l1_voltage",
        "load_l2_voltage",
        "load_l3_voltage",
        "non_essential_power",
        "overall_state",
        "priority_load",
        "pv_power",
        "pv1_current",
        "pv1_power",
        "pv1_voltage",
        "pv2_current",
        "pv2_power",
        "pv2_voltage",
        "pv3_current",
        "pv3_power",
        "pv3_voltage",
        "pv4_current",
        "pv4_power",
        "pv4_voltage",
        "use_timer",
    ],
    "settings": [
        "export_limit_power",
        "grid_charge_enabled",
        "load_limit",
        "prog1_capacity",
        "prog1_charge",
        "prog1_power",
        "prog1_time",
        "prog2_capacity",
        "prog2_charge",
        "prog2_power",
        "prog2_time",
        "prog3_capacity",
        "prog3_charge",
        "prog3_power",
        "prog3_time",
        "prog4_capacity",
        "prog4_charge",
        "prog4_power",
        "prog4_time",
        "prog5_capacity",
        "prog5_charge",
        "prog5_power",
        "prog5_time",
        "prog6_capacity",
        "prog6_charge",
        "prog6_power",
        "prog6_time",
        "solar_export",
        "use_timer",
    ],
    "advanced": [
        "battery_capacity_current",
        "battery_charge_efficiency",
        "battery_low_capacity",
        "battery_max_charge_current",
        "battery_max_discharge_current",
        "battery_resistance",
        "battery_restart_capacity",
        "battery_shutdown_capacity",
        "battery_type",
        "battery_wake_up",
        "configured_grid_frequency",
        "configured_grid_phases",
        "date_time",
        "grid_charge_battery_current",
        "grid_charge_start_battery_soc",
        "grid_standard",
        "track_grid_phase",
        "ups_delay_time",
    ],
    "generator": [
        "gen_signal_on",
        "generator_charge_battery_current",
        "generator_charge_enabled",
        "generator_charge_start_battery_soc",
        "generator_cooling_time",
        "generator_max_operating_time",
        "generator_off_soc",
        "generator_on_soc",
        "generator_port_usage",
        "min_pv_power_for_gen_start",
    ],
    "diagnostics": [
        "battery_bms_alarm_flag",
        "battery_bms_fault_flag",
        "battery_bms_soh",
        "battery_current",
        "battery_power",
        "battery_soc",
        "battery_temperature",
        "battery_voltage",
        "dc_transformer_temperature",
        "fan_warning",
        "fault",
        "grid_l1_voltage",
        "grid_l2_voltage",
        "grid_l3_voltage",
        "grid_phase_warning",
        "grid_relay_status",
        "grid_voltage",
        "inverter_l1_power",
        "inverter_l2_power",
        "inverter_l3_power",
        "inverter_relay_status",
        "lithium_battery_loss_warning",
        "parallel_communication_quality_warning",
        "radiator_temperature",
    ],
    "battery": [
        "battery_absorption_voltage",
        "battery_capacity_current",
        "battery_charge_efficiency",
        "battery_equalization_days",
        "battery_equalization_hours",
        "battery_equalization_voltage",
        "battery_float_voltage",
        "battery_low_capacity",
        "battery_low_voltage",
        "battery_max_charge_current",
        "battery_max_discharge_current",
        "battery_resistance",
        "battery_restart_capacity",
        "battery_restart_voltage",
        "battery_shutdown_capacity",
        "battery_shutdown_voltage",
        "battery_type",
        "battery_wake_up",
    ],
    "parallel": [
        "parallel_bat1_bat2",
        "parallel_mode",
        "parallel_phase",
        "parallel_modbus_sn",
    ],
}


def get_sensors(
    *, target: Iterable[Sensor], names: list[str], warn: bool = True
) -> Generator[Sensor, None, None]:
    """Add a sensor."""
    groups: set[str] = set()

    for sensor_def in names:
        if ":" in sensor_def:
            _LOGGER.error("Modifiers was replaced by schedules: %s", sensor_def)
            continue

        name = slug(sensor_def)

        # Recursive add for groups
        if name in SENSOR_GROUPS or name == "all":
            groups.add(name)
            continue

        # Warn on deprecated
        if name in DEFS.deprecated:
            if warn:
                _LOGGER.error(
                    "Your config includes deprecated sensors. Replace %s with %s",
                    name,
                    DEFS.deprecated[name],
                )
            continue

        if name in [t.name for t in target] and warn:
            _LOGGER.warning("Sensor %s only allowed once", name)
            continue

        sen = DEFS.all.get(name)
        if not isinstance(sen, Sensor):
            if warn:
                _LOGGER.error("Unknown sensor specified: %s", name)
            continue

        yield sen

    # Add groups at the end
    for name in groups:
        names = list(DEFS.all) if name == "all" else SENSOR_GROUPS[name]
        yield from get_sensors(target=target, names=names, warn=False)
