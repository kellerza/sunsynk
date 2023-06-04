"""Parse sensors from options."""
import logging
import traceback
from collections import defaultdict

import attrs
from helpers import import_mysensors
from options import OPT

from sunsynk.definitions import SENSORS as DEFS1
from sunsynk.definitions3ph import SENSORS as DEFS3
from sunsynk.helpers import slug
from sunsynk.rwsensors import RWSensor
from sunsynk.sensors import Sensor, SensorDefinitions

_LOGGER = logging.getLogger(__name__)


@attrs.define(slots=True)
class SensorOptions:
    """A list of sensors from the configuration."""

    # pylint: disable=too-few-public-methods

    sensors: dict[str, Sensor] = attrs.field(factory=dict)
    visible: dict[str, bool] = attrs.field(factory=dict)
    startup: dict[str, Sensor] = attrs.field(factory=dict)
    filter_str: dict[str, str] = attrs.field(factory=dict)
    defs: SensorDefinitions = attrs.field(factory=SensorDefinitions)
    deps: dict[Sensor, set[Sensor]] = attrs.field(factory=lambda: defaultdict(set))
    """A sensor name and al the sensors that might be affected on change."""

    def from_options(self) -> None:
        """Parse options and get the various sensor lists."""
        # pylint: disable=too-many-branches
        self.defs.all.clear()
        self.sensors.clear()
        self.visible.clear()
        self.startup.clear()
        self.filter_str.clear()

        # Load DEFS
        if OPT.sensor_definitions == "three-phase":
            _LOGGER.info("Using three phase sensor definitions.")
            self.defs.all = dict(DEFS3.all)
            self.defs.deprecated = DEFS3.deprecated
        else:
            _LOGGER.info("Using Single phase sensor definitions.")
            self.defs.all = dict(DEFS1.all)
            self.defs.deprecated = DEFS1.deprecated

        # Add custom sensors to DEFS
        try:
            mysensors = import_mysensors()
        except ImportError:
            _LOGGER.error("Unable to import import mysensors.py")
            traceback.print_exc()
        if mysensors:
            self.defs.all.update(mysensors)

        # Add startup sensors
        for sen in (self.defs.rated_power, self.defs.serial):
            self.startup[sen.id] = sen

        # Add other sensors
        for sensor_def in OPT.sensors:
            name, _, fstr = sensor_def.partition(":")
            name = slug(name)

            # Warn on deprecated
            if name in self.defs.deprecated:
                _LOGGER.error(
                    "Your config includes deprecated sensors. Replace %s with %s",
                    name,
                    self.defs.deprecated[name],
                )
                continue

            if name in self.sensors:
                _LOGGER.warning("Sensor %s only allowed once", name)
                continue

            sen = self.defs.all.get(name)
            if not isinstance(sen, Sensor):
                _LOGGER.error("Unknown sensor in config: %s", sensor_def)
                continue

            # if not fstr:
            #    fstr = suggested_filter(sen)

            self.filter_str[name] = fstr
            self.sensors[name] = sen
            self.visible[name] = True

        # Handle RW sensor deps
        for name in list(self.sensors):
            sen = self.sensors[name]
            if not isinstance(sen, RWSensor):
                continue
            for dep in sen.dependencies:
                self.deps[dep].add(sen)
                self.startup[dep.id] = dep
                if dep.id in self.sensors:
                    continue
                self.sensors[dep.id] = dep
                self.filter_str[dep.id] = suggested_filter(dep)

        if hidden := [i for i, v in self.visible.items() if not v]:
            _LOGGER.info(
                "Added hidden sensors as other sensors depend on it: %s",
                ", ".join(hidden),
            )


SOPT = SensorOptions()
"""All the options related to sensors."""
