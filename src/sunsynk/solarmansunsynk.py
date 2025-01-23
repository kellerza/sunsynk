"""Sunsynk lib using PySolarman."""

import asyncio
import logging
from typing import Sequence
from urllib.parse import urlparse

import attrs
from pysolarmanv5 import PySolarmanV5Async  # type: ignore

from sunsynk.sunsynk import Sunsynk

_LOGGER = logging.getLogger(__name__)


RETRY_ATTEMPTS = 5


@attrs.define
class SolarmanSunsynk(Sunsynk):
    """Sunsynk class using PySolarmanV5."""

    client: PySolarmanV5Async = None
    dongle_serial_number: int = attrs.field(kw_only=True)

    @dongle_serial_number.validator
    def check_serial(self, _: attrs.Attribute, value: str) -> None:
        """Check if the dongle serial number is valid."""
        _LOGGER.debug("DBG: check_serial: %s %s", _, value)
        try:
            if int(value) == 0:
                raise ValueError("DONGLE_SERIAL_NUMBER not set")
        except ValueError as err:
            raise ValueError(
                f"DONGLE_SERIAL_NUMBER must be an integer, got '{value}'"
            ) from err

    async def connect(self) -> None:
        """Connect."""
        if self.client:
            return
        url = urlparse(f"{self.port}")
        self.allow_gap = 10
        self.client = PySolarmanV5Async(
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
        await self.client.connect()

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
            _LOGGER.debug("DBG: write_register: %s ==> ...", [value])
            await self.connect()
            res = await self.client.write_multiple_holding_registers(
                register_addr=address, values=[value]
            )
            _LOGGER.debug("DBG: write_register: %s ==> %s", [value], res)
            return True
        except asyncio.TimeoutError:
            _LOGGER.error("timeout writing register %s=%s", address, value)
            await self.disconnect()
        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.error("Error writing register %s: %s", address, err)
            await self.disconnect()

        self.timeouts += 1
        return False

    async def read_holding_registers(self, start: int, length: int) -> Sequence[int]:
        """Read a holding register."""
        attempt = 0
        while True:
            try:
                await self.connect()
                return await self.client.read_holding_registers(start, length)
            except Exception as err:  # pylint: disable=broad-except
                attempt += 1
                _LOGGER.error("Error reading: %s (retry %s)", err, attempt)
                await self.disconnect()
                if attempt >= RETRY_ATTEMPTS:
                    raise IOError(f"Failed to read register {start}") from err
                await asyncio.sleep(2)
