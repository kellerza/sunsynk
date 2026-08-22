"""Connection URL helpers and Sunsynk.from_url."""

import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from modbus_connection import (
    GatewayTargetError,
    ModbusSerialParams,
    ModbusTcpParams,
    ModbusUdpParams,
)
from modbus_connection.mock import MockModbusConnection

from sunsynk.connection import DEFAULT_MESSAGE_SPACING, open_connection, url_to_params
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
    with pytest.raises(NotImplementedError, match="pymodbus-"):
        url_to_params("serial-udp://host:502")
    with pytest.raises(NotImplementedError, match="Unknown scheme"):
        url_to_params("xcp://localhost:10")


def test_url_to_params_serial_udp_with_allow() -> None:
    """serial-udp maps to RTU-over-UDP when allowed (pymodbus backend)."""
    assert url_to_params(
        "serial-udp://host:502", allow_serial_udp=True
    ) == ModbusUdpParams(host="host", port=502, framer="rtu")


def test_open_connection_builds_tmodbus() -> None:
    """open_connection returns a tmodbus ModbusConnection (lazy connect)."""
    from modbus_connection.tmodbus import (  # noqa: PLC0415
        ModbusConnection as TmodbusConnection,
    )

    conn = open_connection("tcp://127.0.0.1:502", timeout=5)
    assert isinstance(conn, TmodbusConnection)
    assert conn.connected is False
    unit = conn.for_unit(1)
    assert unit is not None
    assert conn._pacer._message_spacing == DEFAULT_MESSAGE_SPACING


def test_open_connection_serial_spacing() -> None:
    """Serial (and default TCP) get a 50ms gap; explicit 0 disables it."""
    serial = open_connection("/dev/ttyUSB0", timeout=5)
    assert serial._pacer._message_spacing == DEFAULT_MESSAGE_SPACING
    rtu_tcp = open_connection("serial-tcp://host:8899", timeout=5)
    assert rtu_tcp._pacer._message_spacing == DEFAULT_MESSAGE_SPACING
    no_gap = open_connection("/dev/ttyUSB0", timeout=5, message_spacing=0)
    assert no_gap._pacer._message_spacing == 0.0
    custom = open_connection("tcp://127.0.0.1:502", timeout=5, message_spacing=0.1)
    assert custom._pacer._message_spacing == 0.1


def test_open_connection_pymodbus_prefix() -> None:
    """pymodbus- prefix selects the pymodbus backend."""
    from modbus_connection.pymodbus import (  # noqa: PLC0415
        ModbusConnection as PymodbusConnection,
    )

    conn = open_connection("pymodbus-tcp://127.0.0.1:502", timeout=5)
    assert isinstance(conn, PymodbusConnection)
    assert conn._params == ModbusTcpParams(host="127.0.0.1", port=502)


def test_open_connection_pymodbus_serial_device() -> None:
    """pymodbus- on a device path opens serial params."""
    from modbus_connection.pymodbus import (  # noqa: PLC0415
        ModbusConnection as PymodbusConnection,
    )

    conn = open_connection("pymodbus-/dev/ttyUSB0", timeout=5)
    assert isinstance(conn, PymodbusConnection)
    assert conn._params == ModbusSerialParams(device="/dev/ttyUSB0", baudrate=9600)


def test_open_connection_pymodbus_serial_udp() -> None:
    """pymodbus-serial-udp enables RTU-over-UDP."""
    from modbus_connection.pymodbus import (  # noqa: PLC0415
        ModbusConnection as PymodbusConnection,
    )

    conn = open_connection("pymodbus-serial-udp://host:502", timeout=5)
    assert isinstance(conn, PymodbusConnection)
    assert conn._params == ModbusUdpParams(host="host", port=502, framer="rtu")


def test_open_connection_serial_udp_without_prefix() -> None:
    """serial-udp without pymodbus- prefix is rejected."""
    with pytest.raises(NotImplementedError, match="pymodbus-"):
        open_connection("serial-udp://host:502")


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
    """Timeouts on write increment the counter and return False after retries."""
    unit = MagicMock()
    unit.write_registers = AsyncMock(side_effect=TimeoutError)
    conn = MagicMock()
    conn.connected = True
    conn.disconnect = AsyncMock()
    ss = Sunsynk(unit=unit, state=state, connection=conn)
    assert await ss.write_register(address=1, value=1) is False
    assert ss.timeouts == ss.read_attempts
    assert unit.write_registers.await_count == ss.read_attempts
    conn.disconnect.assert_not_awaited()


