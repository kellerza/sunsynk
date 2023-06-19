"""Sunsynk lib using PySolarman."""
import asyncio
import logging
from typing import Sequence
from urllib.parse import urlparse

import attrs
from pysolarmanv5 import PySolarmanV5Async

from sunsynk.sunsynk import Sunsynk

_LOGGER = logging.getLogger(__name__)


retry_attempts = 5


@attrs.define
class SolarmanSunsynk(Sunsynk):  # pylint: disable=invalid-name
    """Sunsynk class using PySolarmanV5."""

    client: PySolarmanV5Async = None

    async def connect(self) -> None:
        """Connect."""
        url = urlparse(f"{self.port}")
        self.allow_gap = 10
        self.client = PySolarmanV5Async(
            address=url.hostname,
            serial=int(self.serial_nr),
            port=url.port,
            mb_slave_id=self.server_id,
            auto_reconnect=True,
            verbose=False,
            socket_timeout=60,
        )
        await self.client.connect()

    async def write_register(self, *, address: int, value: int) -> bool:
        """Write to a register - Sunsynk supports modbus function 0x10."""
        try:
            await self.client.write_holding_register(address=address, value=value)
            return True
        except asyncio.TimeoutError:
            _LOGGER.error("timeout writing register %s=%s", address, value)
        self.timeouts += 1
        return False

    async def read_holding_registers(self, start: int, length: int) -> Sequence[int]:
        """Read a holding register."""
        _LOGGER.info("I'm alive")
        try:
            return await self.client.read_holding_registers(start, length)
        except Exception:
            for attempt in range(retry_attempts):
                try:
                    return await self.client.read_holding_registers(start, length)
                except Exception as e:
                    _LOGGER.error("Caught error(%s): %s", attempt, e)
                    await asyncio.sleep(2)
                    continue
            else:
                raise IOError(f"failed to read register {start}")
