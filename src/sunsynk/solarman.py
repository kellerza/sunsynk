"""Solarman V5 tunnel as a holding-register unit."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from urllib.parse import urlparse

from pysolarmanv5 import PySolarmanV5Async  # type: ignore[import-untyped]

_LOG = logging.getLogger(__name__)


@dataclass(kw_only=True)
class SolarmanUnit:
    """Holding-register I/O over a Solarman Wi-Fi dongle (not a ModbusConnection)."""

    port: str
    """``solarman://host:8899`` address of the dongle."""

    dongle_serial_number: int
    server_id: int = 1
    timeout: int = 3
    client: PySolarmanV5Async | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        """Validate the dongle serial number."""
        raw = self.dongle_serial_number
        try:
            self.dongle_serial_number = raw if isinstance(raw, int) else int(raw)
            if self.dongle_serial_number == 0:
                raise ValueError()
        except ValueError:
            raise ValueError(
                "DONGLE_SERIAL_NUMBER must be a non-zero integer for a "
                f"solarman:// PORT (Wi-Fi dongle). Got {raw!r}"
            ) from None

    @property
    def connected(self) -> bool:
        """Whether a Solarman client is open."""
        return self.client is not None

    async def connect(self) -> None:
        """Open the Solarman client if needed."""
        await self._connected_client()

    async def disconnect(self) -> None:
        """Close the Solarman client."""
        if not self.client:
            return
        try:
            await self.client.disconnect()
        except AttributeError:
            pass
        finally:
            self.client = None

    async def _connected_client(self) -> PySolarmanV5Async:
        if self.client:
            return self.client

        url = urlparse(self.port)
        self.client = client = PySolarmanV5Async(
            address=url.hostname,
            serial=self.dongle_serial_number,
            port=url.port,
            mb_slave_id=self.server_id,
            auto_reconnect=True,
            verbose=False,
            socket_timeout=self.timeout,
            v5_error_correction=True,
            error_correction=True,  # bug?
        )
        try:
            await client.connect()
        except TimeoutError:
            self.client = None
            raise ConnectionError("Failed to connect: timeout") from None
        except Exception as err:
            self.client = None
            raise ConnectionError(f"Failed to connect: {err}") from err
        return self.client

    async def read_holding_registers(self, address: int, count: int) -> list[int]:
        """Read holding registers (FC03)."""
        try:
            client = await self._connected_client()
            return list(await client.read_holding_registers(address, count) or [])
        except TimeoutError:
            raise
        except Exception as err:
            await self.disconnect()
            raise err

    async def write_registers(self, address: int, values: list[int]) -> None:
        """Write holding registers (FC16)."""
        try:
            client = await self._connected_client()
            _LOG.debug("DBG: write_registers: %s ==> ...", values)
            res = await client.write_multiple_holding_registers(
                register_addr=address, values=values
            )
            _LOG.debug("DBG: write_registers: %s ==> %s", values, res)
        except TimeoutError:
            raise
        except Exception as err:
            await self.disconnect()
            raise err from err
