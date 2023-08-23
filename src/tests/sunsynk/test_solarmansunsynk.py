"""Solarman Sunsynk"""
from unittest.mock import AsyncMock

import pytest

from sunsynk.solarmansunsynk import SolarmanSunsynk


@pytest.mark.asyncio
async def test_uss_sensor() -> None:
    ss = SolarmanSunsynk(port="tcp://127.0.0.1:502")
    # await ss.connect()
    ss.client = AsyncMock()
    rhr = ss.client.read_holding_registers = AsyncMock()

    # _LOGGER.warning("%s", dir(ss.client))
    assert not rhr.called
    await ss.read_holding_registers(1, 2)
    assert rhr.called

    wrr = ss.client.write_holding_register = AsyncMock()
    assert not wrr.called
    await ss.write_register(address=1, value=2)
    assert wrr.called
