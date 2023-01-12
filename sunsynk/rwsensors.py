"""Sensor classes represent modbus registers for an inverter."""
from __future__ import annotations

import logging
from math import modf
from typing import Any, Callable, Dict, Generator, List, Sequence, Tuple, Union

import attr

_LOGGER = logging.getLogger(__name__)


class RWSensor(Sensor):
    """Read & write sensor."""

    def update_reg_value(self, value: Any) -> bool:
        """Update the reg_value from a new value."""
        newv = ensure_tuple(self.value_to_reg(value))

        if newv == self.reg_value:
            return False

        self.reg_value = newv
        self.update_value()

        _LOGGER.debug("%s=%s%s %s", self.name, self.value, self.unit, self.reg_value)

        return True

    def value_to_reg(self, value: Any) -> int | Tuple[int, ...]:
        """Get the reg value from a display value."""
        raise NotImplementedError()


@attr.define(slots=True)
class NumberRWSensor(RWSensor):
    """Numeric sensor which can be read and written."""

    min: int | float | Sensor = attr.field(default=0)
    max: int | float | Sensor = attr.field(default=100)

    @property
    def min_value(self) -> int | float:
        """Get the min value from the configured sensor or static value."""
        return self._static_or_sensor_value(self.min)

    @property
    def max_value(self) -> int | float:
        """Get the max value from the configured sensor or static value."""
        return self._static_or_sensor_value(self.max)

    def dependencies(self) -> List[Sensor]:
        """Get a list of sensors upon which this sensor depends."""
        sensors: List[Sensor] = []
        if isinstance(self.min, Sensor):
            sensors.append(self.min)
        if isinstance(self.max, Sensor):
            sensors.append(self.max)
        return sensors

    def value_to_reg(self, value: int | float) -> int | Tuple[int, ...]:
        """Get the reg value from a display value, or the current reg value if out of range."""
        if value < self.min_value or value > self.max_value:
            # Return current reg_value if value is out of range
            return self.reg_value

        return int(value / abs(self.factor))

    @staticmethod
    def _static_or_sensor_value(val: int | float | Sensor) -> int | float:
        if isinstance(val, Sensor):
            if isinstance(val.value, (int, float)):
                return val.value
            return float(val.value or 0)
        return val


@attr.define(slots=True)
class SelectRWSensor(RWSensor):
    """Sensor with a set of options to select from."""

    options: Dict[int, str] = attr.field(default={})
    _values_map: Dict[str, int] = {}

    def __attrs_post_init__(self) -> None:
        """Ensure correct parameters."""
        self._values_map = {v: k for k, v in self.options.items()}

    def available_values(self) -> List[str]:
        """Get the available values for this sensor."""
        return list(self.options.values())

    def value_to_reg(self, value: str) -> int | Tuple[int, ...]:
        """Get the reg value from a display value, or the current reg value if out of range."""
        return self._values_map.get(value, self.reg_value[0])

    def update_value(self) -> None:
        """Update value from current register values."""
        self.value = self.options.get(self.reg_value[0])
        if not self.value:
            _LOGGER.warning or f"Unknown {self.reg_value[0]}"
        )



@attr.define(slots=True)
class TimeRWSensor(RWSensor):
    """Extract the time."""

    min: TimeRWSensor = attr.field(default=None)
    max: TimeRWSensor = attr.field(default=None)

    @property
    def time(self) -> SSTime:
        """Get the value of this sensor as total minutes."""
        time = SSTime()
        time.reg_value = self.reg_value[0]
        return time

    def available_values(self, step_minutes: int) -> List[str]:
        """Get the available values for this sensor."""
        full_day = 24 * 60

        min_val = self.min.time.minutes if self.min else 0
        max_val = self.max.time.minutes if self.max else full_day
        val = self.time.minutes

        time_range = self._range(min_val, max_val, val, step_minutes, full_day)

        return list(map(lambda i: SSTime(i).str_value, time_range))

    def dependencies(self) -> List[Sensor]:
        """Get a list of sensors upon which this sensor depends."""
        sensors: List[Sensor] = []
        if isinstance(self.min, TimeRWSensor):
            sensors.append(self.min)
        if isinstance(self.max, TimeRWSensor):
            sensors.append(self.max)
        return sensors

    def update_value(self) -> None:
        """Extract the time."""
        self.value = self.time.str_value

    def value_to_reg(self, value: str) -> int | Tuple[int, ...]:
        """Get the reg value from a display value."""
        time = SSTime()
        time.str_value = value
        return time.reg_value

    @staticmethod
    def _range(
        start: int, end: int, val: int, step: int, modulo: int
    ) -> Generator[int, None, None]:
        if val % step != 0:
            yield val
        stop = end if start <= end else end + modulo
        for i in range(start, stop, step):
            yield i % modulo
        if start == end or start != end % modulo:
            yield end
