"""Sensor classes represent modbus registers for an inverter."""
from __future__ import annotations

import logging
from inspect import getfullargspec
from math import modf
from typing import Any, Callable, Dict, List, Sequence, Tuple, Union

import attr

_LOGGER = logging.getLogger(__name__)


def ensure_tuple(val: Any) -> Tuple[int]:
    """Return a tuple."""
    if isinstance(val, tuple):
        return val  # type: ignore
    if isinstance(val, int):
        return (val,)
    return tuple(val)  # type: ignore


def needs_tup(val: Any) -> bool:
    """Is the first argument a tuple."""
    return getfullargspec(val)[0][0] == "tup"


@attr.define(slots=True)
class Sensor:
    """Sunsynk sensor."""

    register: Tuple[int, ...] = attr.field(converter=ensure_tuple)
    name: str = attr.field()
    unit: str = attr.field(default="")
    factor: float = attr.field(default=1)
    value: Union[float, int, str, None] = None
    func: Union[
        None, Callable[[Tuple[int, ...]], str], Callable[[float], float]
    ] = attr.field(default=None)

    def append_to(self, arr: List[Sensor]) -> Sensor:
        """Append to a list of sensors."""
        arr.append(self)
        return self

    @property
    def id(self) -> str:  # pylint: disable=invalid-name
        """Get the sensor ID."""
        return slug(self.name)


class HSensor(Sensor):
    """Hybrid sensor."""


def group_sensors(
    sensors: Sequence[Sensor], allow_gap: int = 3
) -> Sequence[Sequence[int]]:
    """Group sensor registers into blocks for reading."""
    if not sensors:
        return []
    regs = set()
    for sen in sensors:
        regs |= set(sen.register)
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
        if not sen.register[0] in registers:
            continue

        if sen.func and needs_tup(sen.func):
            try:
                tup = tuple(registers[i] for i in sen.register)
            except KeyError as err:
                _LOGGER.error(
                    "Could not update_sensor %s - registers[%s] not found",
                    sen.id,
                    err,
                )
                continue
            sen.value = sen.func(tup)  # type: ignore
            return

        hval = 0
        try:
            hval = registers[sen.register[1]]
        except IndexError:
            pass
        lval = registers[sen.register[0]]

        sen.value = (lval + (hval << 16)) * sen.factor
        if sen.func:
            sen.value = sen.func(sen.value)  # type: ignore
        if isinstance(sen.value, float):
            if modf(sen.value)[0] == 0:
                sen.value = int(sen.value)
            else:
                sen.value = round(sen.value, 2)
        _LOGGER.debug(
            "%s low=%d high=%d value=%d%s",
            sen.name,
            lval,
            hval,
            sen.value,
            sen.unit,
        )


def slug(name: str) -> str:
    """Create a slug."""
    return name.lower().replace(" ", "_")


def offset100(val: float) -> float:
    """Offset by 100 for temperature."""
    return val - 100


def sd_status(tup: Tuple[int, ...]) -> str:
    """SD card status."""
    res = {
        1000: "fault",
        2000: "ok",
    }.get(tup[0], "")
    if res:
        return res
    return f"unknown {tup[0]}"


def inv_state(tup: Tuple[int, ...]) -> str:
    """Offset by 100 for temperature."""
    if tup[0] == 2:
        return "ok"
    return f"unknown {tup[0]}"


def signed(val: float) -> float:
    """Value might be negative."""
    if val > 0x7FFF:
        return val - 0xFFFF
    return val


def decode_serial(tup: Tuple[int, ...]) -> str:
    """Decode serial."""
    res = ""
    for b16 in tup:
        res += chr(b16 >> 8)
        res += chr(b16 & 0xFF)
    return res


def decode_fault(tup: Tuple[int, ...]) -> str:
    """Decode faults."""
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
    for b16 in tup:
        for bit in range(16):
            msk = 1 << bit
            if msk & b16:
                msg = f"F{bit+off+1:02} " + faults.get(off + msk, "")
                err.append(msg.strip())
        off += 16
    if not err:
        return ""
    return ", ".join(err)
