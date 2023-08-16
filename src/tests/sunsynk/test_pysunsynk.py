"""PyModbus."""
import asyncio
from unittest.mock import AsyncMock, MagicMock, PropertyMock, call, patch

import pytest

from sunsynk.pysunsynk import ModbusRtuFramer, PySunsynk
from sunsynk.state import InverterState


@pytest.mark.asyncio
async def test_pyss() -> None:
    ss = PySunsynk()
    with pytest.raises(ConnectionError):
        await ss.connect()

    ss.client = None  # type: ignore
    with pytest.raises(NotImplementedError):
        ss.port = "xcp://localhost:10"
        await ss.connect()

    with patch("sunsynk.pysunsynk.AsyncModbusTcpClient") as client:
        client.return_value = MagicMock()
        ss.port = "serial-tcp://localhost:10"
        assert client.call_args_list == []
        await ss.connect()
        assert client.call_args_list == [
            call(host="localhost", port=10, framer=ModbusRtuFramer)
        ]
        assert ss.client is not None


P_ASYNC_CONNECTED = "sunsynk.pysunsynk.AsyncModbusTcpClient.connected"
P_CONNECT = "sunsynk.pysunsynk.AsyncModbusTcpClient.connect"
P_READ_HR = "sunsynk.pysunsynk.AsyncModbusTcpClient.read_holding_registers"
P_WRITE_REGS = "sunsynk.pysunsynk.AsyncModbusTcpClient.write_registers"


@pytest.mark.asyncio
@patch(P_ASYNC_CONNECTED, new_callable=PropertyMock)
@patch(P_CONNECT, new_callable=AsyncMock)
async def test_ss_tcp_connect(
    connect: AsyncMock,
    async_connect: PropertyMock,
    state: InverterState,
) -> None:
    ss = PySunsynk(port="tcp://1.1.1.1")
    ss.state = state

    # Connect raises an exception
    async_connect.side_effect = [0]
    connect.side_effect = TypeError
    with pytest.raises(TypeError):
        await ss.connect()

    # Connect fails
    async_connect.side_effect = [0, 0]
    connect.side_effect = None
    with pytest.raises(ConnectionError):
        await ss.connect()

    # Ensure we can connect
    async_connect.side_effect = [0, 1, 888]
    connect.side_effect = None
    await ss.connect()
    assert ss.client.connected == 888


@pytest.mark.asyncio
@patch(P_ASYNC_CONNECTED, new_callable=PropertyMock)
@patch(P_CONNECT, new_callable=AsyncMock)
@patch(P_READ_HR, new_callable=AsyncMock)
async def test_ss_tcp_read(
    read_holding_reg: AsyncMock,
    _connect: AsyncMock,
    async_connect: PropertyMock,
    state: InverterState,
) -> None:
    ss = PySunsynk(port="tcp://1.1.1.1")
    ss.state = state

    # Ensure we can read
    async_connect.return_value = 1

    # The return value from client.read_holding_registers
    read_holding_reg.return_value = rhr = MagicMock()
    rhr.function_code = 0
    rhr.registers = [1, 2, 3, 4, 5]
    z = await ss.read_holding_registers(5, 5)
    assert z == [1, 2, 3, 4, 5]

    # some error during read
    rhr.function_code = 0x100
    with pytest.raises(IOError):
        await ss.read_holding_registers(5, 5)

    # Write!
    # await ss.write_register(address=1, value=1)
    # assert "xXx" not in caplog.text


@pytest.mark.asyncio
@patch(P_ASYNC_CONNECTED, new_callable=PropertyMock)
@patch(P_CONNECT, new_callable=AsyncMock)
@patch(P_WRITE_REGS, new_callable=AsyncMock)
async def test_ss_tcp_write(
    write_registers: AsyncMock,
    _connect: AsyncMock,
    async_connect: PropertyMock,
    state: InverterState,
    caplog: pytest.LogCaptureFixture,
) -> None:
    ss = PySunsynk(port="tcp://1.1.1.1")
    ss.state = state

    # Ensure we can write
    async_connect.return_value = 1

    # The return value from client.read_holding_registers
    write_registers.return_value = wrr = MagicMock()
    wrr.function_code = 0
    res = await ss.write_register(address=1, value=1)
    assert res is True

    # some error during read
    wrr.function_code = 0x100
    assert "failed" not in caplog.text
    res = await ss.write_register(address=1, value=1)
    assert res is False
    assert "failed" in caplog.text

    # Timeout
    write_registers.return_value = None
    write_registers.side_effect = asyncio.TimeoutError
    assert "timeout writing" not in caplog.text
    res = await ss.write_register(address=1, value=1)
    assert res is False
    assert "timeout writing" in caplog.text


@pytest.mark.asyncio
@patch("sunsynk.pysunsynk.AsyncModbusSerialClient", async_connected=PropertyMock)
async def test_ss_serial(serialc: MagicMock, state: InverterState) -> None:
    ss = PySunsynk(port="/dev/tty0")
    ss.state = state

    serialc.side_effect = TypeError
    with pytest.raises(TypeError):
        await ss.connect()

    serialc.side_effect = None
    await ss.connect()
