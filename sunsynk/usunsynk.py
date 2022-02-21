"""Sunsynk lib using umodbus."""
import asyncio
import logging
from typing import Dict, Sequence

import attr
from async_modbus import AsyncClient, modbus_for_url

from sunsynk.sensor import Sensor, group_sensors, update_sensors
from sunsynk.sunsynk import Sunsynk, register_map

_LOGGER = logging.getLogger(__name__)


@attr.define
class uSunsynk(Sunsynk):  # pylint: disable=invalid-name
    """Sunsynk class using umodbus."""

    client: AsyncClient = attr.field(default=None)

    async def connect(self, timeout: int = 5) -> None:
        """Connect."""
        _LOGGER.info("Connecting to %s", self.port)
        self.client = modbus_for_url(self.port)

    async def write_register(self, *, address: int, value: int) -> bool:
        """Write to a register - Sunsynk support function code 0x10."""
        try:
            await asyncio.wait_for(
                self.client.write_registers(
                    slave_id=self.server_id,
                    starting_address=address,
                    values=(value,),
                ),
                timeout=10,
            )
            return True
        except asyncio.TimeoutError:
            _LOGGER.critical("timeout writing register %s=%s", address, value)
        return False

    async def read(self, sensors: Sequence[Sensor]) -> None:
        """Read a list of sensors - Sunsynk supports function code 0x03."""
        all_regs: Dict[int, int] = {}
        for grp in group_sensors(sensors, allow_gap=1):
            glen = grp[-1] - grp[0] + 1

            try:
                r_r = await self.client.read_holding_registers(
                    self.server_id, grp[0], glen
                )
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
