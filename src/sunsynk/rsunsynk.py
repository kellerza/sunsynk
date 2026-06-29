"""Sunsynk lib using the Rust modbus-rs package."""

import asyncio
import logging
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlparse

import modbus_rs  # type: ignore[import-untyped, import-not-found]

from sunsynk.sunsynk import Sunsynk

_LOG = logging.getLogger(__name__)


@dataclass(kw_only=True)
class RSunsynk(Sunsynk):
    """Sunsynk class using the Rust modbus-rs package."""

    transport: Any = field(default=None, repr=False)
    client: Any = field(default=None, repr=False)
    is_async: bool = field(default=False, repr=False)

    async def connected_client(self) -> Any:
        """Get client, connect if needed."""
        if self.client is not None:
            return self.client

        url = urlparse(f"{self.port}")
        if url.scheme and url.scheme != "tcp":
            raise NotImplementedError(
                f"modbusrs supports tcp:// or a serial port, not {url.scheme!r}. "
                "Use the pymodbus driver for serial-tcp/serial-udp/udp."
            )

        try:
            if url.scheme == "tcp":
                async with asyncio.timeout(self.timeout):
                    self.transport = await modbus_rs.AsyncTcpTransport.connect(
                        url.hostname, port=url.port or 502
                    )
                self.client = self.transport.create_client(unit_id=self.server_id)
                self.is_async = True
                _LOG.info("modbus-rs tcp: %s:%s", url.hostname, url.port or 502)
            else:
                # ponytail: modbus-rs only exposes a *sync* serial transport, so open
                # and call it in a worker thread. Ceiling: a thread hop per request;
                # upgrade if the binding ever ships an async serial transport.
                self.transport, self.client = await asyncio.to_thread(self._open_serial)
                self.is_async = False
                _LOG.info("modbus-rs serial: %s", self.port)
        except TimeoutError:
            raise ConnectionError("Failed to connect: timeout") from None
        except Exception as err:
            raise ConnectionError(f"Failed to connect: {err}") from err
        return self.client

    def _open_serial(self) -> tuple[Any, Any]:
        """Open a synchronous serial (RTU) transport and client."""
        transport = modbus_rs.RtuTransport.open(self.port, baud_rate=self.baudrate)
        return transport, transport.create_client(unit_id=self.server_id)

    async def _call(self, fn: Callable[..., Any], *args: Any) -> Any:
        """Run a client method, awaiting or threading depending on the transport."""
        if self.is_async:
            return await fn(*args)
        return await asyncio.to_thread(fn, *args)

    async def connect(self) -> None:
        """Connect. Will create a new client if required."""
        await self.connected_client()

    async def disconnect(self) -> None:
        """Drop the client so the next call reconnects."""
        self.transport = self.client = None

    async def write_register(self, *, address: int, value: int) -> bool:
        """Write to a register - Sunsynk supports modbus function 0x10."""
        try:
            client = await self.connected_client()
            async with asyncio.timeout(self.timeout):
                await self._call(client.write_multiple_registers, address, [value])
            return True
        except TimeoutError:
            _LOG.error("timeout writing register %s=%s", address, value)
            self.timeouts += 1
        except Exception as err:
            _LOG.error("failed to write register %s=%s: %s", address, value, err)
        await self.disconnect()
        return False

    async def read_holding_registers(self, start: int, length: int) -> Sequence[int]:
        """Read a holding register."""
        client = await self.connected_client()
        try:
            async with asyncio.timeout(self.timeout):
                regs = await self._call(client.read_holding_registers, start, length)
        except TimeoutError:
            self.timeouts += 1
            await self.disconnect()
            raise OSError(f"timeout reading register {start}") from None
        except Exception as err:
            await self.disconnect()
            raise OSError(f"failed to read register {start}: {err}") from err
        return list(regs)
