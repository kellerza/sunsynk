"""Sunsynk lib using PySolarman."""

import asyncio
import logging
from collections.abc import Sequence
from urllib.parse import urlparse

import attrs
from pysolarmanv5 import PySolarmanV5Async  # type: ignore[]

from sunsynk.sunsynk import Sunsynk

_LOG = logging.getLogger(__name__)


RETRY_ATTEMPTS = 5


@attrs.define(kw_only=True)
class SolarmanSunsynk(Sunsynk):
    """Sunsynk class using PySolarmanV5."""

    client: PySolarmanV5Async | None = attrs.field(default=None, repr=False)
    dongle_serial_number: int = 0

    def __attrs_post_init__(self) -> None:
        """Post init."""
        self.allow_gap = self.allow_gap or 10
        try:
            self.dongle_serial_number = int(self.dongle_serial_number)
            if self.dongle_serial_number == 0:
                raise ValueError("DONGLE_SERIAL_NUMBER not set")
        except ValueError as err:
            raise ValueError(
                f"DONGLE_SERIAL_NUMBER must be an integer, got '{self.dongle_serial_number}'"
            ) from err

    async def connected_client(self) -> PySolarmanV5Async:
        """Get client, connect if needed."""
        if self.client:
            return self.client

        url = urlparse(f"{self.port}")
        self.client = client = PySolarmanV5Async(
            address=url.hostname,
            serial=int(self.dongle_serial_number),
            port=url.port,
            mb_slave_id=self.server_id,
            auto_reconnect=True,
            verbose=False,
            socket_timeout=self.timeout * 2,
            v5_error_correction=True,
            error_correction=True,  # bug?
        )
        try:
            async with asyncio.timeout(self.timeout):
                await client.connect()
        except TimeoutError:
            self.client = None
            raise ConnectionError("Failed to connect: timeout") from None
        except Exception as err:
            self.client = None
            raise ConnectionError(f"Failed to connect: {err}") from err

        return self.client

    async def connect(self) -> None:
        """Connect."""
        await self.connected_client()

    async def disconnect(self) -> None:
        """Disconnect."""
        if not self.client:
            return
        try:
            await self.client.disconnect()
        except AttributeError:
            pass
        finally:
            self.client = None

    async def write_register(self, *, address: int, value: int) -> bool:
        """Write to a register - Sunsynk supports modbus function 0x10."""
        try:
            client = await self.connected_client()
            _LOG.debug("DBG: write_register: %s ==> ...", [value])
            async with asyncio.timeout(self.timeout):
                res = await client.write_multiple_holding_registers(
                    register_addr=address, values=[value]
                )
            _LOG.debug("DBG: write_register: %s ==> %s", [value], res)
            return True
        except TimeoutError:
            _LOG.error("Timeout writing register %s=%s", address, value)
            await self.disconnect()
            self.timeouts += 1
        except Exception as err:
            _LOG.error("Error writing register %s: %s", address, err)
            await self.disconnect()

        return False

    async def read_holding_registers(self, start: int, length: int) -> Sequence[int]:
        """Read a holding register."""
        attempt = 0
        while True:
            try:
                client = await self.connected_client()
                return await client.read_holding_registers(start, length)
            except Exception as err:
                attempt += 1
                _LOG.error("Error reading: %s (retry %s)", err, attempt)
                await self.disconnect()
                if attempt >= RETRY_ATTEMPTS:
                    raise OSError(f"Failed to read register {start}") from err
                await asyncio.sleep(2)
