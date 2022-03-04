"""Sunsync Modbus interface."""
import asyncio
import logging
from typing import Sequence
from urllib.parse import urlparse

import attr
from pymodbus.client.asynchronous.async_io import (  # type: ignore
    AsyncioModbusSerialClient,
    AsyncioModbusTcpClient,
    ModbusClientProtocol,
)

# from pymodbus.client.asynchronous import schedulers  # type: ignore
from pymodbus.client.asynchronous.serial import AsyncModbusSerialClient  # type: ignore
from serial.serialutil import STOPBITS_ONE

from sunsynk.sunsynk import Sunsynk  # type: ignore

_LOGGER = logging.getLogger(__name__)


@attr.define
class pySunsynk(Sunsynk):  # pylint: disable=invalid-name
    """Sunsync Modbus class."""

    port: str = attr.ib(default="/dev/tty0")
    client: ModbusClientProtocol = attr.ib(default=None)

    async def connect(self) -> None:
        """Connect.

        https://pymodbus.readthedocs.io/en/latest/source/example/async_asyncio_serial_client.html

        """
        # pylint: disable=protected-access
        url = urlparse(f"//{self.port}")
        client = None

        if not url.netloc:
            # Cannot run from a coroutine currently
            # https://github.com/riptideio/pymodbus/pull/658/files#r718775308

            # msc = AsyncModbusSerialClient(
            #     schedulers.ASYNC_IO,
            #     port=self.port,
            #     baudrate=self.baudrate,
            #     method="rtu",
            #     stopbits=STOPBITS_ONE,
            #     bytesize=8,
            # )
            # loop, client = msc  # pylint: disable=unpacking-non-sequence

            # Alternative interim...
            client = AsyncioModbusSerialClient(
                port=self.port,
                protocol_class=ModbusClientProtocol,
                framer=AsyncModbusSerialClient._framer(method="rtu"),
                loop=asyncio.get_running_loop(),
                baudrate=self.baudrate,
                stopbits=STOPBITS_ONE,
                bytesize=8,
            )
        else:
            client = AsyncioModbusTcpClient(
                host=url.hostname,
                port=url.port or 502,
                protocol_class=ModbusClientProtocol,
                loop=asyncio.get_running_loop(),
            )

        await client.connect()

        if (hasattr(client, "connected") and not client.connected) or (
            hasattr(client, "_connected") and not client._connected
        ):
            raise ConnectionError

        try:
            client.protocol._timeout = self.timeout
        except AttributeError as err:
            _LOGGER.warning("%s", err)

        self.client = client.protocol

    async def write_register(self, *, address: int, value: int) -> bool:
        """Write to a register."""
        w_r = await self.client.write_registers(
            address=address, values=(value,), unit=self.server_id
        )
        if w_r.function_code >= 0x80:  # test that we are not an error
            raise ConnectionError("failed to write")
        return True

    async def read_holding_registers(self, start: int, length: int) -> Sequence[int]:
        """Read a holding register."""
        res = await self.client.read_holding_registers(
            start, length, unit=self.server_id
        )
        if res.function_code >= 0x80:  # test that we are not an error
            raise Exception("failed to read")
        return res.registers
