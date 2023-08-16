"""Sunsynk lib using PySolarman."""
# pylint: disable=duplicate-code
import asyncio
import logging
from typing import Sequence
from urllib.parse import urlparse

import attrs
from pysolarmanv5 import PySolarmanV5Async, V5FrameError  # type: ignore

from sunsynk.sunsynk import Sunsynk

_LOGGER = logging.getLogger(__name__)


RETRY_ATTEMPTS = 5


@attrs.define
class SolarmanSunsynk(Sunsynk):
    """Sunsynk class using PySolarmanV5."""

    client: PySolarmanV5Async = None
    dongle_serial_number: int = attrs.field(default=0)

    async def connect(self) -> None:
        """Connect."""
        url = urlparse(f"{self.port}")
        self.allow_gap = 10
        self.client = PySolarmanV5Async(
            address=url.hostname,
            serial=int(self.dongle_serial_number),
            port=url.port,
            mb_slave_id=self.server_id,
            auto_reconnect=True,
            verbose=False,
            socket_timeout=self.timeout * 2,
        )
        await self.client.connect()

    async def write_register(self, *, address: int, value: int) -> bool:
        """Write to a register - Sunsynk supports modbus function 0x10."""
        try:
            await self.client.write_holding_register(address, value)
            return True
        except asyncio.TimeoutError:
            _LOGGER.error("timeout writing register %s=%s", address, value)
        self.timeouts += 1
        return False

    async def read_holding_registers(self, start: int, length: int) -> Sequence[int]:
        """Read a holding register."""
        try:
            return await self.client.read_holding_registers(start, length)
        except Exception as exc:  # pylint: disable=broad-except
            for attempt in range(RETRY_ATTEMPTS):
                try:
                    return await self.client.read_holding_registers(start, length)
                except V5FrameError as err:
                    _LOGGER.info("Frame error retry attempt(%s): %s", attempt, err)
                except Exception as err:  # pylint: disable=broad-except
                    _LOGGER.error("Error retry attempt(%s): %s", attempt, err)
                await asyncio.sleep(2)
                continue
            raise IOError(f"Failed to read register {start}") from exc
