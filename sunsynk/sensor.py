"""Sensor classes represent modbus registers for an inverter."""
from __future__ import annotations

import logging
from math import modf
from typing import Any, Dict, Generator, List, Sequence, Tuple, Union

import attr

_LOGGER = logging.getLogger(__name__)


def ensure_tuple(val: Any) -> Tuple[int]:
    """Return a tuple."""
    if isinstance(val, tuple):
        return val  # type: ignore
    if isinstance(val, int):
        return (val,)
    return tuple(val)  # type: ignore


def _round(val: Union[int, float, str]) -> Union[int, float, str]:
    """Round if float."""
    if not isinstance(val, float):
        return val
    val = round(val, 2)
    if modf(val)[0] == 0:
        return int(val)
    return val


def _signed(val: Union[int, float]) -> Union[int, float]:
    """Convert 16-bit value to signed int."""
    return val if val <= 0x7FFF else val - 0xFFFF


@attr.define(slots=True)
class Sensor:
    """Sunsynk sensor."""

    reg_address: Tuple[int, ...] = attr.field(converter=ensure_tuple)
    name: str = attr.field()
    unit: str = attr.field(default="")
    factor: float = attr.field(default=1)
    value: Union[float, int, str, None] = None
    # func: Union[
    #     None, Callable[[Tuple[int, ...]], str], Callable[[float], Any]
    # ] = attr.field(default=None)
    reg_value: Tuple[int, ...] = attr.field(init=False, factory=tuple)

    def append_to(self, arr: List[Sensor]) -> Sensor:
        """Append to a list of sensors."""
        arr.append(self)
        return self

    def reg_to_value(self, value: Tuple[int, ...]) -> Union[float, int, str, None]:
        """Update the reg_value and update."""
        if isinstance(value, tuple):
            self.reg_value = value
        else:
            self.reg_value = (value,)
        self.update_value()
        return self.value

    @property
    def id(self) -> str:  # pylint: disable=invalid-name
        """Get the sensor ID."""
        return slug(self.name)

    def update_value(self) -> None:
        """Update the value from the reg_value."""
        val: Union[int, float] = self.reg_value[0]
        if len(self.reg_value) > 1:
            val += self.reg_value[1] << 16
        elif self.factor < 0:  # Indicate this register is signed
            val = _signed(val)
        self.value = _round(val * abs(self.factor))

        _LOGGER.debug("%s=%s%s %s", self.name, self.value, self.unit, self.reg_value)


class HSensor(Sensor):
    """Hybrid sensor."""


@attr.define(slots=True)
class MathSensor(Sensor):
    """Math sensor, add multiple registers."""

    factors: Tuple[float, ...] = attr.field(default=None, converter=ensure_tuple)
    no_negative: bool = attr.field(default=False)

    def update_value(self) -> None:
        """Update the value."""
        self.value = _round(
            sum(_signed(i) * s for i, s in zip(self.reg_value, self.factors))
        )
        if self.no_negative and not isinstance(self.value, str) and self.value < 0:
            self.value = 0

    def __attrs_post_init__(self) -> None:
        """Ensure correct parameters."""
        assert len(self.reg_address) == len(self.factors)


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

    min: int | Sensor = attr.field(default=0)
    max: int | Sensor = attr.field(default=100)

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

    def value_to_reg(self, value: int) -> int | Tuple[int, ...]:
        """Get the reg value from a display value, or the current reg value if out of range."""
        if value < self.min_value or value > self.max_value:
            # Return current reg_value if value is out of range
            return self.reg_value

        return int(value / abs(self.factor))

    @staticmethod
    def _static_or_sensor_value(val: int | Sensor) -> int | float:
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
        self.value = (
            self.options.get(self.reg_value[0]) or f"Unknown {self.reg_value[0]}"
        )


