from unittest.mock import AsyncMock

import pytest

# from sunsynk.definitions import serial
from sunsynk.sunsynk import Sunsynk

pytestmark = pytest.mark.asyncio


async def test_ss():
    s = Sunsynk()
    with pytest.raises(ConnectionError):
        await s.connect()


async def test_ss_tcp():
    s = Sunsynk(port="127.0.0.1:502")
    with pytest.raises(ConnectionError):
        await s.connect()


async def test_ss_read():
    s = Sunsynk()
    s.client = AsyncMock()

    # await s.read([serial])

    # s.client.read_holding_registers.assert_called_once()

    # assert serial.value == ""
