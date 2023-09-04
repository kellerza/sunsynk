"""Test helpers."""
import pytest

from sunsynk.helpers import (
    SSTime,
    as_num,
    ensure_tuple,
    hex_str,
    int_round,
    patch_bitmask,
    signed,
)
from sunsynk.sensors import Sensor


def test_as_num(caplog: pytest.LogCaptureFixture) -> None:
    assert as_num(None) == 0
    assert as_num(1.0) == 1.0
    assert as_num(1) == 1
    assert as_num("1") == 1
    assert as_num("1.5") == 1.5
    caplog.clear()
    assert as_num("1.0x") == 0
    assert "could not convert string to float: '1.0x'" in caplog.text


def test_ensure_tuple() -> None:
    assert ensure_tuple(1) == (1,)
    assert ensure_tuple((1,)) == (1,)
    assert ensure_tuple((1, 5)) == (1, 5)
    assert ensure_tuple("a") == ("a",)


def test_int_round() -> None:
    res1 = int_round(1.0)
    assert isinstance(res1, int)
    assert res1 == 1


def test_signed() -> None:
    assert signed(0x7FFF) == 0x7FFF
    assert signed(0xFFFF) == -1
    assert signed(0) == 0
    assert signed(32767) == 32767
    assert signed(32768) == -32768


def test_signeds() -> None:
    """Signed sensors have a -1 factor"""
    s = Sensor(1, "", "", factor=-1)
    assert s.reg_to_value((1,)) == 1
    assert s.reg_to_value((0xFFFE,)) == -2
    assert s.reg_to_value((0xFFBA,)) == -70

    s = Sensor(1, "", "", factor=1)
    assert s.reg_to_value((1,)) == 1
    assert s.reg_to_value((0xFFFE,)) == 0xFFFE
    assert s.reg_to_value((1, 1)) == 0x10001


def test_time() -> None:
    time = SSTime(minutes=10)
    assert time.str_value == "0:10"
    assert time.reg_value == 10
    time.str_value = "0:10"
    assert time.minutes == 10
    time.str_value = "00:10"
    assert time.minutes == 10
    time.reg_value = 10
    assert time.minutes == 10

    time = SSTime(minutes=100)
    assert time.str_value == "1:40"
    assert time.reg_value == 140
    time.str_value = "1:40"
    assert time.minutes == 100
    time.str_value = "01:40"
    assert time.minutes == 100
    time.reg_value = 140
    assert time.minutes == 100

    just_before_midnight = 23 * 60 + 59
    time = SSTime(minutes=just_before_midnight)
    assert time.str_value == "23:59"
    assert time.reg_value == 2359
    time.str_value = "23:59"
    assert time.minutes == just_before_midnight
    time.reg_value = 2359
    assert time.minutes == just_before_midnight


def test_patch_bitmask() -> None:
    assert patch_bitmask(2, 1, 1) == 3
    assert patch_bitmask(1, 2, 2) == 3

    assert patch_bitmask(0xFFF, 0, 1) == 0xFFE
    assert patch_bitmask(0xFFFF, 0, 1) == 0xFFFE
    assert patch_bitmask(0xFFF, 0, 2) == 0xFFD


def test_hex_str() -> None:
    """Test hex str."""
    assert hex_str((1, 2)) == "{0x0001 0x0002}"
    assert hex_str((1, 2), address=(10, 20)) == "{10=0x0001 20=0x0002}"
    with pytest.raises(ValueError):
        assert hex_str((1, 2), address=(10,))
    with pytest.raises(TypeError):
        assert hex_str(1, address=(10, 12))  # type: ignore
