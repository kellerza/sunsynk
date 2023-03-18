"""Sunsynk sensor tests."""
import logging
from typing import Sequence

import pytest

from sunsynk.definitions import AMPS, CELSIUS, SENSORS, VOLT, WATT
from sunsynk.rwsensors import RWSensor, SelectRWSensor
from sunsynk.sensors import (
    FaultSensor,
    InverterStateSensor,
    MathSensor,
    SDStatusSensor,
    Sensor,
    SerialSensor,
    TempSensor,
)
from sunsynk.state import group_sensors

_LOGGER = logging.getLogger(__name__)


def test_sen():
    s = Sensor(0, "S 1")
    a = [s]
    assert a[0] == s
    assert s.id == "s_1"

    # Test __hash__
    s2 = Sensor(0, "S 2")
    ss = {s, s}
    assert len(ss) == 1
    ss = {s, s2}
    assert len(ss) == 2

    # Test eq
    s22 = Sensor(0, "S 2")
    assert s != s2
    assert s22 == s2
    with pytest.raises(TypeError):
        assert s == 0


def test_sensor_hash():
    ss = {Sensor(0, "S 1"), Sensor(0, "S 1")}
    assert len(ss) == 1
    ss = {Sensor(0, "S 1"), Sensor(0, "S 2")}
    assert len(ss) == 2

    s = Sensor(0, "S 1")
    m = MathSensor((0, 1), "math1", factors=(1, 1))
    ss = {s, m}
    assert len(ss) == 2

    s = RWSensor((0, 1), "rwswitch")
    m = SelectRWSensor((0, 1), "switch")
    ss = {s, m}
    assert len(ss) == 2


def test_group() -> None:
    sen = [
        Sensor(10, "10"),
        Sensor(11, "11"),
        Sensor(12, "12"),
        Sensor(20, "20"),
    ]
    g = list(group_sensors(sen))
    assert g == [[10, 11, 12], [20]]

    assert len(list(group_sensors(None))) == 0


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
    s = [SENSORS.all[s] for s in SENSORS.all]
    for i in range(2, 6):
        _LOGGER.warning("waste with %d gap: %s", i, waste(group_sensors(s, i)))

    grp = group_sensors(s)

    grplen = [len(i) for i in grp]

    assert grplen[:1] == [6]
    # assert grplen[-1:] == [1]


def waste(groups) -> Sequence[int]:
    """Calculate amount of unused registers in this grouping."""
    return [sum(b - a for a, b in zip(g[:-1], g[1:])) for g in groups]


def test_ids() -> None:
    for name, sen in SENSORS.all.items():
        assert name == sen.id

        if sen.factor and sen.factor < 0 and len(sen.address) > 1:
            assert False, "only single signed supported"

        if sen.id in SENSORS.deprecated:
            continue
        assert sen.unit != AMPS or sen.name.endswith(" current")
        assert sen.unit != WATT or sen.name.endswith(" power")
        assert sen.unit != VOLT or sen.name.endswith(" voltage")
        assert sen.unit != CELSIUS or sen.name.endswith(" temperature")


def test_other_sensors() -> None:
    s = TempSensor(1, "", "", 0.1)
    assert s.reg_to_value((1000,)) == 0

    s = SDStatusSensor(1, "", "")
    assert s.reg_to_value((1000,)) == "fault"
    assert s.reg_to_value((1,)) == "unknown 1"

    s = InverterStateSensor(1, "", "")
    assert s.reg_to_value((2,)) == "ok"
    assert s.reg_to_value((1,)) == "unknown 1"


def test_math() -> None:
    s = MathSensor((1, 2), "", "", factors=(1, -1))
    assert s.reg_to_value((1000, 800)) == 200

    with pytest.raises(AssertionError):
        MathSensor((0, 1), "", "", factors=(1))

    with pytest.raises(AssertionError):
        MathSensor((0, 1), "", "", factors="aaa")

    with pytest.raises(TypeError):
        MathSensor((0, 1), "", "")

    assert s.reg_to_value((200, 800)) == -600
    s.no_negative = True
    assert s.reg_to_value((200, 800)) == 0
    s.no_negative = False
    s.absolute = True
    assert s.reg_to_value((200, 800)) == 600
    s = MathSensor((1, 2), "", "", factors=(1, -1), absolute=True)
    assert s.reg_to_value((200, 800)) == 600


def test_update_func() -> None:
    s = SerialSensor(1, "", "")
    regs = (0x4148, 0x3738)
    assert s.reg_to_value(regs) == "AH78"


# def test_update_float(caplog) -> None:
#     s = TempSensor(60, "two", factor=0.1)
#     rmap = register_map(60, [1001])
#     update_sensors([s], rmap)

#     assert s.value == 0.1

#     s.reg_value = (None,)
#     s.update_value()
#     assert "Could not decode" in caplog.text


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
