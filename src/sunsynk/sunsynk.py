"""Sunsync Modbus interface."""

import asyncio
import logging
import time
from collections.abc import Iterable, Sequence

import attrs

from sunsynk.helpers import hex_str, patch_bitmask
from sunsynk.rwsensors import RWSensor
from sunsynk.sensors import Sensor, ValType
from sunsynk.state import InverterState, group_sensors, register_map

_LOG = logging.getLogger(__name__)


@attrs.define(kw_only=True)
class Sunsynk:
    """Sunsync Modbus class."""

    state: InverterState = attrs.field(factory=InverterState)
    port: str = "/dev/tty0"
    baudrate: int = 9600
    server_id: int = 1
    timeout: int = 10
    read_sensors_batch_size: int = 20
    allow_gap: int = 2
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
        regs = sensor.value_to_reg(value, self.state)
        # if bitmask we should READ the register first!!!
        if sensor.bitmask:
            _LOG.debug("0 - %s", regs)
            regs = sensor.reg(*regs, msg=f"while setting value = {value}")
            _LOG.debug("1 - %s", regs)
            val1 = regs[0]
            r_r = await self.read_holding_registers(sensor.address[0], 1)
            _LOG.debug("r_r - %s", r_r)
            val0 = r_r[0]
            regs0 = patch_bitmask(val0, val1, sensor.bitmask)
            regs = (regs0, *regs[1:])
            msg = f"[Register {val0}-->{val1}]"

        _LOG.info(
            "Writing sensor %s=%s Registers:%s %s",
            sensor.id,
            value,
            hex_str(regs, address=sensor.address),
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
                _LOG.warning("sensor %s not being tracked", sen.id)

        new_regs: dict[int, int] = {}
        errs: list[Exception] = []
        groups = group_sensors(
            sensors,
            allow_gap=self.allow_gap,
            max_group_size=self.read_sensors_batch_size,
        )
        for grp in groups:
            glen = grp[-1] - grp[0] + 1
            try:
                perf = time.perf_counter()
                async with asyncio.timeout(self.timeout + 1):
                    r_r = await self.read_holding_registers(grp[0], glen)
                perf = time.perf_counter() - perf
                _LOG.debug(
                    "Time taken to fetch %s registers starting at %s : %ss",
                    glen,
                    grp[0],
                    f"{perf:.2f}",
                )
            except TimeoutError:
                errs.append(
                    TimeoutError(f"timeout reading {glen} registers from {grp[0]}")
                )
                self.timeouts += 1
                continue
            except Exception as err:
                errs.append(
                    err.__class__(
                        f"{err.__class__.__name__} reading {glen} registers from {grp[0]}: {err}"
                    )
                )
                continue

            regs = register_map(grp[0], r_r)
            new_regs.update(regs)

            if len(r_r) != glen:
                _LOG.warning("Did not complete read, only read %s/%s", len(r_r), glen)

            _LOG.debug(
                "Request registers: %s glen=%d. Response %s len=%d. regs=%s",
                grp,
                glen,
                r_r,
                len(r_r),
                regs,
            )

        self.state.update(new_regs)
        if len(errs) > 1:
            raise ExceptionGroup("Errors reading sensors", errs) from None
        if errs:
            raise errs[0] from None
