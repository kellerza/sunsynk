"""Sunsync Modbus interface."""

import asyncio
import logging
import time
from typing import Iterable, Sequence, TypedDict, Union

import attrs

from sunsynk.helpers import hex_str, patch_bitmask
from sunsynk.rwsensors import RWSensor
from sunsynk.sensors import (
    BinarySensor,
    EnumSensor,
    InverterStateSensor,
    SDStatusSensor,
    Sensor,
    ValType,
)
from sunsynk.state import InverterState, group_sensors, register_map

_LOGGER = logging.getLogger(__name__)


class RegisterReadError(Exception):
    """Exception raised when there are errors reading registers."""


@attrs.define
class Sunsynk:
    """Sunsync Modbus class."""

    # pylint: disable=too-many-instance-attributes

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

        _LOGGER.info(
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
        # pylint: disable=too-many-locals,too-many-branches
        # Check if state is ok & tracking the sensors being read
        assert self.state is not None
        for sen in sensors:
            if sen not in self.state.values:
                _LOGGER.warning("sensor %s not being tracked", sen.id)

        # Create a map of register addresses to their corresponding sensors
        reg_to_sensor: dict[int, Union[Sensor, None]] = {}
        for sensor in sensors:
            for addr in sensor.address:
                reg_to_sensor[addr] = sensor

        new_regs: dict[int, int] = {}
        errs: list[str] = []
        groups = group_sensors(
            sensors,
            allow_gap=self.allow_gap,
            max_group_size=self.read_sensors_batch_size,
        )
        for grp in groups:
            glen = grp[-1] - grp[0] + 1
            try:
                perf = time.perf_counter()
                _LOGGER.debug("Starting read of %s registers from %s", glen, grp[0])

                r_r = await asyncio.wait_for(
                    self.read_holding_registers(grp[0], glen), timeout=self.timeout + 1
                )
                perf = time.perf_counter() - perf

                # Log performance metrics
                _LOGGER.debug(
                    "Time taken to fetch %s registers starting at %s : %ss",
                    glen,
                    grp[0],
                    f"{perf:.2f}",
                )

                # Check for potential communication issues based on timing
                if perf > self.timeout * 0.8:  # If taking more than 80% of timeout
                    _LOGGER.warning(
                        "Slow register read detected: %ss for %s registers from %s",
                        f"{perf:.2f}",
                        glen,
                        grp[0],
                    )

            except asyncio.TimeoutError:
                errs.append(f"timeout reading {glen} registers from {grp[0]}")
                self.timeouts += 1
                # Log consecutive timeouts
                if self.timeouts > 3:
                    _LOGGER.error(
                        "Multiple consecutive timeouts detected: %s. Consider checking connection.",
                        self.timeouts,
                    )
                continue
            except Exception as err:  # pylint: disable=broad-except
                errs.append(
                    f"{err.__class__.__name__} reading {glen} registers from {grp[0]}: {err}"
                )
                continue

            regs = register_map(grp[0], r_r)
            new_regs.update(regs)

            if len(r_r) != glen:
                _LOGGER.warning(
                    "Did not complete read, only read %s/%s registers. This may cause value spikes.",
                    len(r_r),
                    glen,
                )

            # Log register values for debugging
            _LOGGER.debug(
                "Request registers: %s glen=%d. Response %s len=%d. regs=%s",
                grp,
                glen,
                [hex(r) for r in r_r],  # Convert to hex for better debugging
                len(r_r),
                {
                    k: hex(v) for k, v in regs.items()
                },  # Convert to hex for better debugging
            )

            # Check for potentially invalid register values
            for reg_addr, reg_val in regs.items():
                maybe_sensor: Union[Sensor, None] = reg_to_sensor.get(reg_addr)
                if maybe_sensor is None:
                    continue

                current_sensor: Sensor = maybe_sensor
                if reg_val == 0xFFFF:
                    _LOGGER.warning(
                        "Potentially invalid register value detected: addr=%s value=0xFFFF sensor=%s",
                        reg_addr,
                        current_sensor.name,
                    )
                # Only check zeros for status/enum type sensors
                elif reg_val == 0 and any(
                    isinstance(current_sensor, t)
                    for t in (
                        BinarySensor,
                        EnumSensor,
                        InverterStateSensor,
                        SDStatusSensor,
                    )
                ):
                    _LOGGER.debug(
                        "Zero value detected in status sensor: addr=%s sensor=%s",
                        reg_addr,
                        current_sensor.name,
                    )

        if errs:
            _LOGGER.warning("Errors during sensor read: %s", ", ".join(errs))
            raise RegisterReadError(", ".join(errs))

        # Reset timeout counter if successful
        if not errs:
            self.timeouts = 0

        self.state.update(new_regs)


class SunsynkInitParameters(TypedDict):
    """Sunsynk typing parameters."""

    port: str
    server_id: int
    timeout: int
    read_sensors_batch_size: int
    allow_gap: int
