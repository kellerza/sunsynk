"""Test sunsynk library."""
from typing import Sequence
from unittest.mock import AsyncMock

import pytest

# from sunsynk.definitions import serial
from sunsynk import Sunsynk
from sunsynk.pysunsynk import pySunsynk
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
