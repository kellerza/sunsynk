"""Sensor classes represent modbus registers for an inverter."""
from __future__ import annotations

import logging
import re
from typing import Callable, Generator, Optional, Union

import attrs
from mqtt_entity.utils import BOOL_OFF, BOOL_ON  # type: ignore

from sunsynk.helpers import NumType, RegType, SSTime, ValType, as_num, hex_str
from sunsynk.sensors import Sensor

_LOGGER = logging.getLogger(__name__)
ResolveType = Optional[Callable[[Sensor, ValType], ValType]]


@attrs.define(slots=True, eq=False)
class RWSensor(Sensor):
    """Read & write sensor."""

    def reg(self, *regs: int, msg: str = "") -> RegType:
        """Check the registers are within the bitmask."""
        if self.bitmask and regs[0] != (regs[0] & self.bitmask):
            _LOGGER.error(
                "Trying to set a register value outside the sensor's bitmask! sensor:%s regvalue:%s %s",
                self.name,
                regs,
                msg,
            )
            return (regs[0] & self.bitmask,) + tuple(regs[1:])
        return regs

    def value_to_reg(self, value: ValType, resolve: ResolveType) -> RegType:
        """Get the reg value from a display value."""
        raise NotImplementedError()

    def reg_to_value(self, regs: RegType) -> ValType:
        """Decode the register."""
        return super().reg_to_value(self.masked(regs))

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


@attrs.define(slots=True, eq=False)
class NumberRWSensor(RWSensor):
    """Numeric sensor which can be read and written."""

    min: int | float | Sensor = attrs.field(default=0)
    max: int | float | Sensor = attrs.field(default=100)

    @property
    def dependencies(self) -> list[Sensor]:
        """Get a list of sensors upon which this sensor depends."""
        return [s for s in (self.min, self.max) if isinstance(s, Sensor)]

    def value_to_reg(self, value: ValType, resolve: ResolveType) -> RegType:
        """Get the reg value from a display value, or the current reg value if out of range."""
        fval = float(value)  # type:ignore
        minv = resolve_num(resolve, self.min, 0)
        maxv = resolve_num(resolve, self.max, 100)
        val = int(max(minv, min(maxv, fval / abs(self.factor))))
        if len(self.address) == 1:
            if val < 0:
                val = 0x10000 + val
            return self.reg(val)
        if len(self.address) == 2:
            return self.reg(val & 0xFFFF, int(val >> 16))
        raise NotImplementedError


@attrs.define(slots=True, eq=False)
class SelectRWSensor(RWSensor):
    """Sensor with a set of options to select from."""

    options: dict[int, str] = attrs.field(factory=dict)
    # switch: Optional[tuple[int, int]] = attrs.field(default=None)

    # def __attrs_post_init__(self) -> None:
    #     """Ensure correct parameters."""
    #     if self.switch:
    #         assert not self.options
    #         assert len(self.switch) == 2
    #         self.options = {self.switch[0]: "OFF", self.switch[1]: "ON"}

    def available_values(self) -> list[str]:
        """Get the available values for this sensor."""
        return list(self.options.values())

    def value_to_reg(self, value: ValType, resolve: ResolveType) -> RegType:
        """Get the reg value from a display value, or the current reg value if out of range."""
        value = str(value)
        regs = [r for r, v in self.options.items() if v == value]
        if regs:
            return self.reg(regs[0])
        _LOGGER.warning("Unknown %s", value)
        current = resolve(self, None) if resolve else 0
        return self.value_to_reg(current, None)  # type:ignore

    def reg_to_value(self, regs: RegType) -> ValType:
        """Decode the register."""
        regsm = self.masked(regs)
        res = self.options.get(regsm[0])
        if res is None:
            _LOGGER.warning("%s: Unknown register value %s", self.id, regsm[0])
        return res


@attrs.define(slots=True, eq=False)
class SwitchRWSensor(SelectRWSensor):
    """Switch Sensor."""

    on: int = attrs.field(default=1)
    """The register value representing ON."""
    off: int = attrs.field(default=0)
    """The register value representing OFF."""

    def __attrs_post_init__(self) -> None:
        """Ensure correct parameters."""
        assert not self.options
        assert self.on != self.off
        self.options = {self.off: BOOL_OFF, self.on: BOOL_ON}


@attrs.define(slots=True, eq=False)
class SystemTimeRWSensor(RWSensor):
    """Read & write time sensor."""

    def value_to_reg(self, value: ValType, resolve: ResolveType) -> RegType:
        """Get the reg value from a display value."""
        # pylint: disable=invalid-name
        redt = re.compile(r"(2\d{3})-(\d{2})-(\d{2}) ([012]?\d{1}):(\d{2}):(\d{2})")
        match = redt.fullmatch(str(value).strip())
        if not match:
            raise ValueError(f"Invalid datetime {value}")
        y, m, d = int(match.group(1)) - 2000, int(match.group(2)), int(match.group(3))
        h, mn, s = int(match.group(4)), int(match.group(5)), int(match.group(6))
        regs = (
            (y << 8) + m,
            (d << 8) + h,
            (mn << 8) + s,
        )
        msg = f"20{y:02}-{m:02}-{d:02} {h:02}:{mn:02}:{s:02}"
        msg += f"==> Registers(ym, dh, ms):{hex_str(regs, address=self.address)}"
        assert len(regs) == len(self.address)
        _LOGGER.debug("Set date_time = %s", msg)
        return regs

    def reg_to_value(self, regs: RegType) -> ValType:
        """Decode the register."""
        # pylint: disable=invalid-name
        y = ((regs[0] & 0xFF00) >> 8) + 2000
        m = regs[0] & 0xFF
        d = (regs[1] & 0xFF00) >> 8
        h = regs[1] & 0xFF
        mn = (regs[2] & 0xFF00) >> 8
        s = regs[2] & 0xFF
        return f"{y}-{m:02}-{d:02} {h}:{mn:02}:{s:02}"


@attrs.define(slots=True, eq=False)
class TimeRWSensor(RWSensor):
    """Extract the time."""

    min: TimeRWSensor = attrs.field(default=None)
    max: TimeRWSensor = attrs.field(default=None)

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

    def value_to_reg(self, value: ValType, resolve: ResolveType) -> RegType:
        """Get the reg value from a display value."""
        return self.reg(SSTime(string=str(value)).reg_value)

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
    resolve: ResolveType,
    val: Union[NumType, Sensor],
    default: NumType = 0,
) -> NumType:
    """Resolve a number helper."""
    if isinstance(val, (int, float)):
        return val
    if isinstance(val, Sensor):
        res = resolve(val, default) if resolve else 0
        return as_num(res)
    return as_num(val)
