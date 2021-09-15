"""Sensor classes represent modbus registers for an inverter."""
from __future__ import annotations

import logging
from math import modf
from typing import Any, List, Sequence, Tuple, Union

import attr

_LOGGER = logging.getLogger(__name__)


def tup(val: Any) -> Tuple[int]:
    """Return a tuple."""
    if isinstance(val, tuple):
        return val
    if isinstance(val, int):
        return (val,)
    return tuple(val)


@attr.define(slots=True)
class Sensor:
    """Sunsynk sensor."""

    register: Tuple[int] = attr.field(converter=tup)
    name: str = attr.field()
    unit: str = attr.field(default="")
    factor: float = attr.field(default=1)
    value: Union[float, None] = None

    def append_to(self, arr: List[Sensor]) -> Sensor:
        """Append to a list of sensors."""
        arr.append(self)
        return self

    @property
    def id(self):
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


def update_sensors(
    sensors: Sequence[Sensor], register: int, values: Sequence[int]
) -> None:
    """Update sensors."""
    hreg = register + len(values)
    for sen in sensors:
        if sen.register[0] >= register and sen.register[0] < hreg:
            hval = 0
            try:
                hval = values[sen.register[1] - register]
            except IndexError:
                pass
            lval = values[sen.register[0] - register]

            sen.value = round((lval + (hval << 16)) * sen.factor, 2)
            if modf(sen.value)[0] == 0:
                sen.value = int(sen.value)
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
