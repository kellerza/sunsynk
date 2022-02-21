"""Sunsync Modbus interface."""
import asyncio
from typing import Dict, Sequence

import attr

from .sensor import Sensor


@attr.define
class Sunsynk:
    """Sunsync Modbus class."""

    port: str = attr.ib(default="/dev/tty0")
    baudrate: int = attr.ib(default=9600)
    server_id: int = attr.ib(default=1)
    timeout: int = attr.ib(default=10)

    async def connect(self, timeout: int = 5) -> None:
        """Connect."""
        raise NotImplementedError

    async def write_register(self, *, address: int, value: int) -> bool:
        """Write to a register - Sunsynk support function code 0x10."""
        raise NotImplementedError

    async def write(self, sensor: Sensor) -> None:
        """Write a sensor."""
        await self.write_register(
            address=sensor.reg_address[0], value=sensor.reg_value[0]
        )
        for idx in range(len(sensor.reg_address) - 1):
            await asyncio.sleep(0.05)
            await self.write_register(
                address=sensor.reg_address[idx], value=sensor.reg_value[idx]
            )

    async def read(self, sensors: Sequence[Sensor]) -> None:
        """Read a list of sensors."""
        raise NotImplementedError


def register_map(start: int, registers: Sequence[int]) -> Dict[int, int]:
    """Turn the registers into a dictionary or map."""
    return {start + i: r for (i, r) in enumerate(registers)}