async def test_read_holding_registers_timeout(state: InverterState) -> None:
    """Serial timeouts increment the counter, flush, retry, then raise ExceptionGroup."""
    unit = MagicMock()
    unit.read_holding_registers = AsyncMock(side_effect=TimeoutError)
    conn = MagicMock()
    conn.connected = True
    conn.disconnect = AsyncMock()
    conn._params = ModbusSerialParams(device="/dev/ttyUSB0")
    ss = Sunsynk(unit=unit, state=state, connection=conn)
    with pytest.raises(ExceptionGroup, match="Failed to read 1 registers at 1"):
        await ss.read_holding_registers(1, 1)
    assert ss.timeouts == ss.read_attempts
    assert unit.read_holding_registers.await_count == ss.read_attempts
    assert conn.disconnect.await_count == ss.read_attempts


async def test_read_holding_registers_timeout_tcp_does_not_flush(
    state: InverterState,
) -> None:
    """TCP timeouts still retry but leave the socket up."""
    unit = MagicMock()
    unit.read_holding_registers = AsyncMock(side_effect=TimeoutError)
    conn = MagicMock()
    conn.connected = True
    conn.disconnect = AsyncMock()
    conn._params = ModbusTcpParams(host="1.2.3.4", port=502)
    ss = Sunsynk(unit=unit, state=state, connection=conn)
    with pytest.raises(ExceptionGroup, match="Failed to read"):
        await ss.read_holding_registers(1, 1)
    assert ss.timeouts == ss.read_attempts
    conn.disconnect.assert_not_awaited()


async def test_read_holding_registers_timeout_without_connection(
    state: InverterState,
) -> None:
    """Solarman-style units have no ModbusConnection to flush."""
    unit = MagicMock()
    unit.read_holding_registers = AsyncMock(side_effect=TimeoutError)
    ss = Sunsynk(unit=unit, state=state)
    with pytest.raises(ExceptionGroup, match="Failed to read"):
        await ss.read_holding_registers(1, 1)
    assert ss.timeouts == ss.read_attempts


async def test_read_holding_registers_timeout_then_success(
    state: InverterState,
) -> None:
    """A later attempt can still succeed after a timeout flush."""
    unit = MagicMock()
    unit.read_holding_registers = AsyncMock(side_effect=[TimeoutError, [9, 8]])
    conn = MagicMock()
    conn.connected = True
    conn.disconnect = AsyncMock()
    conn._params = ModbusSerialParams(device="/dev/ttyUSB0")
    ss = Sunsynk(unit=unit, state=state, connection=conn)
    assert list(await ss.read_holding_registers(5, 2)) == [9, 8]
    assert ss.timeouts == 1
    conn.disconnect.assert_awaited_once()


async def test_read_holding_registers_one_attempt(state: InverterState) -> None:
    """read_attempts=1 raises after a single timeout."""
    unit = MagicMock()
    unit.read_holding_registers = AsyncMock(side_effect=TimeoutError)
    ss = Sunsynk(unit=unit, state=state, read_attempts=1)
    with pytest.raises(ExceptionGroup, match="Failed to read"):
        await ss.read_holding_registers(1, 1)
    assert ss.timeouts == 1
    assert unit.read_holding_registers.await_count == 1


async def test_read_holding_registers_logs_empty_timeout(
    state: InverterState,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Empty TimeoutError strings must still log the exception type."""
    unit = MagicMock()
    unit.read_holding_registers = AsyncMock(side_effect=TimeoutError())
    ss = Sunsynk(unit=unit, state=state)
    with caplog.at_level(logging.ERROR):
        with pytest.raises(ExceptionGroup):
            await ss.read_holding_registers(0, 8)
    assert "Read register 0 (count 8): TimeoutError" in caplog.text
    assert "(retry" not in caplog.text


async def test_read_holding_registers_gateway_target_flushes(
    state: InverterState,
) -> None:
    """Gateway 0x0B (target failed to respond) is a read error and still flushes."""
    unit = MagicMock()
    unit.read_holding_registers = AsyncMock(side_effect=GatewayTargetError())
    conn = MagicMock()
    conn.connected = True
    conn.disconnect = AsyncMock()
    ss = Sunsynk(unit=unit, state=state, connection=conn)
    with pytest.raises(ExceptionGroup, match="Failed to read 2 registers at 176"):
        await ss.read_holding_registers(176, 2)
    assert ss.timeouts == 0
    assert conn.disconnect.await_count == ss.read_attempts
