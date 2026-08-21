"""Test driver."""

from unittest.mock import MagicMock, patch

from ha_addon_sunsynk_multi.a_inverter import AInverter
from ha_addon_sunsynk_multi.driver import STATE, init_driver
from ha_addon_sunsynk_multi.options import OPT
from sunsynk.solarman import SolarmanUnit
from sunsynk.sunsynk import Sunsynk


def test_init() -> None:
    """Test init."""
    inv_port = "tcp://127.0.0.1:123"
    inv_option = {"inverters": [{"port": inv_port, "modbus_id": 1}]}

    OPT.load_dict(inv_option)

    AInverter.connections.clear()
    AInverter.solarman_ports.clear()
    mock_conn = MagicMock()
    mock_conn.for_unit.return_value = MagicMock()
    with patch(
        "ha_addon_sunsynk_multi.driver.open_connection", return_value=mock_conn
    ) as open_conn:
        init_driver(OPT)
    assert len(STATE) == 1
    ist = STATE[0].inv
    assert isinstance(ist, Sunsynk)
    assert ist.port == inv_port
    assert ist.read_attempts == 3
    mock_conn.for_unit.assert_called_once_with(1)
    open_conn.assert_called_once_with(
        inv_port, timeout=OPT.timeout, message_spacing=0.05
    )

    AInverter.connections.clear()
    AInverter.solarman_ports.clear()
    OPT.read_message_spacing = 0
    mock_conn = MagicMock()
    mock_conn.for_unit.return_value = MagicMock()
    with patch(
        "ha_addon_sunsynk_multi.driver.open_connection", return_value=mock_conn
    ) as open_conn:
        init_driver(OPT)
    open_conn.assert_called_once_with(inv_port, timeout=OPT.timeout, message_spacing=0)
    OPT.read_message_spacing = 0.05

    AInverter.connections.clear()
    AInverter.solarman_ports.clear()
    solar_port = "solarman://127.0.0.1:8899"
    inv_option = {
        "inverters": [
            {
                "port": solar_port,
                "modbus_id": 1,
                "dongle_serial_number": "101",
            }
        ]
    }
    OPT.inverters = []
    OPT.load_dict(inv_option)
    init_driver(OPT)
    assert len(STATE) == 1
    ist = STATE[0].inv
    assert isinstance(ist, Sunsynk)
    assert isinstance(ist.unit, SolarmanUnit)
    assert ist.port == solar_port
    assert ist.unit.dongle_serial_number == 101
