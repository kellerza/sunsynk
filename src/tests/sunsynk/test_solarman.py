"""Solarman unit."""

from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from sunsynk.solarman import SolarmanUnit
from sunsynk.sunsynk import Sunsynk

P_CONNECT = "sunsynk.solarman.SolarmanUnit.connect"


def test_solarman_dongle_serial_zero_is_clear_error() -> None:
    """Zero must not be reported as a non-integer parse failure."""
    with pytest.raises(ValueError, match="non-zero integer"):
        SolarmanUnit(port="tcp://127.0.0.1:8899", dongle_serial_number=0)


def test_solarman_dongle_serial_invalid_type() -> None:
    """Non-numeric values get a parse-oriented message."""
    with pytest.raises(ValueError, match="Got 'abc'"):
        SolarmanUnit(port="tcp://127.0.0.1:8899", dongle_serial_number="abc")  # type: ignore[arg-type]


@patch(P_CONNECT, new_callable=AsyncMock)
async def test_uss_sensor(connect: Any) -> None:
    """Tests."""
    unit = SolarmanUnit(port="tcp://127.0.0.1:502", dongle_serial_number=101)
    unit.client = AsyncMock()
    rhr = unit.client.read_holding_registers = AsyncMock(return_value=[1, 2])

    assert not rhr.called
    await unit.read_holding_registers(1, 2)
    assert rhr.called

    wrr = unit.client.write_multiple_holding_registers = AsyncMock()
    assert not wrr.called
    await unit.write_registers(1, [2])
    assert wrr.called

    ss = Sunsynk(unit=unit, port="tcp://127.0.0.1:502")
    await ss.write_register(address=1, value=2)
    assert wrr.called


async def test_read_holding_registers_disconnects_on_error() -> None:
    """A failed read drops the client so the next Sunsynk retry reconnects."""
    unit = SolarmanUnit(port="solarman://127.0.0.1:8899", dongle_serial_number=101)
    client = AsyncMock()
    client.read_holding_registers = AsyncMock(side_effect=ValueError())
    unit.client = client

    with pytest.raises(ValueError):
        await unit.read_holding_registers(0, 8)

    assert client.read_holding_registers.await_count == 1
    client.disconnect.assert_awaited_once()
    assert unit.client is None
