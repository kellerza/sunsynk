"""Filters."""
import logging
from statistics import mean
from typing import Any, List, Optional, Sequence, Union

import attr

_LOGGER = logging.getLogger(__name__)

# disable=no-member https://stackoverflow.com/questions/47972143/using-attr-with-pylint


@attr.define
class Filter:
    """Main filter class."""

    interval: int = attr.field(default=60)
    _i: int = attr.field(default=0)
    values: List[float] = attr.field(default=attr.Factory(list))
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

    def update(self, value: Union[float, int]) -> Optional[Union[float, int]]:
        """Add value."""
        if value is None:
            _LOGGER.warning(
                "%s: should not be None (%s)",
                getattr(self.sensor, "name", ""),
                self._filter.__name__,  # pylint: disable=no-member
            )
            return None
        self.values.append(value)  # pylint: disable=no-member
        if len(self.values) < self.samples:
            return None
        res = self._filter(self.values)  # pylint: disable=not-callable
        self.values.clear()  # pylint: disable=no-member
        _LOGGER.info(
            "%s: %s over %d samples = %s",
            getattr(self.sensor, "name", ""),
            self._filter.__name__,  # pylint: disable=no-member
            self.samples,
            res,
        )
        return res


@attr.define
class SCFilter(Filter):
    """Significant change filter."""

    threshold: int = attr.field(default=80)

    def update(self, value: Union[float, int]) -> Optional[Union[float, int]]:
        """Add value."""
        if self.values:
            if (
                value > self.values[0] + self.threshold
                or value < self.values[0] - self.threshold
            ):
                _LOGGER.info(
                    "%s: significant change %s -> %s (%d samples in buffer)",
                    getattr(self.sensor, "name", ""),
                    self.values[0],
                    value,
                    len(self.values),
                )
                self.values = [value]
                return value
        return super().update(value)


def getfilter(filter_def: str, sensor: Any) -> Filter:
    """Get a filter from a filterstring."""
    fff = filter_def.split(":")

    funcs = {"min": min, "max": max, "mean": mean}
    if fff[0] in funcs:
        res = Filter(interval=10, samples=6, filter=funcs[fff[0]], sensor=sensor)
        return res

    if fff[0] == "last":

        def last(val: Sequence[int]) -> int:
            return val[-1]

        res = Filter(interval=60, samples=1, filter=last, sensor=sensor)
        return res

    if fff:
        _LOGGER.warning("Unknown filter: %s", filter)

    return SCFilter(interval=1, samples=60, filter=mean, sensor=sensor)
