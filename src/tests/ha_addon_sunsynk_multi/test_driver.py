"""Test driver."""

import pytest

from ha_addon_sunsynk_multi.a_inverter import AInverter
from ha_addon_sunsynk_multi.driver import STATE, init_driver
from ha_addon_sunsynk_multi.options import OPT
from sunsynk.pysunsynk import PySunsynk
from sunsynk.solarmansunsynk import SolarmanSunsynk
from sunsynk.usunsynk import USunsynk


def test_init() -> None:
    """Test init."""
    inv_port = "tcp://127.0.0.1:123"
    inv_option = {"inverters": [{"port": inv_port, "modbus_id": 1}]}

    OPT.load_dict(inv_option)

    with pytest.raises(ValueError):
        OPT.driver = "bad"
        init_driver(OPT)

    OPT.driver = "pymodbus"
    OPT.inverters[0].driver = ""
    init_driver(OPT)
    assert len(STATE) == 1
    ist = STATE[0].connector[0]
    assert isinstance(ist, PySunsynk)
    assert ist.port == inv_port
    # assert STATE[0].inv == PySunsynk(port=inv_port, state=STATE[0].inv_state)

    AInverter.connectors.clear()
    OPT.driver = "umodbus"
    OPT.load_dict(inv_option)
    init_driver(OPT)
    assert len(STATE) == 1
    ist = STATE[0].connector[0]
    assert isinstance(ist, USunsynk)
    assert ist.port == inv_port
    # assert STATE[0].inv == USunsynk(port=inv_port, state=STATE[0].inv_state)

    AInverter.connectors.clear()
    inv_option = {
        "inverters": [{"port": inv_port, "modbus_id": 1, "dongle_serial_number": "101"}]
    }
    OPT.driver = "solarman"
    OPT.inverters = []
    OPT.load_dict(inv_option)
    init_driver(OPT)
    assert len(STATE) == 1
    ist = STATE[0].connector[0]
    assert isinstance(ist, SolarmanSunsynk)
    assert ist.port == inv_port
    assert ist.dongle_serial_number == 101
    # assert STATE[0].inv == SolarmanSunsynk(
    #     port=inv_port, state=STATE[0].inv_state, dongle_serial_number=101
    # )
