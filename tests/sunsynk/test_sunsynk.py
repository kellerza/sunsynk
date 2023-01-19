"""Test sunsynk library."""
import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# from sunsynk.definitions import serial
from sunsynk import Sunsynk, update_sensors
from sunsynk.pysunsynk import pySunsynk
from sunsynk.rwsensors import NumberRWSensor
from sunsynk.usunsynk import uSunsynk

_LOGGER = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_pyss():
    ss = pySunsynk()
    with pytest.raises(ConnectionError):
        await ss.connect()


@pytest.mark.asyncio
async def test_uss_schemes():
    """Test url schemes for usunsynk.

    umodbus only connects on read.
    """
    for port in ("serial:///dev/usb1", "tcp://127.0.0.1:502"):
        ss = uSunsynk(port=port)
        try:
            await ss.connect()
        except ModuleNotFoundError as err:  # not working on windows
            _LOGGER.error("usunsynk could not connect to %s: %s", port, err)

    for port in ("127.0.0.1:502", "xxx", "localhost"):
        ss = uSunsynk(port=port)
        with pytest.raises(ValueError):
            await ss.connect()


@pytest.mark.asyncio
async def test_uss_sensor():
    ss = uSunsynk(port="tcp://127.0.0.1:502")
    await ss.connect()

    rhr = ss.client.read_holding_registers = AsyncMock()

    _LOGGER.warning("%s", dir(ss.client))
    assert not rhr.called
    await ss.read_holding_registers(1, 2)
    assert rhr.called

    wrr = ss.client.write_registers = AsyncMock()
    assert not wrr.called
    await ss.write_register(address=1, value=2)
    assert wrr.called


@pytest.mark.asyncio
async def test_ss_NotImplemented():
    ss = Sunsynk()
    with pytest.raises(NotImplementedError):
        await ss.connect()
    with pytest.raises(NotImplementedError):
        await ss.write_register(address=1, value=1)
    with pytest.raises(NotImplementedError):
        await ss.read_holding_registers(1, 1)


@pytest.mark.asyncio
@patch("sunsynk.Sunsynk.read_holding_registers")
@patch("sunsynk.Sunsynk.write_register")
async def test_ss_write_sensor(rhr: MagicMock, wreg: MagicMock):
    ss = Sunsynk()
    sen = NumberRWSensor((1, 2), "", min=1, max=10)
    sen.reg_value = (99, 98)
    await ss.write_sensor(sen)

    # with pytest.raises(NotImplementedError):
    await ss.read_holding_registers(1, 1)

    # test a sensor with a bitmask
    sen = NumberRWSensor((1,), "", min=1, max=10, bitmask=0x3)
    rhr.return_value = (1,)
    update_sensors([sen], {1: 99})
    assert sen.reg_value != (99,)
    assert sen.reg_value == (99 & 3,)
    await ss.write_sensor(sen)


@pytest.mark.asyncio
@patch("sunsynk.Sunsynk.read_holding_registers")
async def test_ss_read_sensors(rhr: MagicMock):
    ss = Sunsynk()
    sen = NumberRWSensor((1,), "", min=1, max=10)
    rhr.return_value = (1,)
    assert sen.value is None
    await ss.read_sensors([sen])
    assert sen.value == 1

    rhr.side_effect = Exception("a")
    with pytest.raises(Exception):
        await ss.read_sensors([sen])
