"""Filters."""
import logging
from statistics import mean
from typing import Any, Callable, List, Optional, Union

import attr

_LOGGER = logging.getLogger(__name__)


@attr.define
class Filter:
    """Main filter class."""

    interval: int = attr.field(default=60)
    _i: int = attr.field(default=1)
    values: List = attr.field(default=attr.Factory(list))
    samples: int
    _filter: Callable
    sensor: Any

    def should_update(self) -> bool:
        """Should we update this sensor."""
        if self._i < 1:
            self._i = self.interval
            return True
        self._i -= 1
        return False

    def update(self, value: Union[float, int]) -> Optional[Union[float, int]]:
        """Add value."""
        self.values.append(value)
        if len(self.values) < self.samples:
            return None
        res = self._filter(self.values)
        self.values.clear()
        _LOGGER.debug(
            "%s over %d samples = %s", self._filter.__name__, self.samples, res
        )
        return res


class SCFilter(Filter):
    """Significant change filter."""

    threshold: int

    def update(self, value: Union[float, int]) -> None:
        """Add value."""
        if self.values:
            if (
                value > self.values[0] + self.threshold
                or value < self.values[0] - self.threshold
            ):
                _LOGGER.debug(
                    "Significant change %s -> %s (%d samples in buffer)",
                    self.values[0],
                    value,
                    len(self.values),
                )
                self.values = [value]
                return value
        return super().update(value)


def getfilter(filter, sensor: Any) -> Filter:
    """Get a filter from a filterstring."""
    fff = filter.split(":")

    funcs = {"min": min, "max": max, "mean": mean}
    if fff[0] in funcs:
        res = Filter(interval=10, samples=6, filter=funcs[fff[0]], sensor=sensor)
        return res

    if fff[0] == "last":

        def last(val):
            return val[-1]

        res = Filter(interval=60, samples=1, filter=last, sensor=sensor)
        return res

    if fff:
        _LOGGER.warning("Unknown filter: %s", filter)

    return SCFilter(interval=1, samples=60, filter=mean, sensor=sensor)
