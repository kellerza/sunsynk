"""Tests."""

import asyncio
from unittest.mock import AsyncMock, PropertyMock, patch

import pytest

from ha_addon_sunsynk_multi.a_inverter import AInverter
from sunsynk.definitions.single_phase import SENSORS
from sunsynk.pysunsynk import PySunsynk
from sunsynk.state import InverterState

P_ASYNC_CONNECTED = "sunsynk.pysunsynk.AsyncModbusTcpClient.connected"
P_CONNECT = "sunsynk.pysunsynk.AsyncModbusTcpClient.connect"
P_READ_HR = "sunsynk.pysunsynk.AsyncModbusTcpClient.read_holding_registers"


@pytest.mark.asyncio
@patch(P_ASYNC_CONNECTED, new_callable=PropertyMock)
@patch(P_CONNECT, new_callable=AsyncMock)
@patch(P_READ_HR, new_callable=AsyncMock)
async def test_ss_tcp_read(
    read_holding_reg: AsyncMock,
    _connect: AsyncMock,
    async_connect: PropertyMock,
    state: InverterState,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Simulate a timeout during retry read.

    https://github.com/kellerza/sunsynk/issues/180
    Also see sunsynk.test_pysunsynk.
    """
    read_holding_reg.side_effect = asyncio.exceptions.CancelledError

    ss = PySunsynk(port="tcp://1.1.1.1")
    ss.state = state
    ss.state.track(SENSORS.rated_power)
    ss.state.track(SENSORS.serial)

    # Ensure we can read
    async_connect.return_value = 1

    # AInverter.read_sensors_retry
    ist = AInverter(index=0, inv=ss, opt={}, ss={})  # type:ignore

    sensors = [SENSORS.rated_power]

    with pytest.raises(asyncio.exceptions.CancelledError):
        await ist.read_sensors(sensors=sensors)

    res = await ist.read_sensors_retry(sensors=sensors)
    assert res is False
    assert "Could not read" not in caplog.text

    # more sensors to retry individual
    sensors.append(SENSORS.serial)

    res = await ist.read_sensors_retry(sensors=sensors)
    assert res is False
    assert "Could not read" in caplog.text
