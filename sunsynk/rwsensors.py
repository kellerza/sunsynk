"""Sensor classes represent modbus registers for an inverter."""
from __future__ import annotations

import logging
from typing import Callable, Generator, Union

import attr

from sunsynk.helpers import NumType, RegType, SSTime, ValType, as_num
from sunsynk.sensors import Sensor

_LOGGER = logging.getLogger(__name__)


@attr.define(slots=True, eq=False)
class RWSensor(Sensor):
    """Read & write sensor."""

    def check_bitmask(self, value: ValType, regs: RegType) -> RegType:
        """Check the registers are within the bitmask."""
        if self.bitmask and regs[0] != (regs[0] & self.bitmask):
            _LOGGER.error(
                "Trying to set a value outside the sensor's bitmask! %s (value=%s, regvalue=%s)",
                self.name,
                value,
                regs,
            )
            return (regs[0] & self.bitmask,)
        return regs

    def value_to_reg(
        self, value: ValType, resolve: Callable[[Sensor, ValType], ValType]
    ) -> RegType:
        """Get the reg value from a display value."""
        raise NotImplementedError()

    def __attrs_post_init__(self) -> None:
        """Run post init."""
        if self.bitmask > 0 and len(self.address) != 1:
            _LOGGER.fatal(
                "Sensors with a bitmask should reference a single register! %s [registers=%s]",
                self.name,
                self.address,
            )

    @property
    def dependencies(self) -> list[Sensor]:
        """Dependencies."""
        return []


@attr.define(slots=True, eq=False)
class NumberRWSensor(RWSensor):
    """Numeric sensor which can be read and written."""

    min: int | float | Sensor = attr.field(default=0)
    max: int | float | Sensor = attr.field(default=100)

    @property
    def dependencies(self) -> list[Sensor]:
        """Get a list of sensors upon which this sensor depends."""
        return [s for s in (self.min, self.max) if isinstance(s, Sensor)]

    def value_to_reg(
        self, value: ValType, resolve: Callable[[Sensor, ValType], ValType]
    ) -> RegType:
        """Get the reg value from a display value, or the current reg value if out of range."""
        if value is None or isinstance(value, str):
            raise TypeError
        minv = resolve_num(resolve, self.min, 0)
        maxv = resolve_num(resolve, self.max, 100)
        val = int(max(minv, min(maxv, value / abs(self.factor))))
        if len(self.address) == 1:
            return (val,)
        if len(self.address) == 2:
            return (val & 0xFFFF, int(val >> 16))
        raise NotImplementedError


@attr.define(slots=True, eq=False)
class SelectRWSensor(RWSensor):
    """Sensor with a set of options to select from."""

    options: dict[int, str] = attr.field(default={})

    def available_values(self) -> list[str]:
        """Get the available values for this sensor."""
        return list(self.options.values())

    def value_to_reg(
        self, value: ValType, resolve: Callable[[Sensor, ValType], ValType]
    ) -> RegType:
        """Get the reg value from a display value, or the current reg value if out of range."""
        value = str(value)
        for reg, val in self.options.items():
            if val == value:
                return (reg,)
        # Unknown value, try to get the existing value
        _LOGGER.warning("Unknown %s", value)
        if resolve is None:
            return None
        current = resolve(self, None)
        return self.value_to_reg(current, None)  # type:ignore

    def reg_to_value(self, regs: RegType) -> ValType:
        """Decode the register."""
        if regs[0] in self.options:
            return self.options[regs[0]]
        _LOGGER.warning("%s: Unknown register value %s", self.id, regs[0])
        return None


@attr.define(slots=True)
class SwitchRWSensor(SelectRWSensor):
    """Sensor with a set of options to switch from."""


@attr.define(slots=True, eq=False)
class TimeRWSensor(RWSensor):
    """Extract the time."""

    min: TimeRWSensor = attr.field(default=None)
    max: TimeRWSensor = attr.field(default=None)

    def available_values(
        self, step_minutes: int, resolve: Callable[[Sensor, ValType], ValType]
    ) -> list[str]:
        """Get the available values for this sensor."""
        full_day = 24 * 60

        min_val = SSTime(string=str(resolve(self.min, 0))).minutes if self.min else 0
        max_val = (
            SSTime(string=str(resolve(self.max, 0))).minutes if self.max else full_day
        )
        val = SSTime(string=str(resolve(self, 0))).minutes

        time_range = self._range(min_val, max_val, val, step_minutes, full_day)
        return list(map(lambda m: SSTime(minutes=m).str_value, time_range))

    @property
    def dependencies(self) -> list[Sensor]:
        """Get a list of sensors upon which this sensor depends."""
        return [s for s in (self.min, self.max) if isinstance(s, TimeRWSensor)]

    def reg_to_value(self, regs: RegType) -> ValType:
        """Decode the time from a register."""
        return SSTime(register=regs[0]).str_value

    def value_to_reg(
        self, value: ValType, resolve: Callable[[Sensor, ValType], ValType]
    ) -> RegType:
        """Get the reg value from a display value."""
        return (SSTime(string=str(value)).reg_value,)

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


def resolve_num(
    resolve: Callable[[Sensor, ValType], ValType],
    val: Union[NumType, Sensor],
    default: NumType = 0,
) -> NumType:
    """Resolve a number helper."""
    if isinstance(val, (int, float)):
        return val
    if isinstance(val, Sensor):
        res = resolve(val, default)
        return as_num(res)
    return as_num(val)
