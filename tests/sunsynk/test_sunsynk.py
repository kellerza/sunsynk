"""Test sunsynk library."""
from typing import Sequence
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# from sunsynk.definitions import serial
from sunsynk import Sunsynk, update_sensors
from sunsynk.pysunsynk import pySunsynk
from sunsynk.rwsensors import NumberRWSensor
from sunsynk.usunsynk import uSunsynk


@pytest.fixture
def sss() -> Sequence[Sunsynk]:
    res: Sequence[Sunsynk] = []
    if uSunsynk:
        res.append(uSunsynk())
    if pySunsynk:
        res.append(pySunsynk())
    return res


@pytest.mark.asyncio
async def test_ss():
    if pySunsynk:
        ss = pySunsynk()
        with pytest.raises(ConnectionError):
            await ss.connect()


@pytest.mark.asyncio
async def test_ss_tcp():
    if pySunsynk:
        ss = pySunsynk()
        ss.port = "127.0.0.1:502"
        with pytest.raises(ConnectionError):
            await ss.connect()


@pytest.mark.asyncio
async def test_ss_read(sss):
    for ss in sss:
        if uSunsynk:
            ss = uSunsynk()
            ss.client = AsyncMock()

        if pySunsynk:
            ss = pySunsynk()
            ss.client = AsyncMock()


@pytest.mark.asyncio
async def test_ss_base_class():
    ss = Sunsynk()
    with pytest.raises(NotImplementedError):
        await ss.connect()


@pytest.mark.asyncio
async def test_ss_NotImplemented():
    ss = Sunsynk()
    with pytest.raises(NotImplementedError):
        await ss.connect()
    with pytest.raises(NotImplementedError):
        await ss.write_register(address=1, value=1)


@pytest.mark.asyncio
@patch("sunsynk.Sunsynk.read_holding_registers")
@patch("sunsynk.Sunsynk.write_register")
async def test_ss_write_sensor(rhr: MagicMock, wreg: MagicMock):
    ss = Sunsynk()
    sen = NumberRWSensor((1,), "", min=1, max=10)
    sen.reg_value = (99,)
    await ss.write_sensor(sen)

    # test a sensor with a bitmask
    sen = NumberRWSensor((1,), "", min=1, max=10, bitmask=0x3)
    rhr.return_value = (1,)
    update_sensors([sen], {1: 99})
    assert sen.reg_value != (99,)
    assert sen.reg_value == (99 & 3,)
    await ss.write_sensor(sen)


@pytest.mark.asyncio
@patch("sunsynk.Sunsynk.read_holding_registers")
async def test_ss_read_sensor(rhr: MagicMock):
    ss = Sunsynk()
    sen = NumberRWSensor((1,), "", min=1, max=10)
    rhr.return_value = (1,)
    assert sen.value is None
    await ss.read_sensors([sen])
    assert sen.value == 1

    rhr.side_effect = Exception("a")
    with pytest.raises(Exception):
        await ss.read_sensors([sen])


def test_update_sensor(caplog) -> None:
    s = NumberRWSensor(60, "two", factor=0.1)
    assert s.value is None
    update_sensors([s], {})
    assert s.value is None
    update_sensors([s], {60: 10})
    assert s.value == 1


def test_bad_sensor(caplog) -> None:
    NumberRWSensor((60, 1), "two", factor=0.1, bitmask=1)
    assert "single register" in caplog.text
