"""Register state."""
import logging
from collections import defaultdict
from typing import Callable, Generator, Iterable, Iterator, Optional, Sequence, cast

import attr

from sunsynk.rwsensors import RWSensor
from sunsynk.sensors import NumType, Sensor, ValType

_LOGGER = logging.getLogger(__name__)


@attr.define()
class InverterState:
    """Keep the state of the inverter."""

    values: dict[Sensor, ValType] = attr.field(factory=dict)
    registers: dict[int, int] = attr.field(factory=dict)
    onchange: Optional[Callable[[Sensor, ValType, ValType], None]] = attr.field(
        default=None
    )
    history: dict[Sensor, list[NumType]] = attr.field(
        init=False, factory=lambda: defaultdict(list)
    )
    """Historic values for numeric types."""
    historynn: dict[Sensor, list[ValType]] = attr.field(
        init=False, factory=lambda: defaultdict(list)
    )
    """Historic values for non-numeric types."""

    def __getitem__(self, sensor: Sensor) -> ValType:
        """Get the current value of a sensor."""
        return self.values.get(sensor)

    def get(self, sensor: Sensor, default: ValType = None) -> ValType:
        """Get the current value of a sensor."""
        return self.values.get(sensor, default)

    def track(self, *sensor: Sensor) -> None:
        """Add a sensor to be tracked."""
        for sen in sensor:
            self.values.setdefault(sen, None)
            if isinstance(sen, RWSensor) and sen.dependencies:
                for dep in sen.dependencies:
                    self.values.setdefault(dep, None)

    @property
    def sensors(self) -> Iterator[Sensor]:
        """Get a generator of all sensors."""
        return iter(self.values.keys())

    def update(self, new_regs: dict[int, int]) -> None:
        """Update the state."""
        changed: dict[Sensor, tuple[ValType, ValType]] = {}  # sensor, old & new value

        for sen in self.sensors:
            # No updates for this sensor, skip
            if not any(a in new_regs for a in sen.address):
                continue

            regs = tuple(new_regs.get(a, self.registers.get(a, 0)) for a in sen.address)

            assert isinstance(regs, tuple)
            assert isinstance(sen.address, tuple)
            assert len(regs) == len(sen.address)

            oldv = self.values[sen]
            if sen.bitmask:
                regs = (regs[0] & sen.bitmask,)

            newv = sen.reg_to_value(regs)
            _LOGGER.debug("register %s = %s (old=%s)", self.registers, oldv, newv)
            if oldv != newv:
                self.values[sen] = newv
                changed[sen] = (newv, oldv)

            numeric = (
                isinstance(newv, (int, float))
                and not isinstance(sen, RWSensor)
                and sen not in self.historynn
            )
            if numeric:
                self.history[sen].append(cast(NumType, newv))
            else:
                if not self.historynn[sen]:
                    self.historynn[sen].append(None)
                self.historynn[sen].append(newv)
                while len(self.historynn[sen]) > 2:
                    self.historynn[sen].pop(0)

        self.registers.update(new_regs)

        if not self.onchange:
            return
        for sen, (new, old) in changed.items():
            self.onchange(sen, new, old)

    def history_average(self, sensor: Sensor) -> NumType:
        """Return the average of the history."""
        hist0, *hist = self.history[sensor]  # raises ValueError if no history
        if not hist:
            return hist0
        res = sum(hist) / len(hist)
        self.history[sensor].clear()
        self.history[sensor].append(res)
        return res

    # def history_done(self) -> None:
    #     """Flush the history."""
    #     self.history.clear()

    # def history_significant_change(
    #     self, change: float, percent: int
    # ) -> dict[Sensor, NumType]:
    #     """Check if there has been a significant change in the history."""
    #     changes: dict[Sensor, NumType] = {}
    #     for sen, hist in self.history.items():
    #         if len(hist) < 2:
    #             continue
    #         _change = abs(hist[-1] - hist[-2]) > change
    #         _percent = abs(hist[-1]) > abs(hist[-2]) * (percent / 100)
    #         if _change or _percent:
    #             changes[sen] = hist[-1]
    #             hist.clear()
    #             hist.append(changes[sen])

    #     return changes


def group_sensors(
    sensors: Iterable[Sensor], allow_gap: int = 3, max_group_size: int = 60
) -> Generator[list[int], None, None]:
    """Group sensor registers into blocks for reading."""
    if not sensors:
        return
    regs = {r for s in sensors for r in s.address}
    group: list[int] = []
    adr0 = 0
    for adr1 in sorted(regs):
        if group and (adr1 - adr0 > allow_gap or adr1 - group[0] >= max_group_size):
            yield group
            group = []
        adr0 = adr1
        group.append(adr1)
    if group:
        yield group


def register_map(start: int, registers: Sequence[int]) -> dict[int, int]:
    """Turn the registers into a dictionary or map."""
    return dict(enumerate(registers, start))
