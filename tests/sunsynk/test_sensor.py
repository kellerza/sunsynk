"""Sunsynk sensor tests."""
import logging
from typing import Sequence

import pytest

from sunsynk.definitions import ALL_SENSORS, AMPS, CELSIUS, DEPRECATED, VOLT, WATT
from sunsynk.sensor import (
    FaultSensor,
    HSensor,
    InverterStateSensor,
    MathSensor,
    NumberRWSensor,
    SDStatusSensor,
    SelectRWSensor,
    Sensor,
    SerialSensor,
    SSTime,
    TempSensor,
    TimeRWSensor,
    ensure_tuple,
    group_sensors,
    update_sensors,
)
from sunsynk.sunsynk import register_map

_LOGGER = logging.getLogger(__name__)


# @pytest.fixture
# def sensors():
#     """Fixture to create some sensors."""
#     yield [
#         (402, True, Sensor("6400_00262200", "s_402", "W")),
#         (3514, True, Sensor("6400_00260100", "s_3514", "W", 1000)),
#     ]


def test_sen():
    a = []
    s = Sensor(0, "S 1").append_to(a)
    h = HSensor(0, "H 1").append_to(a)
    assert a[0] is s
    assert a[1] is h
    assert s.id == "s_1"


def test_group() -> None:
    sen = [
        Sensor(10, "10"),
        Sensor(11, "11"),
        Sensor(12, "12"),
        Sensor(20, "20"),
    ]
    g = list(group_sensors(sen))
    assert g == [[10, 11, 12], [20]]


def test_group_max_size() -> None:
    sen = [
        Sensor(10, "10"),
        Sensor(11, "11"),
        Sensor(12, "12"),
        Sensor(13, "13"),
        Sensor(14, "14"),
        Sensor(15, "15"),
        Sensor(16, "16"),
    ]
    g = list(group_sensors(sen, max_group_size=3))
    assert g == [[10, 11, 12], [13, 14, 15], [16]]


def test_all_groups() -> None:
    s = [ALL_SENSORS[s] for s in ALL_SENSORS]
    for i in range(2, 6):
        _LOGGER.warning("waste with %d gap: %s", i, waste(group_sensors(s, i)))

    grp = group_sensors(s)

    grplen = [len(i) for i in grp]

    assert grplen[:1] == [6]
    assert grplen[-1:] == [1]


def waste(groups) -> Sequence[int]:
    """Calculate amount of unused registers in this grouping."""
    return [sum(b - a for a, b in zip(g[:-1], g[1:])) for g in groups]


def test_ids() -> None:
    for name, sen in ALL_SENSORS.items():
        assert name == sen.id

        if sen.factor and sen.factor < 0 and len(sen.reg_address) > 1:
            assert False, "only single signed supported"

        if sen.id in DEPRECATED:
            continue
        assert sen.unit != AMPS or sen.name.endswith(" current")
        assert sen.unit != WATT or sen.name.endswith(" power")
        assert sen.unit != VOLT or sen.name.endswith(" voltage")
        assert sen.unit != CELSIUS or sen.name.endswith(" temperature")


def test_ensure_tuple() -> None:
    assert ensure_tuple(1) == (1,)
    assert ensure_tuple((1,)) == (1,)
    assert ensure_tuple((1, 5)) == (1, 5)
    assert ensure_tuple("a") == ("a",)


def test_signed() -> None:
    """Signed sensors have a -1 factor"""
    s = Sensor(1, "", "", factor=-1)
    assert s.reg_to_value(1) == 1
    assert s.reg_to_value(0xFFFE) == -1

    s = Sensor(1, "", "", factor=1)
    assert s.reg_to_value(1) == 1
    assert s.reg_to_value(0xFFFE) == 0xFFFE
    assert s.reg_to_value((1, 1)) == 0x10001


def test_other_sensros() -> None:
    s = TempSensor(1, "", "", 0.1)
    assert s.reg_to_value(1000) == 0

    s = SDStatusSensor(1, "", "")
    assert s.reg_to_value(1000) == "fault"
    assert s.reg_to_value(1) == "unknown 1"

    s = InverterStateSensor(1, "", "")
    assert s.reg_to_value(2) == "ok"
    assert s.reg_to_value(1) == "unknown 1"


