"""Sunsynk sensor tests."""
import logging

import pytest

from sunsynk.rwsensors import (
    NumberRWSensor,
    RWSensor,
    SelectRWSensor,
    Sensor,
    SwitchRWSensor,
    SystemTimeRWSensor,
    TimeRWSensor,
)
from sunsynk.state import InverterState

_LOGGER = logging.getLogger(__name__)


def test_bitmask(caplog: pytest.LogCaptureFixture, state: InverterState) -> None:
    s = RWSensor(1, "", bitmask=0x1)
    with pytest.raises(NotImplementedError):
        s.value_to_reg(None, state.get)

    s = NumberRWSensor(1, "", min=1, max=10, bitmask=0x1)

    state.track(s)
    assert state[s] is None

    state.update({1: 1})
    assert state[s] == 1
    assert "outside" not in caplog.text

    state.update({1: 3})

    val = 3
    reg = s.value_to_reg(val, state.get)
    reg = s.reg(*reg, msg=f"value was {val}")

    assert reg == (1,)
    assert "outside" in caplog.text


def test_bitmask2(caplog: pytest.LogCaptureFixture, state: InverterState) -> None:
    s = SwitchRWSensor(1, "", on=4, bitmask=0x4)
    state.track(s)

    assert state[s] is None
    state.update({1: 0x1})

    assert state[s] == "OFF"
    assert "outside" not in caplog.text

    state.update({1: 0x14})
    assert state[s] == "ON"

    val = "OFF"
    reg = s.value_to_reg(val, state.get)
    reg = s.reg(*reg, msg=f"value was {val}")
    assert reg == (0,)


def test_number_rw(state: InverterState) -> None:
    s = NumberRWSensor(1, "s1", min=1, max=10, factor=1)

    assert s.dependencies == []
    assert s.min == 1
    assert s.max == 10

    s.min = Sensor(2, "2")
    assert s.dependencies == [s.min]

    s.max = Sensor(3, "3")
    assert s.dependencies == [s.min, s.max]

    state.track(s)

    state.update(
        {
            1: 230,
            2: 1,
            3: 300,
        }
    )
    assert state[s] == 230

    state.update({1: 500})
    assert state[s] == 500  # does not take min/max into account!

    assert s.value_to_reg(200, state.get) == (200,)
    assert s.value_to_reg(500, state.get) == (300,)
    assert s.value_to_reg(-1, state.get) == (1,)

    # writing negative values (when allowed by min)
    s.min = -10
    assert s.value_to_reg(-1, state.get) == (65535,)

    s = NumberRWSensor(1, "s2", factor=0.01)
    state.track(s)

    state.update({1: 4850})
    assert state.registers[1] == 4850
    assert state[s] == 48.5

    long = NumberRWSensor((1, 2), "long", max=0xFFFFF)
    reg55 = (55, 1)
    res55 = (1 << 16) + 55
    assert long.reg_to_value(reg55) == res55
    assert long.value_to_reg(res55, state.get) == reg55

    with pytest.raises(NotImplementedError):
        s.address = tuple()
        s.value_to_reg(123, state.get)


def test_select_rw(caplog: pytest.LogCaptureFixture, state: InverterState) -> None:
    s = SelectRWSensor(1, "", options={1: "one", 2: "two"})

    assert s.reg_to_value((2,)) == "two"
    assert s.value_to_reg("two", state.get) == (2,)
    assert s.reg_to_value((5,)) is None

    state.track(s)
    state.update({1: 1})
    assert state[s] == "one"

    state.update({1: 2})
    assert state[s] == "two"

    assert s.available_values() == ["one", "two"]

    assert s.value_to_reg("five", state.get) == (2,)
    assert caplog.records[-1].message == "Unknown five"
    assert caplog.records[-1].levelname == "WARNING"


def test_systemtime_rw(state: InverterState) -> None:
    s = SystemTimeRWSensor((1, 2, 3), "Time")
    state.track(s)

    tim = "2023-03-01 12:34:56"
    res = s.value_to_reg(tim, state.get)
    assert res == (5891, 268, 8760)
    assert s.reg_to_value(res) == tim

    with pytest.raises(ValueError):
        s.value_to_reg("2023-03-01 12:34", state.get)


def test_time_rw(state: InverterState) -> None:
    s = TimeRWSensor(60, "two", factor=0.1)
    state.track(s)

    state.update(
        {
            60: 300,
        }
    )
    assert state[s] == "3:00"

    assert s.value_to_reg("0:00", state.get) == (0,)
    assert s.value_to_reg("4:01", state.get) == (401,)
    assert s.value_to_reg("23:59", state.get) == (2359,)

    assert s.dependencies == []
    s.min = TimeRWSensor(50, "min", factor=0.1)
    assert s.dependencies == [s.min]
    s.max = TimeRWSensor(70, "max", factor=0.1)
    assert s.dependencies == [s.min, s.max]

    state.track(s.min, s.max)
    assert state[s.min] is None
    assert state[s.max] is None
    state.update({50: 200, 70: 300})
    assert state[s.min] == "2:00"
    assert state[s.max] == "3:00"

    assert s.available_values(15, state.get) == ["2:00", "2:15", "2:30", "2:45", "3:00"]

    s.reg_to_value((201,))
    assert s.available_values(15, state.get) == [
        "2:00",
        "2:15",
        "2:30",
        "2:45",
        "3:00",
    ]

    state.update(
        {
            50: 2330,
            60: 2330,
            70: 30,
        }
    )
    assert s.available_values(15, state.get) == [
        "23:30",
        "23:45",
        "0:00",
        "0:15",
        "0:30",
    ]

    state.update(
        {
            50: 200,
            70: 200,
        }
    )
    assert s.available_values(15, state.get) == ["2:00"]


# def test_update_sensor(caplog) -> None:
#     s = NumberRWSensor(60, "two", factor=0.1)
#     assert s.value is None
#     update_sensors([s], {})
#     assert s.value is None
#     update_sensors([s], {60: 10})
#     assert s.value == 1


def test_bad_sensor(caplog: pytest.LogCaptureFixture) -> None:
    NumberRWSensor((60, 1), "two", factor=0.1, bitmask=1)
    assert "single register" in caplog.text


def test_sensor_hash() -> None:
    ss = {Sensor(0, "S 1"), Sensor(0, "S 1")}
    assert len(ss) == 1
    ss = {Sensor(0, "S 1"), Sensor(0, "S 2")}
    assert len(ss) == 2

    s = RWSensor((0, 1), "rwswitch")
    m = SelectRWSensor((0, 1), "switch")
    ss = {s, m}
    assert len(ss) == 2
