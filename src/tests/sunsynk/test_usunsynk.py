"""Test sunsynk library."""
import logging
import os
from unittest.mock import AsyncMock

import pytest

# from sunsynk.definitions import serial
from sunsynk.usunsynk import USunsynk

_LOGGER = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_uss_schemes() -> None:
    """Test url schemes for usunsynk.

    umodbus only connects on read.
    """
    for port in ("serial:///dev/usb1", "tcp://127.0.0.1:502"):
        ss = USunsynk(port=port)
        try:
            await ss.connect()
        except ModuleNotFoundError as err:  # not working on windows
            _LOGGER.error("usunsynk could not connect to %s: %s", port, err)
            if os.name == "posix":
                raise

    for port in ("127.0.0.1:502", "xxx", "localhost"):
        ss = USunsynk(port=port)
        with pytest.raises(ValueError):
            await ss.connect()


@pytest.mark.asyncio
async def test_uss_sensor() -> None:
    ss = USunsynk(port="tcp://127.0.0.1:502")
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
