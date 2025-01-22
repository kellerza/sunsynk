"""Sunsynk lib using PySolarman."""

import asyncio
import logging
from random import randrange
from typing import Sequence
from urllib.parse import urlparse

import attrs
from pysolarmanv5 import PySolarmanV5Async  # type: ignore

from sunsynk.sunsynk import Sunsynk

_LOGGER = logging.getLogger(__name__)


RETRY_ATTEMPTS = 5
POLY = 0xA001  # Modbus CRC polynomial


@attrs.define
class SolarmanSunsynk(Sunsynk):
    """Sunsynk class using PySolarmanV5."""

    client: PySolarmanV5Async = None
    dongle_serial_number: int = attrs.field(kw_only=True)
    current_sequence_number: int | None = attrs.field(default=None, init=False)

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

    def advance_sequence_number(self) -> None:
        """Generate and advance the sequence number for packet validation."""
        # Generate initial value randomly and increment from then forward
        if self.current_sequence_number is None:
            self.current_sequence_number = randrange(0x01, 0xFF)
        else:
            self.current_sequence_number = (self.current_sequence_number + 1) & 0xFF  # prevent overflow

    def validate_modbus_crc(self, frame: bytes) -> bool:
        """Validate Modbus CRC of a frame."""
        # Calculate CRC with all but the last 2 bytes of the frame (they contain the CRC)
        crc = 0xFFFF
        for pos in range(len(frame) - 2):
            crc ^= frame[pos]
            for _ in range(8):
                if crc & 0x0001:
                    crc = (crc >> 1) ^ POLY
                else:
                    crc >>= 1

        # Compare calculated CRC with the one in the frame
        frame_crc = (frame[-1] << 8) | frame[-2]  # CRC is little-endian in frame
        return crc == frame_crc

    def validate_packet(self, packet: bytes, length: int) -> bool:
        """Validate received packet."""
        # Does the v5 packet start and end with what we expect?
        if packet[0] != 0xa5 or packet[-1] != 0x15:
            _LOGGER.warning("unexpected v5 packet start/stop")
            return False

        # Does the response match the request?
        if packet[5] != self.current_sequence_number:
            _LOGGER.warning("response frame contains unexpected sequence number")
            return False

        # Extract the Modbus frame from the V5 packet (including CRC)
        modbus_frame = packet[12:-1]
        _LOGGER.debug("Extracted Modbus frame: %s", " ".join(f"{b:02x}" for b in modbus_frame))

        # Is the Modbus CRC correct?
        if not self.validate_modbus_crc(modbus_frame):
            _LOGGER.warning("invalid modbus crc")
            _LOGGER.debug("Frame CRC: %04x", (modbus_frame[-1] << 8) | modbus_frame[-2])
            crc = 0xFFFF
            for pos in range(len(modbus_frame) - 2):
                crc ^= modbus_frame[pos]
                for _ in range(8):
                    if crc & 0x0001:
                        crc = (crc >> 1) ^ POLY
                    else:
                        crc >>= 1
            _LOGGER.debug("Calculated CRC: %04x", crc)
            return False

        # Were the expected number of registers returned?
        actual_data_len = len(modbus_frame) - 5  # do not count slave id, function code, length or CRC bytes (2)
        if actual_data_len != length * 2:  # each register is 2 bytes
            _LOGGER.warning("unexpected number of registers found in response")
            return False

        return True

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
            self.advance_sequence_number()  # Set sequence number for this request
            res = await self.client.write_multiple_holding_registers(
                register_addr=address, values=[value], sequence_number=self.current_sequence_number
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
                self.advance_sequence_number()  # Set sequence number for this request
                response = await self.client.read_holding_registers(
                    start, length, sequence_number=self.current_sequence_number
                )
                if not self.validate_packet(response.raw_response, length):
                    raise IOError("Invalid response packet")
                return response.registers
            except Exception as err:  # pylint: disable=broad-except
                attempt += 1
                _LOGGER.error("Error reading: %s (retry %s)", err, attempt)
                await self.disconnect()
                if attempt >= RETRY_ATTEMPTS:
                    raise IOError(f"Failed to read register {start}") from err
                await asyncio.sleep(2)
