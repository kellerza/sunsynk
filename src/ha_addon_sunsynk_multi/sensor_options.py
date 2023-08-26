"""Parse sensors from options."""
import logging
import traceback
from typing import Generator, Iterable

import attrs

from ha_addon_sunsynk_multi.helpers import import_mysensors
from ha_addon_sunsynk_multi.options import OPT
from ha_addon_sunsynk_multi.timer_schedule import SCHEDULES, Schedule, get_schedule
from sunsynk.definitions import SENSORS as DEFS1
from sunsynk.definitions3ph import SENSORS as DEFS3
from sunsynk.helpers import slug
from sunsynk.rwsensors import RWSensor
from sunsynk.sensors import Sensor, SensorDefinitions

_LOGGER = logging.getLogger(__name__)

DEFS = SensorDefinitions()
"""Sensor definitions (1ph / 3ph)."""


@attrs.define(slots=True)
class SensorOption:
    """Options for a sensor."""

    sensor: Sensor = attrs.field()
    schedule: Schedule = attrs.field()
    visible: bool = attrs.field(default=True)
    startup: bool = attrs.field(default=False)
    affects: set[Sensor] = attrs.field(factory=set)
    """Affect sensors due to dependencies."""
    first: bool = attrs.field(default=False)
    """Only on the first inverter."""

    def __hash__(self) -> int:
        """Hash the sensor id."""
        return self.sensor.__hash__()


@attrs.define(slots=True)
class SensorOptions(dict[Sensor, SensorOption]):
    """A dict of sensors from the configuration."""

    startup: set[Sensor] = attrs.field(factory=set)

    def init_sensors(self) -> None:
        """Parse options and get the various sensor lists."""
        if not DEFS.all:
            import_definitions()
        self.clear()

        # Add startup sensors
        self.startup = {DEFS.rated_power, DEFS.serial}
        self[DEFS.rated_power] = SensorOption(
            sensor=DEFS.rated_power, schedule=Schedule(), visible=False
        )
        self[DEFS.serial] = SensorOption(
            sensor=DEFS.serial, schedule=Schedule(), visible=False
        )

        # Add sensors from config
        for sen in get_sensors(target=self, names=OPT.sensors):
            if sen in self:
                continue
            self[sen] = SensorOption(
                sensor=sen,
                schedule=get_schedule(sen, SCHEDULES),
                visible=True,
            )

        # Add 1st inverter sensors
        for sen in get_sensors(target=self, names=OPT.sensors_first_inverter):
            if sen not in self:
                self[sen] = SensorOption(
                    sensor=sen,
                    schedule=get_schedule(sen, SCHEDULES),
                    visible=True,
                    first=True,
                )

        # Handle RW sensor deps
        for sopt in list(self.values()):
            if isinstance(sopt.sensor, RWSensor):
                for dep in sopt.sensor.dependencies:
                    self.startup.add(dep)
                    if dep not in self:
                        self[dep] = SensorOption(
                            sensor=dep,
                            schedule=get_schedule(dep, SCHEDULES),
                        )
                    self[dep].affects.add(sopt.sensor)

        # Info if we have hidden sensors
        if hidden := [s.sensor.name for s in self.values() if not s.visible]:
            _LOGGER.info(
                "Added hidden sensors as other sensors depend on it: %s",
                ", ".join(hidden),
            )


def import_definitions() -> None:
    """Load definitions according to options."""
    DEFS.all.clear()
    DEFS.deprecated.clear()

    # Load DEFS
    if OPT.sensor_definitions == "three-phase":
        _LOGGER.info("Using three phase sensor definitions.")
        DEFS.all = dict(DEFS3.all)
        DEFS.deprecated = DEFS3.deprecated
    else:
        _LOGGER.info("Using Single phase sensor definitions.")
        DEFS.all = dict(DEFS1.all)
        DEFS.deprecated = DEFS1.deprecated

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

SENSOR_GROUPS = {
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
        "battery_current",
        "battery_power",
        "battery_soc",
        "battery_voltage",
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
        "grid_power",
        "grid_voltage",
        "inverter_current",
        "inverter_power",
        "load_frequency",
        "non_essential_power",
        "overall_state",
        "priority_load",
        "pv1_current",
        "pv1_power",
        "pv1_voltage",
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
    ],
}


def get_sensors(
    *, target: Iterable[Sensor], names: list[str], warn_once: bool = True
) -> Generator[Sensor, None, None]:
    """Add a sensor."""
    for sensor_def in names:
        name, _, mod = sensor_def.partition(":")
        if mod:
            _LOGGER.warning("Modifiers was replaced by schedules: %s", sensor_def)

        name = slug(name)

        # Recursive add for groups
        if name in SENSOR_GROUPS:
            yield from get_sensors(
                target=target, names=SENSOR_GROUPS[name], warn_once=False
            )
            continue

        # Warn on deprecated
        if name in DEFS.deprecated:
            _LOGGER.error(
                "Your config includes deprecated sensors. Replace %s with %s",
                name,
                DEFS.deprecated[name],
            )
            continue

        if name in [t.name for t in target] and warn_once:
            _LOGGER.warning("Sensor %s only allowed once", name)
            continue

        sen = DEFS.all.get(name)
        if not isinstance(sen, Sensor):
            _LOGGER.error("Unknown sensor specified: %s", name)
            continue

        yield sen
