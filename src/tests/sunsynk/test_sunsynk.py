"""Test sunsynk library."""
import logging
from unittest.mock import MagicMock, call, patch

import pytest

# from sunsynk.definitions import serial
from sunsynk import Sunsynk
from sunsynk.rwsensors import NumberRWSensor
from sunsynk.state import InverterState

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio

_LOGGER = logging.getLogger(__name__)


async def test_ss_NotImplemented() -> None:
    ss = Sunsynk()
    with pytest.raises(NotImplementedError):
        await ss.connect()
    with pytest.raises(NotImplementedError):
        await ss.write_register(address=1, value=1)
    with pytest.raises(NotImplementedError):
        await ss.read_holding_registers(1, 1)


@patch("sunsynk.Sunsynk.read_holding_registers")
@patch("sunsynk.Sunsynk.write_register")
async def test_ss_write_sensor(
    wreg: MagicMock,
    rhr: MagicMock,
    state: InverterState,
    caplog: pytest.LogCaptureFixture,
) -> None:
    ss = Sunsynk()
    ss.state = state

    sen = NumberRWSensor((1,), "s1")
    state.track(sen)

    assert sen.value_to_reg(44, state.get) == (44,)

    await ss.write_sensor(sen, 44)
    assert state.registers == {1: 44}

    wreg.assert_called_once()
    assert wreg.call_args == call(address=1, value=44)

    # test a sensor with a bitmask
    sen = NumberRWSensor((1,), "s2", min=1, max=10, bitmask=0x3)
    state.track(sen)
    rhr.return_value = (1,)

    await ss.write_sensor(sen, 3)
    assert state.registers == {1: 3}

    await ss.write_sensor(sen, 5)
    assert state.registers == {1: 1}
    assert "outside" in caplog.text


@patch("sunsynk.Sunsynk.read_holding_registers")
@patch("sunsynk.Sunsynk.write_register")
async def test_ss_write_sensor_bm(
    wreg: MagicMock,
    rhr: MagicMock,
    state: InverterState,
    caplog: pytest.LogCaptureFixture,
) -> None:
    ss = Sunsynk()
    ss.state = state

    sen = NumberRWSensor((1,), "s1", bitmask=0x10)
    state.track(sen)
    state.update({1: 0xFF})
    assert state.registers == {1: 0xFF}

    assert sen.value_to_reg(0x10, state.get) == (0x10,)
    assert "outside" not in caplog.text

    rhr.return_value = [0xF8]  # write will perform a read!
    await ss.write_sensor(sen, 0x10)
    assert "outside" not in caplog.text
    assert state.registers == {1: 0xF8}
    wreg.assert_called_once()
    assert wreg.call_args == call(address=1, value=0xF8)

    await ss.write_sensor(sen, 0x00)
    assert state.registers == {1: 0xE8}
    assert "outside" not in caplog.text


@patch("sunsynk.Sunsynk.read_holding_registers")
async def test_ss_read_sensors(rhr: MagicMock, state: InverterState) -> None:
    ss = Sunsynk()
    ss.state = state
    sen = NumberRWSensor((1,), "", min=1, max=10)
    ss.state.track(sen)

    rhr.return_value = (1,)
    assert ss.state[sen] is None
    await ss.read_sensors([sen])
    assert ss.state[sen] == 1

    rhr.side_effect = Exception("a")
    with pytest.raises(Exception):
        await ss.read_sensors([sen])
