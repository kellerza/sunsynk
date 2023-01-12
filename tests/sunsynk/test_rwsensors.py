"""Sunsynk sensor tests."""
import logging

import pytest

from sunsynk.rwsensors import (
    NumberRWSensor,
    RWSensor,
    SelectRWSensor,
    Sensor,
    TimeRWSensor,
)
from sunsynk.sunsynk import register_map, update_sensors

_LOGGER = logging.getLogger(__name__)


def test_bitmask(caplog) -> None:
    s = RWSensor(1, "", bitmask=0x1)
    with pytest.raises(NotImplementedError):
        s.value_to_reg(None)

    s = NumberRWSensor(1, "", min=1, max=10, bitmask=0x1)

    assert s.value is None

    s.update_reg_value(1)
    assert "" == caplog.text
    assert s.reg_value == (1,)
    assert s.value == 1

    s.update_reg_value(3)
    assert s.reg_value == (1,)
    assert "outside" in caplog.text
    assert s.value == 1


def test_number_rw() -> None:
    s = NumberRWSensor(1, "", min=1, max=10)

    deps = s.dependencies()
    assert len(deps) == 0
    assert s.min_value == 1
    assert s.max_value == 10

    s.min = Sensor(2, "2")
    deps = s.dependencies()
    assert len(deps) == 1
    assert deps[0].id == "2"
    assert s.min_value == 0
    s.min.value = 20
    assert s.min_value == 20
    s.min.value = "20"
    assert s.min_value == 20
    s.min.value = None
    assert s.min_value == 0

    s.max = Sensor(3, "3")
    deps = s.dependencies()
    assert len(deps) == 2
    assert deps[1].id == "3"
    assert s.max_value == 0
    s.max.value = 30
    assert s.max_value == 30

    assert s.update_reg_value(25)
    assert s.reg_value == (25,)

    assert s.update_reg_value(500) is False
    assert s.update_reg_value(-1) is False
    assert s.reg_value == (25,)

    s = NumberRWSensor(1, "", factor=0.01)
    s.reg_to_value(4850)
    assert s.value == 48.5
    s.update_reg_value(50)
    assert s.reg_value == (5000,)
    s.update_reg_value(50.1)
    assert s.reg_value == (5010,)

    s.min = Sensor(2, "2", factor=0.01)
    s.min.reg_to_value(4710)
    assert s.min_value == 47.1

    s.max = Sensor(3, "3", factor=0.01)
    s.max.reg_to_value(5450)
    assert s.max_value == 54.5


def test_select_rw(caplog) -> None:
    s = SelectRWSensor(1, "", options={1: "one", 2: "two"})
    s.reg_to_value(1)

    assert s.value == "one"
    assert s.available_values() == ["one", "two"]
    assert s.update_reg_value("two")
    assert s.reg_value == (2,)

    assert s.update_reg_value("five") is False
    assert s.value == "two"
    assert s.reg_value == (2,)
    assert caplog.records[-1].message == "Unknown five"
    assert caplog.records[-1].levelname == "WARNING"

    assert s.reg_to_value(2) == "two"
    assert s.reg_to_value(5) is None


def test_time_rw() -> None:
    s = TimeRWSensor(60, "two", factor=0.1)
    rmap = register_map(60, [300])
    update_sensors([s], rmap)
    assert s.value == "3:00"

    assert len(s.available_values(15)) == 24 * 60 / 15

    assert s.value_to_reg("0:00") == (0,)
    assert s.value_to_reg("4:01") == (401,)
    assert s.value_to_reg("23:59") == (2359,)

    deps = s.dependencies()
    assert len(deps) == 0
    s.min = s_min = TimeRWSensor(50, "min", factor=0.1)
    deps = s.dependencies()
    assert len(deps) == 1
    assert deps[0].id == "min"
    s.max = s_max = TimeRWSensor(70, "max", factor=0.1)
    deps = s.dependencies()
    assert len(deps) == 2
    assert deps[1].id == "max"

    s_min.reg_to_value(200)
    s_max.reg_to_value(300)
    assert s.available_values(15) == ["2:00", "2:15", "2:30", "2:45", "3:00"]

    s.reg_to_value(201)
    assert s.available_values(15) == ["2:01", "2:00", "2:15", "2:30", "2:45", "3:00"]

    s.reg_to_value(2330)
    s_min.reg_to_value(2330)
    s.max.reg_to_value(30)
    assert s.available_values(15) == ["23:30", "23:45", "0:00", "0:15", "0:30"]

    s.reg_to_value(200)
    s_min.reg_to_value(200)
    s.max.reg_to_value(200)
    assert s.available_values(15) == ["2:00"]
