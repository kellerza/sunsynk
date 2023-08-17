"""Sunsynk lib using umodbus."""
import asyncio
import logging
from typing import Sequence
from urllib import parse

import attrs
from async_modbus import AsyncClient, modbus_for_url  # type: ignore
from connio import SERIAL_SCHEMES, SOCKET_SCHEMES  # type: ignore

from sunsynk.sunsynk import Sunsynk

_LOGGER = logging.getLogger(__name__)


@attrs.define
class USunsynk(Sunsynk):
    """Sunsynk class using umodbus."""

    client: AsyncClient = None

    async def connect(self) -> None:
        """Connect."""
        url_result = parse.urlparse(self.port)
        scheme = url_result.scheme
        if scheme not in SOCKET_SCHEMES and scheme not in SERIAL_SCHEMES:
            sks = [f"{s}://" for s in SOCKET_SCHEMES]
            sks.extend(f"{s}://" for s in SERIAL_SCHEMES)
            raise ValueError(
                "Bad port/connection URL. It should start with one of the following: "
                + ", ".join(sks)
            )

        conn_opt = {
            "timeout": self.timeout,  # sockio.TCP & Serial._timeout
        }
        if scheme and scheme in SOCKET_SCHEMES:
            conn_opt["connection_timeout"] = self.timeout  # sockio.TCP

        self.client = modbus_for_url(self.port, conn_opt)

    async def write_register(self, *, address: int, value: int) -> bool:
        """Write to a register - Sunsynk supports modbus function 0x10."""
        try:
            await asyncio.wait_for(
                self.client.write_registers(
                    slave_id=self.server_id,
                    starting_address=address,
                    values=(value,),
                ),
                timeout=self.timeout,
            )
            return True
        except asyncio.TimeoutError:
            _LOGGER.error("timeout writing register %s=%s", address, value)
        self.timeouts += 1
        return False

    async def read_holding_registers(self, start: int, length: int) -> Sequence[int]:
        """Read a holding register."""
        return await self.client.read_holding_registers(self.server_id, start, length)
