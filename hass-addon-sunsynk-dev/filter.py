"""Filters."""
import logging
from statistics import mean
from typing import Any, List, Optional, Sequence, Union

import attr
from options import OPT

from sunsynk.definitions import ALL_SENSORS, AMPS, CELSIUS, KWH, VOLT, WATT, Sensor

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

    def update(self, value: Union[float, int, str]) -> Optional[Union[float, int, str]]:
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
    active: List[Sensor] = attr.field(factory=list)
    list: List[Sensor] = attr.field(factory=list)
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
        return self.sensor in RROBIN.active

    def update(self, value: Union[float, int, str]) -> Optional[Union[float, int, str]]:
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
        RROBIN.list.append(self.sensor)


def getfilter(filter_def: str, sensor: Sensor) -> Filter:
    """Get a filter from a filterstring."""
    fff = filter_def.split(":")

    if fff[0] == "round_robin":
        return RoundRobinFilter(sensor=sensor)

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


def suggested_filter(sensor: Sensor) -> str:
    """Default filters."""
    if sensor.id.startswith("prog"):
        return "round_robin"
    f_id = {
        "battery_soc": "last",
        "fault": "round_robin",
        "grid_connected_status": "last",
        "overall_state": "step",
        "priority_mode": "round_robin",
        "sd_status": "step",
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
