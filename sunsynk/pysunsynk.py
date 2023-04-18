"""Sunsync Modbus interface."""
import asyncio
import logging
from typing import Sequence
from urllib.parse import urlparse

import attr
from pymodbus import version
from pymodbus.client import (
    AsyncModbusSerialClient,
    AsyncModbusTcpClient,
    ModbusBaseClient,
)

from sunsynk.sunsynk import Sunsynk

_LOGGER = logging.getLogger(__name__)


@attr.define
class pySunsynk(Sunsynk):  # pylint: disable=invalid-name
    """Sunsync Modbus class."""

    port: str = attr.ib(default="/dev/tty0")
    client: ModbusBaseClient = attr.ib(default=None)

    async def connect(self) -> None:
        """Connect.

        https://pymodbus.readthedocs.io/en/latest/source/example/async_asyncio_serial_client.html

        """
        if self.client and self.client.async_connected:
            return
        url = urlparse(f"{self.port}")

        if not url.netloc:
            # Cannot run from a coroutine currently
            # https://github.com/riptideio/pymodbus/pull/658/files#r718775308
            _LOGGER.debug("Port: %s pymodbus %s", self.port, version.short())

            self.client = AsyncModbusSerialClient(
                port=self.port,
                baudrate=self.baudrate,
                # method="rtu",
                stopbits=1,
                bytesize=8,
            )
            # _loop, client = msc  # pylint: disable=unpacking-non-sequence

            # Alternative interim...
            # client = AsyncioModbusSerialClient(
            #     port=self.port,
            #     protocol_class=ModbusClientProtocol,
            #     framer=AsyncModbusSerialClient._framer(method="rtu"),
            #     loop=asyncio.get_running_loop(),
            #     baudrate=self.baudrate,
            #     stopbits=STOPBITS_ONE,
            #     bytesize=8,
            # )
        else:
            _LOGGER.debug(
                "Host: %s : %s pymodbus %s", url.hostname, url.port, version.short()
            )
            self.client = AsyncModbusTcpClient(
                host=url.hostname,
                port=url.port or 502,
                # protocol_class=ModbusClientProtocol,
                # loop=asyncio.get_running_loop(),
            )

        await self.client.connect()

        if not self.client.async_connected:
            raise ConnectionError

        # try:
        #     client.protocol._timeout = self.timeout
        # except AttributeError as err:
        #     _LOGGER.warning("%s", err)

        # self.client = client. .protocol

    async def write_register(self, *, address: int, value: int) -> bool:
        """Write to a register - Sunsynk supports modbus function 0x10."""
        try:
            w_r = await self.client.write_registers(
                address=address, values=(value,), slave=self.server_id
            )
            if w_r.function_code < 0x80:  # test that we are not an error
                return True
            _LOGGER.error("failed to write register %s=%s", address, value)
        except asyncio.TimeoutError:
            _LOGGER.error("timeout writing register %s=%s", address, value)
        self.timeouts += 1
        return False

    async def read_holding_registers(self, start: int, length: int) -> Sequence[int]:
        """Read a holding register."""
        res = await self.client.read_holding_registers(
            address=start, count=length, slave=self.server_id
        )
        if res.function_code >= 0x80:  # test that we are not an error
            raise Exception(  # pylint: disable=broad-exception-raised
                f"failed to read register {start} - function code: {res.function_code}"
            )
        return res.registers
