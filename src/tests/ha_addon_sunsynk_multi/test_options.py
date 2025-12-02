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
async def test_unique(mock_init: MagicMock) -> None:
    """Tests."""
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
        (["a=1", "b=2", "c=x"], {"a": 1, "b": 2}),
    ]

    for input_data, expected in tests:
        OPT.overrides = None
        OPT.sensor_overrides = None
        OPT.load_dict({"sensor_overrides": input_data})
        assert OPT.overrides == expected
