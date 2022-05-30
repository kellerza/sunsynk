"""Sunsync Modbus interface."""
import asyncio
import logging
from typing import Dict, Sequence

import attr

from sunsynk.sensor import Sensor, group_sensors, update_sensors

_LOGGER = logging.getLogger(__name__)


@attr.define
class Sunsynk:
    """Sunsync Modbus class."""

    port: str = attr.ib(default="/dev/tty0")
    baudrate: int = attr.ib(default=9600)
    server_id: int = attr.ib(default=1)
    timeout: int = attr.ib(default=10)
    read_sensors_batch_size: int = attr.field(default=60)

    async def connect(self) -> None:
        """Connect."""
        raise NotImplementedError

    async def write_register(self, *, address: int, value: int) -> bool:
        """Write to a register - Sunsynk support function code 0x10."""
        raise NotImplementedError

    async def write_sensor(self, sensor: Sensor) -> None:
        """Write a sensor."""
        await self.write_register(
            address=sensor.reg_address[0], value=sensor.reg_value[0]
        )
        for idx in range(len(sensor.reg_address) - 1):
            await asyncio.sleep(0.05)
            await self.write_register(
                address=sensor.reg_address[idx], value=sensor.reg_value[idx]
            )

    async def read_holding_registers(self, start: int, length: int) -> Sequence[int]:
        """Read a holding register."""
        raise NotImplementedError

    async def read_sensors(self, sensors: Sequence[Sensor]) -> None:
        """Read a list of sensors - Sunsynk supports function code 0x03."""
        all_regs: Dict[int, int] = {}
        for grp in group_sensors(
            sensors, allow_gap=1, max_group_size=self.read_sensors_batch_size
        ):
            glen = grp[-1] - grp[0] + 1

            try:
                r_r = await self.read_holding_registers(grp[0], glen)
            except Exception as err:  # pylint: disable=broad-except
                raise Exception(  # pylint: disable=raise-missing-from
                    f"({self.server_id},{grp[0]},{glen}) {err}"
                )

            # if r_r.function_code >= 0x80:  # test that we are not an error
            #    raise Exception("failed to read")
            regs = register_map(grp[0], r_r)
            all_regs.update(regs)

            if len(r_r) != glen:
                _LOGGER.warning(
                    "Did not complete read, only read %s/%s", len(r_r), glen
                )

            _LOGGER.debug(
                "Request registers: %s glen=%d. Response %s len=%d. regs=%s",
                grp,
                glen,
                r_r,
                len(r_r),
                regs,
            )

        update_sensors(sensors, all_regs)


def register_map(start: int, registers: Sequence[int]) -> Dict[int, int]:
    """Turn the registers into a dictionary or map."""
    return {start + i: r for (i, r) in enumerate(registers)}
