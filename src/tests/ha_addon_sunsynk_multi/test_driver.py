"""Test driver."""
import pytest

from ha_addon_sunsynk_multi.driver import STATE, init_driver  # noqa
from ha_addon_sunsynk_multi.options import OPT, unmarshal  # noqa
from sunsynk.pysunsynk import PySunsynk
from sunsynk.solarmansunsynk import SolarmanSunsynk
from sunsynk.usunsynk import USunsynk


def test_init() -> None:
    """Test init."""

    with pytest.raises(ValueError):
        OPT.driver = "bad"
        init_driver(OPT)

    inv_port = "tcp://127.0.0.1:123"
    inv_option = {"inverters": [{"port": inv_port, "modbus_id": 1}]}

    OPT.driver = "pymodbus"
    unmarshal(OPT, inv_option)
    init_driver(OPT)
    assert len(STATE) == 1
    assert STATE[0].inv == PySunsynk(port=inv_port, state=STATE[0].inv.state)

    OPT.driver = "umodbus"
    unmarshal(OPT, inv_option)
    init_driver(OPT)
    assert len(STATE) == 1
    assert STATE[0].inv == USunsynk(port=inv_port, state=STATE[0].inv.state)

    inv_option = {
        "inverters": [{"port": inv_port, "modbus_id": 1, "dongle_serial_number": 101}]
    }
    OPT.driver = "solarman"
    unmarshal(OPT, inv_option)
    init_driver(OPT)
    assert len(STATE) == 1
    assert STATE[0].inv == SolarmanSunsynk(
        port=inv_port, state=STATE[0].inv.state, dongle_serial_number=101
    )
