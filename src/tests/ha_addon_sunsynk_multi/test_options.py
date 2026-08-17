"""Options."""

import os
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from ha_addon_sunsynk_multi.options import OPT, Schedule


def test_load() -> None:
    """Tests."""
    OPT.prog_time_interval = 15
    assert OPT.prog_time_interval != 30
    OPT.load_dict({"PROG_TIME_interval": "30"})
    assert OPT.prog_time_interval == 30


def test_load_env() -> None:
    """Tests."""
    OPT.prog_time_interval = 15
    assert OPT.prog_time_interval != 30
    test_environ = {
        "PROG_TIME_INTERVAL": "30",
        "SENSORS": "two,sensors",
        "SENSORS_FIRST_INVERTER": '["first","inv"]',
        "SCHEDULES": '[{"key": "k2", "change_by": "2"}]',
    }

    with patch.dict(os.environ, test_environ, clear=True):
        res = OPT.load_env()

    assert OPT.prog_time_interval == 30
    assert OPT.sensors == ["two", "sensors"]
    assert OPT.sensors_first_inverter == ["first", "inv"]
    assert OPT.schedules == [Schedule(key="k2", change_by=2)]
    assert res


def test_load_env_bad() -> None:
    """Tests."""
    OPT.prog_time_interval = 15
    assert OPT.prog_time_interval != 30
    test_environ = {
        "PROG_TIME_INTERVAL": "30seconds",
    }

    with pytest.raises(ValueError):
        with patch.dict(os.environ, test_environ, clear=True):
            OPT.load_env()


@patch("ha_addon_sunsynk_multi.options.MQTTOptions.init_addon")
async def test_legacy_port_migration(mock_init: MagicMock) -> None:
    """Legacy serial:// and tcp+dongle migrate via PORT schemes."""
    OPT.driver = ""
    OPT.load_dict(
        {
            "inverters": [
                {
                    "ha_prefix": "inv1",
                    "port": "serial:///dev/ttyUSB0",
                    "serial_nr": "1",
                }
            ],
        }
    )
    await OPT.init_addon()
    assert OPT.inverters[0].port == "/dev/ttyUSB0"

    OPT.load_dict(
        {
            "inverters": [
                {
                    "ha_prefix": "inv1",
                    "port": "tcp://192.168.1.182:8899",
                    "serial_nr": "1",
                    "dongle_serial_number": 1,
                }
            ],
        }
    )
    await OPT.init_addon()
    assert OPT.inverters[0].port == "solarman://192.168.1.182:8899"

    OPT.load_dict(
        {
            "inverters": [
                {
                    "ha_prefix": "inv1",
                    "port": "solarman://192.168.1.182:8899",
                    "serial_nr": "1",
                    "dongle_serial_number": 1,
                }
            ],
        }
    )
    await OPT.init_addon()
    assert OPT.inverters[0].port == "solarman://192.168.1.182:8899"


@patch("ha_addon_sunsynk_multi.options.MQTTOptions.init_addon")
async def test_init_addon_rejects_incorrect_config(mock_init: MagicMock) -> None:
    """DRIVER, empty HA_PREFIX, and unusable Solarman PORT fail startup."""
    OPT.load_dict(
        {
            "driver": "pymodbus",
            "inverters": [
                {"ha_prefix": "inv1", "port": "/dev/ttyUSB0", "serial_nr": "1"}
            ],
        }
    )
    with pytest.raises(ValueError, match="DRIVER is obsolete"):
        await OPT.init_addon()

    OPT.driver = ""
    OPT.load_dict(
        {
            "inverters": [
                {
                    "ha_prefix": "inv1",
                    "port": "/dev/ttyUSB0",
                    "serial_nr": "1",
                    "driver": "solarman",
                }
            ],
        }
    )
    with pytest.raises(ValueError, match="DRIVER is obsolete"):
        await OPT.init_addon()

    OPT.load_dict(
        {
            "inverters": [
                {"ha_prefix": "", "port": "tcp://192.168.1.1:502", "serial_nr": "1"}
            ],
        }
    )
    with pytest.raises(ValueError, match="HA_PREFIX is required"):
        await OPT.init_addon()

    OPT.load_dict(
        {
            "inverters": [
                {
                    "ha_prefix": "inv1",
                    "port": "/dev/ttyUSB0",
                    "serial_nr": "1",
                    "dongle_serial_number": 99,
                }
            ],
        }
    )
    with pytest.raises(ValueError, match="Cannot use Solarman"):
        await OPT.init_addon()


@patch("ha_addon_sunsynk_multi.options.MQTTOptions.init_addon")
async def test_unique(mock_init: MagicMock) -> None:
    """Tests."""
    OPT.driver = ""
    invs = [
        {"ha_prefix": "inv1", "port": "a"},
        {"ha_prefix": "inv2", "port": "b"},
        {"ha_prefix": "inv3", "port": "c"},
    ]
    OPT.load_dict({"inverters": invs})

    assert mock_init.call_count == 0
    await OPT.init_addon()
    assert mock_init.call_count == 1

    invs[1]["ha_prefix"] = invs[0]["ha_prefix"]
    OPT.load_dict({"inverters": invs})
    with pytest.raises(ValueError) as err:
        await OPT.init_addon()
    assert err.match("unique HA_PREFIX: inv1, inv1, inv3")


def test_to_dict() -> None:
    """Tests."""
    tests: list[tuple[Any, dict | None]] = [
        (None, None),
        ({}, {}),
        (["a=1", "b=2", "c=-0.1", "x=no"], {"a": 1, "b": 2, "c": -0.1}),
    ]

    for input_data, expected in tests:
        OPT.overrides = None
        OPT.sensor_overrides = None
        OPT.load_dict({"sensor_overrides": input_data})
        assert OPT.overrides == expected
