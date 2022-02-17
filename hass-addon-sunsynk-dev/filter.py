"""Filters."""
import logging
from statistics import mean
from typing import Any, List, Optional, Sequence, Union

import attr
from options import OPT

import sunsynk.definitions as ssdef

_LOGGER = logging.getLogger(__name__)

# disable=no-member https://stackoverflow.com/questions/47972143/using-attr-with-pylint


@attr.define
class Filter:
    """Main filter class."""

    interval: int = attr.field(default=60)
    _i: int = attr.field(default=0)
    values: List[Any] = attr.field(default=attr.Factory(list))
    samples: int = attr.field(default=1)
    _filter: Any = attr.field(default=mean)
    sensor: Any = attr.field(default=None)

    def should_update(self) -> bool:
        """Should we update this sensor."""
        if self._i < 1:
            self._i = self.interval - 1
            return True
        self._i -= 1
        return False

    @property
    def name(self) -> str:
        """Return the name of the sensor and filter."""
        nme = getattr(self.sensor, "name", str(self.sensor))
        if isinstance(self, SCFilter):
            nme += ":step"
        return f"{nme}:{self._filter.__name__}"  # pylint: disable=no-member

    def update(self, value: Union[float, int, str]) -> Optional[Union[float, int, str]]:
        """Add value."""
        if value is None:
            _LOGGER.warning("%s: should not be None", self.name)
            return None
        if isinstance(value, str) and self.values and value != str(self.values[-1]):
            # always significant change for strings!!
            self.values = [value]
            return value

        self.values.append(value)  # pylint: disable=no-member
        if len(self.values) < self.samples:
            return None
        try:
            value = self._filter(self.values)  # pylint: disable=not-callable
        except TypeError:
            pass

        self.values.clear()  # pylint: disable=no-member
        _LOGGER.debug(
            "%s over %d samples = %s",
            self.name,
            self.samples,
            value,
        )
        return value


@attr.define
class SCFilter(Filter):
    """Significant change filter."""

    threshold: int = attr.field(default=80)

    def update(self, value: Union[float, int, str]) -> Optional[Union[float, int, str]]:
        """Add value."""
        val0 = self.values[0] if self.values else 0
        if (
            isinstance(value, str)
            or isinstance(val0, str)
            or (not (value > val0 + self.threshold or value < val0 - self.threshold))
        ):
            return super().update(value)

        if OPT.debug >= 1:
            _LOGGER.info(
                "%s: significant change %s -> %s (%d samples in buffer)",
                self.name,
                val0,
                value,
                len(self.values),
            )
        self.values = [value]
        return value


def getfilter(filter_def: str, sensor: Any) -> Filter:
    """Get a filter from a filterstring."""
    fff = filter_def.split(":")

    funcs = {"min": min, "max": max, "mean": mean, "avg": mean}
    if fff[0] in funcs:
        res = Filter(interval=10, samples=6, filter=funcs[fff[0]], sensor=sensor)
        return res

    if fff[0] == "last":

        def last(val: Sequence[int]) -> int:
            return val[-1]

        res = Filter(interval=60, samples=1, filter=last, sensor=sensor)
        return res

    if fff[0] == "now":
        res = Filter(interval=2, samples=1, filter=max, sensor=sensor)
        return res

    if fff and fff[0] != "step":
        _LOGGER.warning("Unknown filter: %s", fff)

    thr = 80
    try:
        thr = int(fff[1])
    except IndexError:
        pass
    except ValueError as err:
        _LOGGER.error("Bad threshold: %s - %s", fff[1], err)

    return SCFilter(interval=1, samples=60, filter=mean, sensor=sensor, threshold=thr)


def suggested_filter(sensor: ssdef.Sensor) -> str:
    """Default filters."""
    if sensor.id.startswith("prog"):
        return "last"
    f_id = {
        ssdef.serial.id: "last",
        ssdef.overall_state.id: "step",
        ssdef.battery_soc.id: "last",
        ssdef.sd_status.id: "step",
        ssdef.fault.id: "last",
    }
    f_unit = {
        "A": "step",
        "V": "avg",
        "W": "step",
        ssdef.KWH: "last",
        ssdef.CELSIUS: "avg",
    }
    res = f_id.get(sensor.id) or f_unit.get(sensor.unit) or "step"
    _LOGGER.debug("%s unit:%s, id:%s", res, sensor.unit, sensor.id)
    return res
