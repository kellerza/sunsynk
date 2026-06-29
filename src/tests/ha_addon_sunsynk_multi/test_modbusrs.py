"""Optional tests for the modbus-rs driver (requires ``pip install sunsynk[modbusrs]``)."""

import pytest

pytest.importorskip("modbus_rs")
pytestmark = pytest.mark.modbusrs


from ha_addon_sunsynk_multi.a_inverter import AInverter  # noqa: E402
from ha_addon_sunsynk_multi.driver import STATE, init_driver  # noqa: E402
from ha_addon_sunsynk_multi.options import OPT  # noqa: E402
from sunsynk.rsunsynk import RSunsynk  # noqa: E402


def test_init_modbusrs() -> None:
    """Test the modbus-rs driver builds an RSunsynk connector."""
    AInverter.connectors.clear()
    inv_port = "tcp://127.0.0.1:502"
    OPT.driver = "modbusrs"
    OPT.inverters = []
    OPT.load_dict({"inverters": [{"port": inv_port, "modbus_id": 1}]})
    init_driver(OPT)
    assert len(STATE) == 1
    ist = STATE[0].connector[0]
    assert isinstance(ist, RSunsynk)
    assert ist.port == inv_port