def test_math() -> None:
    s = MathSensor((1, 2), "", "", factors=(1, -1))
    assert s.reg_to_value((1000, 800)) == 200

    with pytest.raises(AssertionError):
        MathSensor((0, 1), "", "", factors=(1))

    with pytest.raises(AssertionError):
        MathSensor((0, 1), "", "", factors="aaa")

    with pytest.raises(TypeError):
        MathSensor((0, 1), "", "")


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

    s = NumberRWSensor(1, "", factor=0.1)
    s.reg_to_value(485)
    assert s.value == 48.5
    s.update_reg_value(50)
    assert s.reg_value == (500,)


def test_select_rw() -> None:
    s = SelectRWSensor(1, "", options={1: "one", 2: "two"})
    s.reg_to_value(1)

    assert s.value == "one"
    assert s.available_values() == ["one", "two"]
    assert s.update_reg_value("two")
    assert s.reg_value == (2,)

    assert s.update_reg_value("five") is False
    assert s.reg_value == (2,)

    s.reg_to_value(5)
    assert s.value == "Unknown 5"


def test_update_func() -> None:
    s = SerialSensor(1, "", "")
    regs = (0x4148, 0x3738)
    assert s.reg_to_value(regs) == "AH78"

    # s = Sensor((2, 3, 4), "serial", func=decode_serial)

    # rmap = register_map(2, regs)

    # assert s.value is None
    # update_sensors([s], rmap)
    # assert s.value is None, "no update, not enough registers"

    # rmap = register_map(2, regs + regs)
    # update_sensors([s], rmap)
    # assert s.value == "AH78AH"


def test_update_float() -> None:
    s = TempSensor(60, "two", factor=0.1)
    rmap = register_map(60, [1001])
    update_sensors([s], rmap)
    assert s.value == 0.1


def test_decode_fault() -> None:
    s = FaultSensor(1, "", "")
    regs = (0x01, 0x0, 0x0, 0x0)
    assert s.reg_to_value(regs) == "F01"
    regs = (0x02, 0x0, 0x0, 0x0)
    assert s.reg_to_value(regs) == "F02"
    regs = (0x80, 0x0, 0x0, 0x0)
    assert s.reg_to_value(regs) == "F08"

    regs = (0x0, 0x8000, 0x0, 0x0)
    assert s.reg_to_value(regs) == "F32"
    regs = (0x0, 0x0, 0x1, 0x0)
    assert s.reg_to_value(regs) == "F33"


def test_time() -> None:
    time = SSTime(10)
    assert time.str_value == "0:10"
    assert time.reg_value == 10
    time.str_value = "0:10"
    assert time.minutes == 10
    time.str_value = "00:10"
    assert time.minutes == 10
    time.reg_value = 10
    assert time.minutes == 10

    time = SSTime(100)
    assert time.str_value == "1:40"
    assert time.reg_value == 140
    time.str_value = "1:40"
    assert time.minutes == 100
    time.str_value = "01:40"
    assert time.minutes == 100
    time.reg_value = 140
    assert time.minutes == 100

    just_before_midnight = 23 * 60 + 59
    time = SSTime(just_before_midnight)
    assert time.str_value == "23:59"
    assert time.reg_value == 2359
    time.str_value = "23:59"
    assert time.minutes == just_before_midnight
    time.reg_value = 2359
    assert time.minutes == just_before_midnight


def test_time_rw() -> None:
    s = TimeRWSensor(60, "two", factor=0.1)
    rmap = register_map(60, [300])
    update_sensors([s], rmap)
    assert s.value == "3:00"

    assert len(s.available_values(15)) == 24 * 60 / 15

    assert s.value_to_reg("0:00") == 0
    assert s.value_to_reg("4:01") == 401
    assert s.value_to_reg("23:59") == 2359

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


def test_dep() -> None:
    ctl = ALL_SENSORS["grid_ct_load"]
    assert ctl.id in DEPRECATED

    ctl = ALL_SENSORS["grid_ct_power"]
    assert ctl.id not in DEPRECATED
