"""Options."""

import os
from unittest import mock

import pytest

from ha_addon_sunsynk_multi.options import OPT, Schedule


def test_load() -> None:
    OPT.prog_time_interval = 15
    assert OPT.prog_time_interval != 30
    OPT.load({"PROG_TIME_interval": "30"})
    assert OPT.prog_time_interval == 30


def test_load_env() -> None:
    OPT.prog_time_interval = 15
    assert OPT.prog_time_interval != 30
    test_environ = {
        "PROG_TIME_INTERVAL": "30",
        "SENSORS": "two,sensors",
        "SENSORS_FIRST_INVERTER": '["first","inv"]',
        "SCHEDULES": '[{"key": "k2", "change_by": "2"}]',
    }

    with mock.patch.dict(os.environ, test_environ, clear=True):
        res = OPT.load_env()

    assert OPT.prog_time_interval == 30
    assert OPT.sensors == ["two", "sensors"]
    assert OPT.sensors_first_inverter == ["first", "inv"]
    assert OPT.schedules == [Schedule(key="k2", change_by=2)]
    assert res


def test_load_env_bad() -> None:
    OPT.prog_time_interval = 15
    assert OPT.prog_time_interval != 30
    test_environ = {
        "PROG_TIME_INTERVAL": "30seconds",
    }

    with pytest.raises(ValueError):
        with mock.patch.dict(os.environ, test_environ, clear=True):
            OPT.load_env()
