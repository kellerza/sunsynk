"""Sensor classes represent modbus registers for an inverter."""
from __future__ import annotations

from typing import List, Sequence, Union

import attr


@attr.define(slots=True)
class Sensor:
    """Sunsynk sensor."""

    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-few-public-methods
    register: int = attr.field()
    name: str = attr.field()
    unit: str = attr.field(default="")
    factor: float = attr.field(default=1)
    high_register: Union[int, None] = attr.field(
        default=None
    )  # The high register for 32-bit values
    value: Union[float, None] = None

    def append_to(self, arr: List[Sensor]) -> Sensor:
        """Append to a list of sensors."""
        arr.append(self)
        return self


def group_sensors(
    sensors: Sequence[Sensor], allow_gap: int = 3
) -> Sequence[Sequence[int]]:
    """Group sensor registers into blocks for reading."""
    regs = set()
    for sen in sensors:
        regs.add(sen.register)
        if sen.high_register is not None:
            regs.add(sen.high_register)
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
        if sen.register >= register and sen.register < hreg:
            hval = 0
            if (
                sen.high_register is not None
                and sen.high_register >= register
                and sen.high_register < hreg
            ):
                hval = values[sen.high_register - register]
            lval = values[sen.register - register]

            sen.value = (lval + hval << 16) * sen.factor


# a = (msg.payload.data / 10)
# if (a > 32767) {
# msg.payload = (a - 65535) / 10;
# } else {
#     msg.payload = (a) / 1;
# }
