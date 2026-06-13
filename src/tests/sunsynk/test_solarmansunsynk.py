"""Solarman Sunsynk."""

from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from sunsynk.solarmansunsynk import SolarmanSunsynk

P_CONNECT = "sunsynk.solarmansunsynk.SolarmanSunsynk.connect"


def test_solarman_dongle_serial_zero_is_clear_error() -> None:
    """Zero must not be reported as a non-integer parse failure."""
    with pytest.raises(ValueError, match="non-zero integer"):
        SolarmanSunsynk(port="tcp://127.0.0.1:8899", dongle_serial_number=0)


def test_solarman_dongle_serial_invalid_type() -> None:
    """Non-numeric values get a parse-oriented message."""
    with pytest.raises(ValueError, match="Got 'abc'"):
        SolarmanSunsynk(port="tcp://127.0.0.1:8899", dongle_serial_number="abc")  # type: ignore[arg-type]


@patch(P_CONNECT, new_callable=AsyncMock)
async def test_uss_sensor(connect: Any) -> None:
    """Tests."""
    ss = SolarmanSunsynk(port="tcp://127.0.0.1:502", dongle_serial_number=101)
    # await ss.connect()
    ss.client = AsyncMock()
    rhr = ss.client.read_holding_registers = AsyncMock()

    # _LOG.warning("%s", dir(ss.client))
    assert not rhr.called
    await ss.read_holding_registers(1, 2)
    assert rhr.called

    wrr = ss.client.write_multiple_holding_registers = AsyncMock()
    assert not wrr.called
    await ss.write_register(address=1, value=2)
    assert wrr.called
