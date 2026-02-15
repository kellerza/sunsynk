"""Sunsync Modbus interface."""

import asyncio
import logging
from collections.abc import Sequence
from dataclasses import dataclass, field
from urllib.parse import urlparse

from pymodbus import __version__ as version
from pymodbus.client import (
    AsyncModbusSerialClient,
    AsyncModbusTcpClient,
    AsyncModbusUdpClient,
    ModbusBaseClient,
)
from pymodbus.framer import FramerType

from sunsynk.sunsynk import Sunsynk

_LOG = logging.getLogger(__name__)


@dataclass(kw_only=True)
class PySunsynk(Sunsynk):
    """Sunsync Modbus class."""

    client: ModbusBaseClient | None = field(default=None, repr=False)

    def _new_client(self) -> ModbusBaseClient:
        """Create a new client."""
        url = urlparse(f"{self.port}")
        if url.hostname:
            host, port = url.hostname, url.port or 502

            client: AsyncModbusTcpClient | AsyncModbusUdpClient | None = None

            match url.scheme:  # python 3.10 minimum
                case "serial-tcp":  # RTU-over-TCP
                    client = AsyncModbusTcpClient(
                        host=host, port=port, framer=FramerType.RTU
                    )
                case "tcp":
                    client = AsyncModbusTcpClient(host=host, port=port)
                case "serial-udp":  # RTU-over-UDP
                    client = AsyncModbusUdpClient(
                        host=host, port=port, framer=FramerType.RTU
                    )
                case "udp":
                    client = AsyncModbusUdpClient(host=host, port=port)
                case _:
                    raise NotImplementedError(
                        "Unknown scheme {url.scheme}: Only tcp and serial-tcp are supported"
                    )

            _LOG.info("PyModbus %s %s: %s:%s", version, url.scheme, host, port)
            return client

        _LOG.info("PyModbus %s Serial: %s", version, self.port)
        return AsyncModbusSerialClient(
            port=self.port,
            baudrate=self.baudrate,
            # method="rtu",
            stopbits=1,
            bytesize=8,
        )

    async def connected_client(self) -> ModbusBaseClient:
        """Get client, connect if needed."""
        if not self.client:
            self.client = self._new_client()
        if self.client.connected:
            return self.client
        try:
            async with asyncio.timeout(self.timeout):
                await self.client.connect()
        except TimeoutError:
            raise ConnectionError("Failed to connect: timeout") from None
        except Exception as err:
            raise ConnectionError(f"Failed to connect: {err}") from err
        if not self.client.connected:
            raise ConnectionError("Failed to connect")
        return self.client

    async def connect(self) -> None:
        """Connect. Will create a new client if required."""
        await self.connected_client()

    async def write_register(self, *, address: int, value: int) -> bool:
        """Write to a register - Sunsynk supports modbus function 0x10."""
        try:
            client = await self.connected_client()
            async with asyncio.timeout(self.timeout):
                res = await client.write_registers(
                    address=address,
                    values=[value],
                    device_id=self.server_id,
                )
            if res.function_code < 0x80:  # test that we are not an error
                return True
            _LOG.error("failed to write register %s=%s", address, value)
        except TimeoutError:
            _LOG.error("timeout writing register %s=%s", address, value)
            self.timeouts += 1
        return False

    async def read_holding_registers(self, start: int, length: int) -> Sequence[int]:
        """Read a holding register."""
        await self.connect()
        try:
            client = await self.connected_client()
            async with asyncio.timeout(self.timeout):
                res = await client.read_holding_registers(
                    address=start, count=length, device_id=self.server_id
                )
            if res.function_code >= 0x80:  # test that we are not an error
                raise OSError(
                    f"failed to read register {start} - function code: {res.function_code}"
                ) from None
        except TimeoutError:
            self.timeouts += 1
            raise OSError(f"timeout reading register {start}") from None

        return res.registers
