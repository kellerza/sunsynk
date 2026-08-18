"""Sunsync Modbus interface."""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from typing import Protocol, cast, runtime_checkable

from modbus_connection import ModbusTimeoutError
from modbus_connection.tmodbus import ModbusConnection

from sunsynk.connection import open_connection
from sunsynk.helpers import hex_str, patch_bitmask
from sunsynk.rwsensors import RWSensor
from sunsynk.sensors import LOG_TRACE, Sensor, ValType
from sunsynk.state import InverterState, group_sensors, register_map

_LOG = logging.getLogger(__name__)


@runtime_checkable
class HoldingUnit(Protocol):
    """Minimal unit surface used by ``Sunsynk`` (ModbusUnit or SolarmanUnit)."""

    @property
    def connected(self) -> bool:
        """Whether the underlying link is up."""
        ...

    async def read_holding_registers(self, /, address: int, count: int) -> list[int]:
        """Read ``count`` holding registers starting at ``address`` (FC03)."""
        ...

    async def write_registers(self, /, address: int, values: list[int]) -> None:
        """Write holding registers starting at ``address`` (FC16)."""
        ...


@dataclass(kw_only=True)
class Sunsynk:
    """Sunsync inverter reached through a holding-register unit."""

    unit: HoldingUnit
    connection: ModbusConnection | None = field(default=None, repr=False)
    """Owned ``ModbusConnection`` when constructed via ``from_url``; else shared/None."""

    state: InverterState = field(default_factory=InverterState)
    port: str = ""
    baudrate: int = 9600
    timeout: int = 10
    read_sensors_batch_size: int = 20
    allow_gap: int = 2
    timeouts: int = 0

    @classmethod
    def from_url(
        cls,
        port: str,
        *,
        server_id: int = 1,
        baudrate: int = 9600,
        timeout: int = 10,
        **kwargs: object,
    ) -> Sunsynk:
        """Create a ``Sunsynk`` that owns a tmodbus connection for ``port``."""
        connection = open_connection(port, baudrate=baudrate, timeout=timeout)
        return cls(
            # ponytail: TmodbusUnit async methods type as Coroutine, Protocol wants
            # CoroutineType — same callable at runtime; cast until the stubs align.
            unit=cast(HoldingUnit, connection.for_unit(server_id)),
            connection=connection,
            port=port,
            baudrate=baudrate,
            timeout=timeout,
            **kwargs,  # type: ignore[arg-type]
        )

    async def connect(self) -> None:
        """Connect the owned link, or a unit that implements ``connect`` (Solarman)."""
        if self.connection is not None:
            try:
                await self.connection.connect()
            except ModbusTimeoutError:
                raise ConnectionError("Failed to connect: timeout") from None
            except Exception as err:
                raise ConnectionError(f"Failed to connect: {err}") from err
            return
        connect = getattr(self.unit, "connect", None)
        if connect is not None:
            await connect()

    async def _flush_modbus_connection(self) -> None:
        """Drop the tmodbus link so the next request reconnects with an empty buffer."""
        if self.connection is None or not self.connection.connected:
            return
        _LOG.debug("Flushing Modbus connection after timeout (%s)", self.port)
        await self.connection.disconnect()

    async def write_register(self, *, address: int, value: int) -> bool:
        """Write to a register - Sunsynk support function code 0x10."""
        try:
            await self.unit.write_registers(address, [value])
            return True
        except TimeoutError:
            _LOG.error("timeout writing register %s=%s", address, value)
            self.timeouts += 1
            await self._flush_modbus_connection()
        except Exception as err:
            _LOG.error("failed to write register %s=%s: %s", address, value, err)
        return False

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

        if sensor.trace:
            _LOG._log(
                LOG_TRACE,
                "Writing sensor %s=%s Registers:%s %s",
                (sensor.id, value, hex_str(regs, address=sensor.address), msg),
            )
        for idx, addr in enumerate(sensor.address):
            if idx:
                await asyncio.sleep(0.05)
            await self.write_register(address=addr, value=regs[idx])
            self.state.registers[addr] = regs[idx]

    async def read_holding_registers(self, start: int, length: int) -> Sequence[int]:
        """Read holding registers (FC03)."""
        try:
            return await self.unit.read_holding_registers(start, length)
        except TimeoutError:
            self.timeouts += 1
            await self._flush_modbus_connection()
            raise OSError(f"timeout reading register {start}") from None

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
                r_r = await self.read_holding_registers(grp[0], glen)
                perf = time.perf_counter() - perf
                _LOG.debug(
                    "Time taken to fetch %s registers starting at %s : %ss",
                    glen,
                    grp[0],
                    f"{perf:.2f}",
                )
            except Exception as err:
                errs.append(
                    Exception(
                        f"{err.__class__.__name__} reading {glen} registers from {grp[0]}: {err}"
                    )
                )
                continue

            if len(r_r) != glen:
                errs.append(
                    OSError(
                        f"response length mismatch reading {glen} registers from "
                        f"{grp[0]}: got {len(r_r)}"
                    )
                )
                continue

            regs = register_map(grp[0], r_r)
            new_regs.update(regs)

            _LOG.debug(
                "Request registers: %s glen=%d. Response %s len=%d. regs=%s",
                grp,
                glen,
                r_r,
                len(r_r),
                regs,
            )

        self.state.update(new_regs)
        if errs:
            raise ExceptionGroup("Errors reading sensors", errs) from None
