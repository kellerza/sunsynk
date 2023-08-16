"""Sunsync Modbus interface."""
import asyncio
import logging
from typing import Any, Sequence
from urllib.parse import urlparse

import attrs
from pymodbus import __version__ as version
from pymodbus.client import (
    AsyncModbusSerialClient,
    AsyncModbusTcpClient,
    ModbusBaseClient,
)
from pymodbus.transaction import ModbusRtuFramer

from sunsynk.sunsynk import Sunsynk

_LOGGER = logging.getLogger(__name__)


@attrs.define
class PySunsynk(Sunsynk):
    """Sunsync Modbus class."""

    client: ModbusBaseClient = None  # type:ignore

    def _new_client(self) -> ModbusBaseClient:
        """Create a new client."""
        url = urlparse(f"{self.port}")
        if url.hostname:
            host, port = url.hostname, url.port or 502

            # Framer from the URL scheme
            opt: dict[str, Any] = {}
            if url.scheme == "serial-tcp":
                opt = {"framer": ModbusRtuFramer}
            elif url.scheme != "tcp":  # default ModbusSocketFramer
                raise NotImplementedError(
                    "Unknown scheme {url.scheme}: Only tcp and serial-tcp are supported"
                )

            _LOGGER.info("PyModbus %s %s: %s:%s", version, url.scheme, host, port)
            return AsyncModbusTcpClient(host=host, port=port, **opt)

        _LOGGER.info("PyModbus %s Serial: %s", version, self.port)
        return AsyncModbusSerialClient(
            port=self.port,
            baudrate=self.baudrate,
            # method="rtu",
            stopbits=1,
            bytesize=8,
        )

    async def connect(self) -> None:
        """Connect. Will create a new client if required."""
        if not self.client:
            self.client = self._new_client()

        if not self.client.connected:
            await self.client.connect()

        if not self.client.connected:
            raise ConnectionError

    async def write_register(self, *, address: int, value: int) -> bool:
        """Write to a register - Sunsynk supports modbus function 0x10."""
        await self.connect()
        try:
            res = await self.client.write_registers(  # type:ignore
                address=address, values=[value], slave=self.server_id
            )
            if res.function_code < 0x80:  # test that we are not an error
                return True
            _LOGGER.error("failed to write register %s=%s", address, value)
        except (asyncio.TimeoutError, TimeoutError):
            _LOGGER.error("timeout writing register %s=%s", address, value)
        self.timeouts += 1
        return False

    async def read_holding_registers(self, start: int, length: int) -> Sequence[int]:
        """Read a holding register."""
        await self.connect()
        res = await self.client.read_holding_registers(  # type:ignore
            address=start, count=length, slave=self.server_id
        )
        if res.function_code >= 0x80:  # test that we are not an error
            raise IOError(
                f"failed to read register {start} - function code: {res.function_code}"
            )
        return res.registers
