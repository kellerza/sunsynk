"""Sunsynk lib using umodbus."""
import logging
from typing import Sequence

import attr
from async_modbus import AsyncClient, modbus_for_url

from sunsynk import Sensor, Sunsynk, group_sensors, update_sensors
from sunsynk.sunsynk import register_map

_LOGGER = logging.getLogger(__name__)


class uSunsynk(Sunsynk):

    client: AsyncClient = attr.field(default=None)

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

            try:
                r_r = await self.client.read_holding_registers(
                    self.unit_id, grp[0], glen
                )
            except Exception as err:  # pylint: disable=broad-except
                raise Exception(f"({self.unit_id},{grp[0]},{glen}) {err}")

            # if r_r.function_code >= 0x80:  # test that we are not an error
            #    raise Exception("failed to read")
            regs = register_map(grp[0], r_r)

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

            update_sensors(sensors, regs)
