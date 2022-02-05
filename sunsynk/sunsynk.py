"""Sunsync Modbus interface."""
import asyncio
import logging
from typing import Dict, Sequence
from urllib.parse import urlparse

import attr
from pymodbus.client.asynchronous.async_io import (  # type: ignore
    AsyncioModbusSerialClient,
    AsyncioModbusTcpClient,
    ModbusClientProtocol,
)

# from pymodbus.client.asynchronous import schedulers  # type: ignore
from pymodbus.client.asynchronous.serial import AsyncModbusSerialClient  # type: ignore
from serial.serialutil import STOPBITS_ONE  # type: ignore

from .sensor import Sensor, group_sensors, update_sensors

_LOGGER = logging.getLogger(__name__)


@attr.s(slots=True)
class Sunsynk:
    """Sunsync Modbus class."""

    port: str = attr.ib(default="/dev/tty0")
    baudrate: int = attr.ib(default=9600)
    unit_id: int = attr.ib(default=1)  # The modbus unit this request is targeting
    client: ModbusClientProtocol = attr.ib(default=None)

    async def connect(self, timeout: int = 5) -> None:
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
            client.protocol._timeout = timeout
        except AttributeError as err:
            _LOGGER.warning("%s", err)

        self.client = client.protocol

    async def write(self, *, address: int, value: int) -> None:
        """Write to a register."""
        w_r = await self.client.write_registers(
            address=address, values=(value,), unit=self.unit_id
        )
        if w_r.function_code >= 0x80:  # test that we are not an error
            raise ConnectionError("failed to write")

    async def read(self, sensors: Sequence[Sensor]) -> None:
        """Read a list of sensors."""
        for grp in group_sensors(sensors):
            glen = grp[-1] - grp[0] + 1
            r_r = await self.client.read_holding_registers(
                grp[0], glen, unit=self.unit_id
            )
            if r_r.function_code >= 0x80:  # test that we are not an error
                raise Exception("failed to read")
            regs = register_map(grp[0], r_r.registers)

            _LOGGER.debug(
                "Request registers: %s glen=%d. Response %s len=%d. regs=%s",
                grp,
                glen,
                r_r.registers,
                len(r_r.registers),
                regs,
            )

            update_sensors(sensors, regs)


def register_map(start: int, registers: Sequence[int]) -> Dict[int, int]:
    """Turn the registers into a dictionary or map."""
    return {start + i: r for (i, r) in enumerate(registers)}
