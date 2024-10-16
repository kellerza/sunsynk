"""Solarman Sunsynk"""

from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from sunsynk.solarmansunsynk import SolarmanSunsynk

P_CONNECT = "sunsynk.solarmansunsynk.SolarmanSunsynk.connect"


@pytest.mark.asyncio
@patch(P_CONNECT, new_callable=AsyncMock)
async def test_uss_sensor(connect: Any) -> None:
    ss = SolarmanSunsynk(port="tcp://127.0.0.1:502", dongle_serial_number=101)
    # await ss.connect()
    ss.client = AsyncMock()
    rhr = ss.client.read_holding_registers = AsyncMock()

    # _LOGGER.warning("%s", dir(ss.client))
    assert not rhr.called
    await ss.read_holding_registers(1, 2)
    assert rhr.called

    wrr = ss.client.write_multiple_holding_registers = AsyncMock()
    assert not wrr.called
    await ss.write_register(address=1, value=2)
    assert wrr.called
