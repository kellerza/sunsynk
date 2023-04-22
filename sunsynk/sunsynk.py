"""Sunsync Modbus interface."""
import asyncio
import logging
from typing import Iterable, Sequence

import attrs

from sunsynk.helpers import patch_bitmask
from sunsynk.rwsensors import RWSensor
from sunsynk.sensors import Sensor, ValType
from sunsynk.state import InverterState, group_sensors, register_map

_LOGGER = logging.getLogger(__name__)


@attrs.define
class Sunsynk:
    """Sunsync Modbus class."""

    state: InverterState = attrs.field(factory=InverterState)
    port: str = attrs.field(default="/dev/tty0")
    baudrate: int = attrs.field(default=9600)
    server_id: int = attrs.field(default=1)
    timeout: int = attrs.field(default=10)
    read_sensors_batch_size: int = attrs.field(default=60)
    timeouts: int = 0

    async def connect(self) -> None:
        """Connect."""
        raise NotImplementedError

    async def write_register(self, *, address: int, value: int) -> bool:
        """Write to a register - Sunsynk support function code 0x10."""
        raise NotImplementedError

    async def write_sensor(
        self, sensor: RWSensor, value: ValType, *, msg: str = ""
    ) -> None:
        """Write a sensor."""
        regs = sensor.value_to_reg(value, self.state.get)
        # if bitmask we should READ the register first!!!
        if sensor.bitmask:
            _LOGGER.debug("0 - %s", regs)
            regs = sensor.reg(*regs, msg=f"while setting value = {value}")
            _LOGGER.debug("1 - %s", regs)
            val1 = regs[0]
            r_r = await self.read_holding_registers(sensor.address[0], 1)
            _LOGGER.debug("r_r - %s", r_r)
            val0 = r_r[0]
            regs0 = patch_bitmask(val0, val1, sensor.bitmask)
            regs = (regs0,) + regs[1:]
            msg = f"[Register {val0}-->{val1}]"

        _LOGGER.critical(
            "Writing sensor %s=%s [%s=%s] %s",
            sensor.id,
            value,
            sensor.address,
            regs,
            msg,
        )
        for idx, addr in enumerate(sensor.address):
            if idx:
                await asyncio.sleep(0.05)
            await self.write_register(address=addr, value=regs[idx])
            self.state.registers[addr] = regs[idx]

    async def read_holding_registers(self, start: int, length: int) -> Sequence[int]:
        """Read a holding register."""
        raise NotImplementedError

    async def read_sensors(self, sensors: Iterable[Sensor]) -> None:
        """Read a list of sensors - Sunsynk supports function code 0x03."""
        # Check if state is ok & tracking the sensors being read
        assert self.state is not None
        for sen in sensors:
            if sen not in self.state.values:
                _LOGGER.warning("sensor %s not being tracked", sen.id)

        new_regs: dict[int, int] = {}
        for grp in group_sensors(
            sensors, allow_gap=1, max_group_size=self.read_sensors_batch_size
        ):
            glen = grp[-1] - grp[0] + 1
            try:
                r_r = await asyncio.wait_for(
                    self.read_holding_registers(grp[0], glen), timeout=self.timeout + 1
                )
            except asyncio.TimeoutError:
                _LOGGER.error("timeout reading register %s (%s)", grp[0], glen)
                self.timeouts += 1
                raise
            except Exception as err:  # pylint: disable=broad-except
                raise Exception(  # pylint: disable=raise-missing-from,broad-exception-raised
                    f"({self.server_id},{grp[0]},{glen}) {err}"
                )

            regs = register_map(grp[0], r_r)
            new_regs.update(regs)

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

        self.state.update(new_regs)
