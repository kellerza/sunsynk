"""Filters."""
import logging
from statistics import mean
from typing import Any, List, Sequence

import attr
from options import OPT

from sunsynk.definitions import ALL_SENSORS, AMPS, CELSIUS, KWH, VOLT, WATT, Sensor
from sunsynk.helpers import ValType
from sunsynk.rwsensors import RWSensor

_LOGGER = logging.getLogger(__name__)

# disable=no-member https://stackoverflow.com/questions/47972143/using-attr-with-pylint


@attr.define
class Filter:
    """Main filter class."""

    interval: int = attr.field(default=60)
    _i: int = attr.field(default=0)
    values: List[Any] = attr.field(default=None)
    samples: int = attr.field(default=1)
    _filter: Any = attr.field(default=mean)
    # sensor: Any = attr.field(default=None)
    sensor_name: str = attr.field(default="")

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
        nme = self.sensor_name
        if isinstance(self, SCFilter):
            nme += ":step"
        return f"{nme}:{self._filter.__name__}"  # pylint: disable=no-member

    def update(self, value: ValType) -> ValType:
        """Add value."""
        if value is None:
            _LOGGER.warning("%s: should not be None", self.name)
            return None
        if isinstance(value, str) and self.values and value != str(self.values[-1]):
            # always significant change for strings!!
            self.values = [value]
            return value

        if self.values is None:  # quick initial start
            self.values = []
            return value

        self.values.append(value)  # pylint: disable=no-member
        if len(self.values) < self.samples:
            return None
        try:
            value = round(self._filter(self.values), 1)  # pylint: disable=not-callable
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

    threshold: int = attr.field(default=50)

    def update(self, value: ValType) -> ValType:
        """Add value."""
        val0 = self.values[0] if self.values else 0
        try:
            if value > val0 + self.threshold or value < val0 - self.threshold:
                if OPT.debug >= 1:
                    msg = f"{self.name}: {val0}->{value}, {len(self.values)} samples"
                    _LOGGER.info(msg)
                self.values = [value]
                return value
        except TypeError:
            pass

        res = super().update(value)
        if res and not self.values:
            self.values = [res]
        return res


@attr.define(slots=True)
class RRobinState:
    """Round Robin settings."""

    # pylint: disable=too-few-public-methods
    active: List[Filter] = attr.field(factory=list)
    list: List[Filter] = attr.field(factory=list)
    idx: int = attr.field(default=-1)

    def tick(self) -> None:
        """Cycle over entries in the RR list."""
        if not self.list:
            return
        self.idx += 1
        try:
            self.active = [self.list[self.idx]]
        except IndexError:
            self.idx = 0
            self.active = [self.list[0]]


RROBIN = RRobinState()


@attr.define
class RoundRobinFilter(Filter):
    """Round Robin Filter."""

    def should_update(self) -> bool:
        """Should we update this sensor."""
        return self in RROBIN.active

    def update(self, value: ValType) -> ValType:
        """Add value."""
        if self.values:
            val0 = self.values[0]

            if val0 == value:
                self.samples += 1
                if self.samples > 100:
                    self.samples = 0
                else:
                    return None
                self.samples = 0

        self.values = [value]
        return value

    def __attrs_post_init__(self) -> None:
        """Init."""
        RROBIN.list.append(self)


def getfilter(filter_def: str, sensor: Sensor) -> Filter:
    """Get a filter from a filterstring."""
    fff = filter_def.split(":")

    sensor_name = "" if sensor is None else sensor.name

    if fff[0] == "round_robin":
        return RoundRobinFilter(sensor_name=sensor_name)

    funcs = {"min": min, "max": max, "mean": mean, "avg": mean}
    if fff[0] in funcs:
        res = Filter(
            interval=10, samples=6, filter=funcs[fff[0]], sensor_name=sensor_name
        )
        return res

    if fff[0] == "last":

        def last(val: Sequence[int]) -> int:
            return val[-1]

        res = Filter(interval=60, samples=1, filter=last, sensor_name=sensor_name)
        return res

    if fff[0] == "now":
        res = Filter(interval=2, samples=1, filter=max, sensor_name=sensor_name)
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

    return SCFilter(
        interval=1, samples=60, filter=mean, sensor_name=sensor_name, threshold=thr
    )


def suggested_filter(sensor: Sensor) -> str:
    """Default filters."""
    if isinstance(sensor, RWSensor):
        return "round_robin"
    f_id = {
        "battery_soc": "last",
        "fault": "last",
        "grid_connected_status": "last",
        "overall_state": "last",
        "sd_status": "last",
        "serial": "round_robin",
    }
    assert all(s in ALL_SENSORS for s in f_id)

    f_unit = {
        AMPS: "step",
        VOLT: "avg",
        WATT: "step",
        KWH: "last",
        CELSIUS: "avg",
    }
    res = f_id.get(sensor.id) or f_unit.get(sensor.unit) or "step"
    _LOGGER.debug("%s unit:%s, id:%s", res, sensor.unit, sensor.id)
    return res
