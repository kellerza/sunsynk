"""Parse sensors from options."""

import logging
import traceback
from typing import Generator, Iterable

import attrs

from ha_addon_sunsynk_multi.helpers import import_mysensors
from ha_addon_sunsynk_multi.options import OPT
from ha_addon_sunsynk_multi.timer_schedule import SCHEDULES, Schedule, get_schedule
from sunsynk.definitions.single_phase import SENSORS as SENSORS_1PH
from sunsynk.definitions.three_phase_hv import SENSORS as SENSORS_3PHV
from sunsynk.definitions.three_phase_lv import SENSORS as SENSORS_3PHLV
from sunsynk.helpers import slug
from sunsynk.rwsensors import RWSensor
from sunsynk.sensors import Sensor, SensorDefinitions

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
    DEFS.all.clear()
    DEFS.deprecated.clear()

    # Load DEFS
    if OPT.sensor_definitions == "three-phase":
        _LOGGER.info("Using three phase sensor definitions.")
        DEFS.all = dict(SENSORS_3PHLV.all)
        DEFS.deprecated = SENSORS_3PHLV.deprecated
    elif OPT.sensor_definitions == "three-phase-hv":
        _LOGGER.info("Using three phase HV sensor definitions.")
        DEFS.all = dict(SENSORS_3PHV.all)
        DEFS.deprecated = SENSORS_3PHV.deprecated
    else:
        _LOGGER.info("Using Single phase sensor definitions.")
        DEFS.all = dict(SENSORS_1PH.all)
        DEFS.deprecated = SENSORS_1PH.deprecated

    # Add custom sensors to DEFS
    try:
        mysensors = import_mysensors()
    except ImportError:
        _LOGGER.error("Unable to import import mysensors.py")
        traceback.print_exc()
    if mysensors:
        DEFS.all.update(mysensors)
        SENSOR_GROUPS["mysensors"] = list(mysensors)


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
        "inverter_current",
        "inverter_power",
        "load_frequency",
        "load_power",
        "load_l1_power",
        "load_l2_power",
        "load_l3_power",
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
        "use_timer",
    ],
    "settings": [
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
        "date_time",
        "grid_charge_battery_current",
        "grid_charge_start_battery_soc",
        "grid_charge_enabled",
        "use_timer",
        "solar_export",
        "export_limit_power",
        "battery_max_charge_current",
        "battery_max_discharge_current",
        "battery_capacity_current",
        "battery_shutdown_capacity",
        "battery_restart_capacity",
        "battery_low_capacity",
        "battery_type",
        "battery_wake_up",
        "battery_resistance",
        "battery_charge_efficiency",
        "grid_standard",
        "configured_grid_frequency",
        "configured_grid_phases",
        "ups_delay_time",
    ],
    "generator": [
        "generator_port_usage",
        "generator_off_soc",
        "generator_on_soc",
        "generator_max_operating_time",
        "generator_cooling_time",
        "min_pv_power_for_gen_start",
        "generator_charge_enabled",
        "generator_charge_start_battery_soc",
        "generator_charge_battery_current",
        "gen_signal_on",
    ],
    "diagnostics": [
        "grid_voltage",
        "grid_l1_voltage",
        "grid_l2_voltage",
        "grid_l3_voltage",
        "battery_temperature",
        "battery_voltage",
        "battery_soc",
        "battery_power",
        "battery_current",
        "fault",
        "dc_transformer_temperature",
        "radiator_temperature",
        "grid_relay_status",
        "inverter_relay_status",
        "battery_bms_alarm_flag",
        "battery_bms_fault_flag",
        "battery_bms_soh",
        "fan_warning",
        "grid_phase_warning",
        "lithium_battery_loss_warning",
        "parallel_communication_quality_warning",
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
