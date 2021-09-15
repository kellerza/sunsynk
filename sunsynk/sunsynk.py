"""Sunsync Modbus interface."""
from typing import Sequence

import attr
from pymodbus.client.asynchronous import schedulers
from pymodbus.client.asynchronous.serial import AsyncModbusSerialClient
from serial.serialutil import STOPBITS_ONE

from .sensor import Sensor, group_sensors, update_sensors


@attr.s(slots=True)
class Sunsynk:
    """Sunsync Modbus class."""

    port: str = attr.ib(default="/dev/tty0")
    baudrate: int = attr.ib(default=9600)
    address: int = attr.ib(default=1)
    client: AsyncModbusSerialClient = attr.ib(default=None)

    def connect(self):
        """Connect.

        https://pymodbus.readthedocs.io/en/latest/source/example/async_asyncio_serial_client.html

        """
        loop, client = AsyncModbusSerialClient(
            schedulers.ASYNC_IO,
            port=self.port,
            baudrate=self.baudrate,
            method="rtu",
            stopbits=STOPBITS_ONE,
            bytesize=8,
        )

        self.client = client.protocol
        return loop

    async def write(self, sensor: Sensor) -> None:
        """Read a list of sensors."""
        rq = await self.client.write_register(
            sensor.register, sensor.value, unit=self.address
        )
        if rq.function_code >= 0x80:  # test that we are not an error
            raise Exception("failed to write")

    async def read(self, sensors: Sequence[Sensor]) -> None:
        """Read a list of sensors."""
        for grp in group_sensors(sensors):
            rr = await self.client.read_holding_registers(
                grp[0], len(grp), unit=self.address
            )
            if rr.function_code >= 0x80:  # test that we are not an error
                raise Exception("failed to write")
            update_sensors(sensors, grp[0], rr.registers)
