"""Sensor classes represent modbus registers for an inverter."""
from __future__ import annotations

import logging
from math import modf
from typing import Any, Dict, List, Sequence, Tuple, Union

import attr

_LOGGER = logging.getLogger(__name__)


def ensure_tuple(val: Any) -> Tuple[int]:
    """Return a tuple."""
    if isinstance(val, tuple):
        return val  # type: ignore
    if isinstance(val, int):
        return (val,)
    return tuple(val)  # type: ignore


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
        hval = self.reg_value[1] if len(self.reg_value) > 1 else 0
        lval = self.reg_value[0]

        _LOGGER.debug(
            "%s low=%d high=%d value=%s%s",
            self.name,
            lval,
            hval,
            self.value,
            self.unit,
        )

        self.value = (lval + (hval << 16)) * self.factor

        if self.factor < 0:  # Indicate this register is signed
            self.value = -self.value
            # Value might be negative.
            if self.value > 0x7FFF:
                self.value -= 0xFFFF

        # if self.func:
        #     self.value = self.func(self.value)  # type: ignore

        # make integer/round?
        if isinstance(self.value, float):
            if modf(self.value)[0] == 0:
                self.value = int(self.value)
            else:
                self.value = round(self.value, 2)


class HSensor(Sensor):
    """Hybrid sensor."""


class RWSensor(Sensor):
    """Read & write sensor."""


def group_sensors(
    sensors: Sequence[Sensor], allow_gap: int = 3
) -> Sequence[Sequence[int]]:
    """Group sensor registers into blocks for reading."""
    if not sensors:
        return []
    regs = set()
    for sen in sensors:
        regs |= set(sen.reg_address)
    adr = sorted(regs)
    cgroup = [adr[0]]
    groups = [cgroup]
    for idx in range(1, len(adr)):
        gap = adr[idx] - adr[idx - 1]
        if gap > allow_gap or len(cgroup) >= 60:
            cgroup = []
            groups.append(cgroup)
        cgroup.append(adr[idx])
    return groups


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
    return name.lower().replace(" ", "_")


class TemperatureSensor(Sensor):
    """Offset by 100 for temperature."""

    def update_value(self) -> None:
        """Offset by 100 for temperature."""
        super().update_value()
        try:
            self.value = round(float(self.value) - 100, 2)  # type: ignore
        except (TypeError, ValueError) as err:
            self.value = 0
            _LOGGER.error("Could not decode temperature: %s", err)


class TimeRWSensor(RWSensor):
    """Extract the time."""

    def update_value(self) -> None:
        """Extract the time."""
        sval = str(self.reg_value[0])
        self.value = f"{sval[:-2]}:{sval[-2:]}"


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