def group_sensors(
    sensors: Sequence[Sensor], allow_gap: int = 3, max_group_size: int = 60
) -> Generator[list[int], None, None]:
    """Group sensor registers into blocks for reading."""
    if not sensors:
        return
    regs = {r for s in sensors for r in s.reg_address}
    group: List[int] = []
    adr0 = 0
    for adr1 in sorted(regs):
        if group and (adr1 - adr0 > allow_gap or len(group) >= max_group_size):
            yield group
            group = []
        adr0 = adr1
        group.append(adr1)
    if group:
        yield group


def update_sensors(sensors: Sequence[Sensor], registers: Dict[int, int]) -> None:
    """Update sensors."""
    for sen in sensors:
        try:
            sen.reg_value = tuple(registers[i] for i in sen.reg_address)
        except KeyError:
            continue
        sen.update_value()


def slug(name: str) -> str:
    """Create a slug."""
    return name.lower().replace(" ", "_").replace("-", "_")


class TempSensor(Sensor):
    """Offset by 100 for temperature."""

    def update_value(self) -> None:
        """Offset by 100 for temperature."""
        super().update_value()
        try:
            self.value = round(float(self.value) - 100, 2)  # type: ignore
        except (TypeError, ValueError) as err:
            self.value = 0
            _LOGGER.error("Could not decode temperature: %s", err)


class SSTime:
    """Deals with inverter time format conversion complexities."""

    minutes: int

    def __init__(self, minutes: int = 0) -> None:
        """Init the time with minutes."""
        self.minutes = minutes

    @property
    def reg_value(self) -> int:
        """Get the register value."""
        hours, minutes = divmod(self.minutes, 60)
        return hours * 100 + minutes

    @reg_value.setter
    def reg_value(self, reg_value: int) -> None:
        """Convert from a register value."""
        hours, minutes = divmod(reg_value, 100)
        self.minutes = hours * 60 + minutes

    @property
    def str_value(self) -> str:
        """Get the value in hh:mm format."""
        hours, minutes = divmod(self.minutes, 60)
        return f"{hours}:{minutes:02}"

    @str_value.setter
    def str_value(self, value: str) -> None:
        """Parse a string in hh:mm format."""
        (hours, _, minutes) = value.partition(":")
        self.minutes = int(hours) * 60 + int(minutes)


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


class SDStatusSensor(Sensor):
    """SD card status."""

    def update_value(self) -> None:
        """SD card status."""
        self.value = {
            1000: "fault",
            2000: "ok",
        }.get(self.reg_value[0]) or f"unknown {self.reg_value[0]}"


class InverterStateSensor(Sensor):
    """Inverter status."""

    def update_value(self) -> None:
        """Inverter status."""
        if self.reg_value[0] == 2:
            self.value = "ok"
        else:
            self.value = f"unknown {self.reg_value[0]}"


class SerialSensor(Sensor):
    """Decode Inverter serial number."""

    def update_value(self) -> None:
        """Decode Inverter serial number."""
        self.value = ""
        res = ""
        for b16 in self.reg_value:
            res += chr(b16 >> 8)
            res += chr(b16 & 0xFF)
        self.value = res


class FaultSensor(Sensor):
    """Decode Inverter faults."""

    def update_value(self) -> None:
        """Decode Inverter faults."""
        faults = {
            13: "Working mode change",
            18: "AC over current",
            20: "DC over current",
            23: "F23 AC leak current or transient over current",
            24: "F24 DC insulation impedance",
            26: "F26 DC busbar imbalanced",
            29: "Parallel comms cable",
            35: "No AC grid",
            42: "AC line low voltage",
            47: "AC freq high/low",
            56: "DC busbar voltage low",
            63: "ARC fault",
            64: "Heat sink tempfailure",
        }
        err = []
        off = 0
        for b16 in self.reg_value:
            for bit in range(16):
                msk = 1 << bit
                if msk & b16:
                    msg = f"F{bit+off+1:02} " + faults.get(off + msk, "")
                    err.append(msg.strip())
            off += 16
        self.value = ", ".join(err)
