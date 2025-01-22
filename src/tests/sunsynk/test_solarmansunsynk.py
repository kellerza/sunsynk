"""Solarman Sunsynk"""

import logging
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from sunsynk.solarmansunsynk import POLY, SolarmanSunsynk

_LOGGER = logging.getLogger(__name__)


def calculate_modbus_crc(frame: bytes) -> int:
    """Calculate Modbus CRC for a frame."""
    crc = 0xFFFF
    for pos in range(len(frame)):
        crc ^= frame[pos]
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ POLY
            else:
                crc >>= 1
    return crc


@pytest.mark.asyncio
@patch("sunsynk.solarmansunsynk.SolarmanSunsynk.connect")
@patch("sunsynk.solarmansunsynk.SolarmanSunsynk.disconnect")
async def test_uss_sensor(mock_disconnect: AsyncMock, mock_connect: AsyncMock) -> None:
    ss = SolarmanSunsynk(port="tcp://127.0.0.1:502", dongle_serial_number=101)

    # Create a mock client with the required methods
    mock_client = AsyncMock()
    mock_response = MagicMock()

    # Set up the client before any operations
    ss.client = mock_client

    # Test read_holding_registers
    assert not mock_client.read_holding_registers.called

    # The sequence number will be set by advance_sequence_number()
    # We'll capture it when read_holding_registers is called
    def read_holding_registers_side_effect(*args: tuple, **kwargs: dict[str, Any]) -> MagicMock:
        sequence_number = kwargs.get('sequence_number', 0)
        if not isinstance(sequence_number, int):
            sequence_number = 0
        # Create the Modbus frame first (without CRC)
        modbus_frame = bytes([
            1,                 # Slave ID
            3,                 # Function code
            4,                 # Data length
            0, 1,             # First register
            0, 2,             # Second register
        ])
        # Calculate CRC for the Modbus frame
        crc = calculate_modbus_crc(modbus_frame)
        # Create complete Modbus frame with CRC
        modbus_frame_with_crc = modbus_frame + bytes([
            crc & 0xFF,        # CRC low byte
            crc >> 8,          # CRC high byte
        ])

        _LOGGER.debug("Modbus frame: %s", " ".join(f"{b:02x}" for b in modbus_frame))
        _LOGGER.debug("Calculated CRC: %04x", crc)
        _LOGGER.debug("Complete Modbus frame: %s", " ".join(f"{b:02x}" for b in modbus_frame_with_crc))

        # Create complete response with V5 packet framing
        mock_response.raw_response = bytes([
            0xa5,             # Start byte
            0x00,             # Ver
            0x00,             # Slave address
            0x00,             # Control code
            0x00,             # Function code
            sequence_number,  # Sequence number (now guaranteed to be an int)
            0x00, 0x00,      # Data length
            0x00, 0x00,      # Source address
            0x00, 0x00,      # Destination address
        ]) + modbus_frame_with_crc + bytes([
            0x15              # End byte
        ])

        _LOGGER.debug("Complete V5 packet: %s", " ".join(f"{b:02x}" for b in mock_response.raw_response))

        mock_response.registers = [1, 2]
        return mock_response

    mock_client.read_holding_registers.side_effect = read_holding_registers_side_effect

    result = await ss.read_holding_registers(1, 2)
    assert mock_client.read_holding_registers.called
    assert result == [1, 2]

    # Test write_register
    assert not mock_client.write_multiple_holding_registers.called
    await ss.write_register(address=1, value=2)
    assert mock_client.write_multiple_holding_registers.called
