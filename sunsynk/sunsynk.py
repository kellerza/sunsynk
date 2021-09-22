"""Sunsync Modbus interface."""
import asyncio
import logging
from typing import Sequence

import attr
from pymodbus.client.asynchronous import schedulers  # type: ignore
from pymodbus.client.asynchronous.serial import AsyncModbusSerialClient  # type: ignore
from serial.serialutil import STOPBITS_ONE  # type: ignore

from .sensor import Sensor, group_sensors, update_sensors

_LOGGER = logging.getLogger(__name__)


@attr.s(slots=True)
class Sunsynk:
    """Sunsync Modbus class."""

    port: str = attr.ib(default="/dev/tty0")
    baudrate: int = attr.ib(default=9600)
    address: int = attr.ib(default=1)
    client: AsyncModbusSerialClient = attr.ib(default=None)

    def connect(self) -> asyncio.AbstractEventLoop:
        """Connect.

        https://pymodbus.readthedocs.io/en/latest/source/example/async_asyncio_serial_client.html

        """
        msc = AsyncModbusSerialClient(
            schedulers.ASYNC_IO,
            port=self.port,
            baudrate=self.baudrate,
            method="rtu",
            stopbits=STOPBITS_ONE,
            bytesize=8,
        )
        loop, client = msc  # pylint: disable=unpacking-non-sequence

        self.client = client.protocol
        return loop

    async def write(self, sensor: Sensor) -> None:
        """Read a list of sensors."""
        w_r = await self.client.write_register(
            sensor.register, sensor.value, unit=self.address
        )
        if w_r.function_code >= 0x80:  # test that we are not an error
            raise Exception("failed to write")

    async def read(self, sensors: Sequence[Sensor]) -> None:
        """Read a list of sensors."""
        for grp in group_sensors(sensors):
            glen = grp[-1] - grp[0] + 1
            r_r = await self.client.read_holding_registers(
                grp[0], glen, unit=self.address
            )
            if r_r.function_code >= 0x80:  # test that we are not an error
                raise Exception("failed to read")
            regs = {grp[0] + i: r for (i, r) in enumerate(r_r.registers)}

            _LOGGER.debug(
                "Request registers: %s glen=%d. Response %s len=%d. regs=%s",
                grp,
                glen,
                r_r.registers,
                len(r_r.registers),
                regs,
            )

            update_sensors(sensors, regs)
