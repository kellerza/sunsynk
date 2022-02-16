"""Sunsynk lib using umodbus."""
import logging
from typing import Sequence

import attr
from async_modbus import AsyncClient, modbus_for_url

from sunsynk import Sensor, Sunsynk, group_sensors, update_sensors
from sunsynk.sunsynk import register_map

_LOGGER = logging.getLogger(__name__)


class uSunsynk(Sunsynk):

    client: AsyncClient = attr.ib(default=None)

    async def connect(self, timeout: int = 5) -> None:
        """Connect."""
        _LOGGER.info("Connecting to %s", self.port)
        self.client = modbus_for_url(self.port)

    async def write(self, *, address: int, value: int) -> None:
        """Write to a register."""

        pass

    async def read(self, sensors: Sequence[Sensor]) -> None:
        """Read a list of sensors."""
        for grp in group_sensors(sensors):
            glen = grp[-1] - grp[0] + 1
            r_r = await self.client.read_holding_registers(
                starting_address=grp[0],
                quantity=glen,
                slave_id=self.unit_id,
            )
            # if r_r.function_code >= 0x80:  # test that we are not an error
            #    raise Exception("failed to read")
            regs = register_map(grp[0], r_r)

            _LOGGER.debug(
                "Request registers: %s glen=%d. Response %s len=%d. regs=%s",
                grp,
                glen,
                r_r,
                len(r_r),
                regs,
            )

            update_sensors(sensors, regs)
