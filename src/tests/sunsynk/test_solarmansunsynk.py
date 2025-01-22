"""Solarman Sunsynk"""

import asyncio
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
    def read_holding_registers_side_effect(
        *args: tuple, **kwargs: dict[str, Any]
    ) -> MagicMock:
        sequence_number = kwargs.get("sequence_number", 0)
        if not isinstance(sequence_number, int):
            sequence_number = 0
        # Create the Modbus frame first (without CRC)
        modbus_frame = bytes(
            [
                1,  # Slave ID
                3,  # Function code
                4,  # Data length
                0,
                1,  # First register
                0,
                2,  # Second register
            ]
        )
        # Calculate CRC for the Modbus frame
        crc = calculate_modbus_crc(modbus_frame)
        # Create complete Modbus frame with CRC
        modbus_frame_with_crc = modbus_frame + bytes(
            [
                crc & 0xFF,  # CRC low byte
                crc >> 8,  # CRC high byte
            ]
        )

        _LOGGER.debug("Modbus frame: %s", " ".join(f"{b:02x}" for b in modbus_frame))
        _LOGGER.debug("Calculated CRC: %04x", crc)
        _LOGGER.debug(
            "Complete Modbus frame: %s",
            " ".join(f"{b:02x}" for b in modbus_frame_with_crc),
        )

        # Create complete response with V5 packet framing
        mock_response.raw_response = (
            bytes(
                [
                    0xA5,  # Start byte
                    0x00,  # Ver
                    0x00,  # Slave address
                    0x00,  # Control code
                    0x00,  # Function code
                    sequence_number,  # Sequence number (now guaranteed to be an int)
                    0x00,
                    0x00,  # Data length
                    0x00,
                    0x00,  # Source address
                    0x00,
                    0x00,  # Destination address
                ]
            )
            + modbus_frame_with_crc
            + bytes(
                [
                    0x15  # End byte
                ]
            )
        )

        _LOGGER.debug(
            "Complete V5 packet: %s",
            " ".join(f"{b:02x}" for b in mock_response.raw_response),
        )

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


@pytest.mark.asyncio
async def test_validate_packet_invalid_start_stop() -> None:
    """Test packet validation with invalid start/stop bytes."""
    ss = SolarmanSunsynk(port="tcp://127.0.0.1:502", dongle_serial_number=101)
    
    # Test invalid start byte
    invalid_packet = bytes([0x00]) + bytes([0] * 20) + bytes([0x15])
    assert not ss.validate_packet(invalid_packet, 2)
    
    # Test invalid end byte
    invalid_packet = bytes([0xA5]) + bytes([0] * 20) + bytes([0x00])
    assert not ss.validate_packet(invalid_packet, 2)


@pytest.mark.asyncio
async def test_validate_packet_invalid_sequence() -> None:
    """Test packet validation with invalid sequence number."""
    ss = SolarmanSunsynk(port="tcp://127.0.0.1:502", dongle_serial_number=101)
    ss.current_sequence_number = 0x42
    
    # Create packet with wrong sequence number
    invalid_packet = bytes([0xA5, 0, 0, 0, 0, 0x43]) + bytes([0] * 15) + bytes([0x15])
    assert not ss.validate_packet(invalid_packet, 2)


@pytest.mark.asyncio
async def test_validate_packet_invalid_crc() -> None:
    """Test packet validation with invalid CRC."""
    ss = SolarmanSunsynk(port="tcp://127.0.0.1:502", dongle_serial_number=101)
    ss.current_sequence_number = 0x42
    
    # Create packet with invalid CRC
    modbus_frame = bytes([1, 3, 4, 0, 1, 0, 2, 0, 0])  # Invalid CRC at end
    packet = bytes([0xA5, 0, 0, 0, 0, 0x42]) + bytes([0] * 6) + modbus_frame + bytes([0x15])
    assert not ss.validate_packet(packet, 2)


@pytest.mark.asyncio
async def test_validate_packet_invalid_length() -> None:
    """Test packet validation with wrong number of registers."""
    ss = SolarmanSunsynk(port="tcp://127.0.0.1:502", dongle_serial_number=101)
    ss.current_sequence_number = 0x42
    
    # Create valid Modbus frame but request wrong length
    modbus_frame = bytes([1, 3, 4, 0, 1, 0, 2])
    crc = calculate_modbus_crc(modbus_frame)
    modbus_frame_with_crc = modbus_frame + bytes([crc & 0xFF, crc >> 8])
    packet = bytes([0xA5, 0, 0, 0, 0, 0x42]) + bytes([0] * 6) + modbus_frame_with_crc + bytes([0x15])
    
    # Test with wrong expected length
    assert not ss.validate_packet(packet, 3)  # Expect 3 registers but only 2 in frame


@pytest.mark.asyncio
@patch("sunsynk.solarmansunsynk.PySolarmanV5Async")
async def test_connect_disconnect(mock_pysolarman: AsyncMock) -> None:
    """Test connection and disconnection scenarios."""
    ss = SolarmanSunsynk(port="tcp://127.0.0.1:502", dongle_serial_number=101)
    
    # Test connect when already connected
    ss.client = AsyncMock()
    await ss.connect()
    assert not mock_pysolarman.called
    
    # Test disconnect when not connected
    ss.client = None
    await ss.disconnect()
    
    # Test disconnect with AttributeError
    mock_client = AsyncMock()
    mock_client.disconnect.side_effect = AttributeError()
    ss.client = mock_client
    await ss.disconnect()
    assert ss.client is None


@pytest.mark.asyncio
async def test_write_register_errors() -> None:
    """Test write_register error handling."""
    ss = SolarmanSunsynk(port="tcp://127.0.0.1:502", dongle_serial_number=101)
    mock_client = AsyncMock()
    ss.client = mock_client
    
    # Test timeout error
    mock_client.write_multiple_holding_registers.side_effect = asyncio.TimeoutError()
    result = await ss.write_register(address=1, value=2)
    assert not result
    assert ss.timeouts == 1
    
    # Test general exception
    mock_client.write_multiple_holding_registers.side_effect = Exception("Test error")
    result = await ss.write_register(address=1, value=2)
    assert not result
    assert ss.timeouts == 2
