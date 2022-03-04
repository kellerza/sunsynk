"""Sunsynk lib using umodbus."""
import asyncio
import logging
from typing import Sequence

import attr
from async_modbus import AsyncClient, modbus_for_url

from sunsynk.sunsynk import Sunsynk

_LOGGER = logging.getLogger(__name__)


@attr.define
class uSunsynk(Sunsynk):  # pylint: disable=invalid-name
    """Sunsynk class using umodbus."""

    client: AsyncClient = attr.field(default=None)

    async def connect(self) -> None:
        """Connect."""
        _LOGGER.info("Connecting to %s", self.port)
        self.client = modbus_for_url(self.port)

    async def write_register(self, *, address: int, value: int) -> bool:
        """Write to a register - Sunsynk support function code 0x10."""
        try:
            await asyncio.wait_for(
                self.client.write_registers(
                    slave_id=self.server_id,
                    starting_address=address,
                    values=(value,),
                ),
                timeout=10,
            )
            return True
        except asyncio.TimeoutError:
            _LOGGER.critical("timeout writing register %s=%s", address, value)
        return False

    async def read_holding_registers(self, start: int, length: int) -> Sequence[int]:
        """Read a holding register."""
        return await self.client.read_holding_registers(self.server_id, start, length)
