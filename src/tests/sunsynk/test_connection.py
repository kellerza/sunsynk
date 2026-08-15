"""Connection URL helpers and Sunsynk.from_url."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from modbus_connection import ModbusSerialParams, ModbusTcpParams, ModbusUdpParams
from modbus_connection.mock import MockModbusConnection

from sunsynk.connection import open_connection, url_to_params
from sunsynk.state import InverterState
from sunsynk.sunsynk import Sunsynk


def test_url_to_params() -> None:
    """Port schemes map to the expected params."""
    assert url_to_params("tcp://1.2.3.4:502") == ModbusTcpParams(
        host="1.2.3.4", port=502
    )
    assert url_to_params("serial-tcp://host:8899") == ModbusTcpParams(
        host="host", port=8899, framer="rtu"
    )
    assert url_to_params("udp://host:502") == ModbusUdpParams(host="host", port=502)
    assert url_to_params("/dev/ttyUSB0", baudrate=19200) == ModbusSerialParams(
        device="/dev/ttyUSB0", baudrate=19200
    )
    with pytest.raises(NotImplementedError, match="serial-udp"):
        url_to_params("serial-udp://host:502")
    with pytest.raises(NotImplementedError, match="Unknown scheme"):
        url_to_params("xcp://localhost:10")


def test_open_connection_builds_tmodbus() -> None:
    """open_connection returns a tmodbus ModbusConnection (lazy connect)."""
    conn = open_connection("tcp://127.0.0.1:502", timeout=5)
    assert conn.connected is False
    unit = conn.for_unit(1)
    assert unit is not None


async def test_from_url_mock_unit(state: InverterState) -> None:
    """Sunsynk.from_url owns a connection; I/O goes through the unit."""
    conn = MockModbusConnection()
    unit = conn.for_unit(1)
    unit.holding[5] = 11
    unit.holding[6] = 22
    unit.holding[7] = 33
    unit.holding[8] = 44
    unit.holding[9] = 55

    with patch("sunsynk.sunsynk.open_connection", return_value=conn):
        ss = Sunsynk.from_url("tcp://1.1.1.1:502", server_id=1, timeout=5)
    ss.state = state
    assert ss.connection is conn

    await ss.connect()
    assert conn.connected

    assert list(await ss.read_holding_registers(5, 5)) == [11, 22, 33, 44, 55]
    assert await ss.write_register(address=5, value=99) is True
    assert unit.holding[5] == 99


async def test_write_register_timeout(state: InverterState) -> None:
    """Timeouts on write increment the counter and return False."""
    unit = MagicMock()
    unit.write_registers = AsyncMock(side_effect=TimeoutError)
    ss = Sunsynk(unit=unit, state=state)
    assert await ss.write_register(address=1, value=1) is False
    assert ss.timeouts == 1


async def test_read_holding_registers_timeout(state: InverterState) -> None:
    """Timeouts on read increment the counter and raise OSError."""
    unit = MagicMock()
    unit.read_holding_registers = AsyncMock(side_effect=TimeoutError)
    ss = Sunsynk(unit=unit, state=state)
    with pytest.raises(OSError, match="timeout reading"):
        await ss.read_holding_registers(1, 1)
    assert ss.timeouts == 1
