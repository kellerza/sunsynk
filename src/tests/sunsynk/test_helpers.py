"""Test helpers."""

import logging
import re
import struct

import pytest

from sunsynk.helpers import (
    RegType,
    SSTime,
    as_num,
    ensure_tuple,
    hex_str,
    int_round,
    pack_value,
    patch_bitmask,
    unpack_value,
)
from sunsynk.sensors import Sensor

_LOGGER = logging.getLogger(__name__)


def test_as_num(caplog: pytest.LogCaptureFixture) -> None:
    """Test as_num function."""
    assert as_num(None) == 0
    assert as_num(1.0) == 1.0
    assert as_num(1) == 1
    assert as_num("1") == 1
    assert as_num("1.5") == 1.5
    caplog.clear()
    assert as_num("1.0x") == 0
    assert "could not convert string to float: '1.0x'" in caplog.text


def test_ensure_tuple() -> None:
    """Test ensure tuple."""
    assert ensure_tuple(1) == (1,)
    assert ensure_tuple((1,)) == (1,)
    assert ensure_tuple((1, 5)) == (1, 5)
    assert ensure_tuple("a") == ("a",)


def test_hex_str() -> None:
    """Test hex str."""
    assert hex_str((1, 2)) == "{0x0001 0x0002}"
    assert hex_str((1, 2), address=(10, 20)) == "{10=0x0001 20=0x0002}"
    with pytest.raises(ValueError):
        assert hex_str((1, 2), address=(10,))
    with pytest.raises(TypeError):
        assert hex_str(1, address=(10, 12))  # type: ignore


def test_int_round() -> None:
    """Test int round."""
    res1 = int_round(1.0)
    assert isinstance(res1, int)
    assert res1 == 1

    res1 = int_round(1.1)
    assert isinstance(res1, float)
    assert res1 == 1.1

    res1 = int_round(1.001)
    assert isinstance(res1, int)
    assert res1 == 1


def extract_ints(text: str) -> list[int]:
    """Extract numbers from a string."""
    val_arr = re.sub(r"\s+", " ", text.strip()).split(" ")
    return [int(v, 16 if "0x" in v else 10) for v in val_arr]


def test_pack_unpack_16bits() -> None:
    """Test pack & unpack, 32-bit."""
    tests: list[tuple[str, RegType]] = [
        ("  32767   0x7fff", (0x7FFF,)),
        ("     -1         ", (0xFFFF,)),
        ("      0         ", (0,)),
        (" -32768  -0x8000", (0x8000,)),
    ]
    for idx, (text, regs) in enumerate(tests):
        vals = extract_ints(text)
        _LOGGER.info("Test 16-bit %d - %s", idx, (regs, vals))
        val = vals[0]
        for j in vals:
            assert j == val

        assert pack_value(val, bits=16) == regs
        assert unpack_value(regs) == val


def test_pack_unpack_32bits() -> None:
    """Test pack & unpack, 32-bit."""
    tests: list[tuple[str, RegType]] = [
        ("-2147483648           ", (0x0000, 0x8000)),
        ("     -65536   -0x10000", (0x0000, 0xFFFF)),
        ("     -65535    -0xFFFF", (0x0001, 0xFFFF)),
        ("     -65510    -0xFFE6", (0x001A, 0xFFFF)),
        ("     -65509    -0xFFE5", (0x001B, 0xFFFF)),
        ("     -32768           ", (0x8000, 0xFFFF)),
        ("         -2           ", (0xFFFE, 0xFFFF)),
        ("         -1           ", (0xFFFF, 0xFFFF)),
        ("          0           ", (0x0000, 0x0000)),
        ("          1           ", (0x0001, 0x0000)),
        ("      32767     0x7FFF", (0x7FFF, 0x0000)),
        ("      32768     0x8000", (0x8000, 0x0000)),
        ("      32769     0x8001", (0x8001, 0x0000)),
        ("      65535     0xFFFF", (0xFFFF, 0x0000)),
        (" 2147483647 0x7FFFFFFF", (0xFFFF, 0x7FFF)),
    ]

    for idx, (text, regs) in enumerate(tests):
        vals = extract_ints(text)
        _LOGGER.info("Test 32-bit #%d: %s = %s", idx, vals, regs)
        val = vals[0]
        for j in vals:
            assert j == val

        assert pack_value(val, bits=32) == regs
        assert unpack_value(regs) == val


def test_pack_unpack_maybe16() -> None:
    """Test maybe16."""
    for m16 in [True, False]:
        assert unpack_value((0x7FFF, 0x0000), maybe16=m16) == 32767
        assert unpack_value((0xFFFF, 0xFFFF), maybe16=m16) == -1

        assert unpack_value((0xFFFF,), maybe16=m16) == -1
    assert unpack_value((0xFFFF, 0x0000), maybe16=True) == -1
    assert unpack_value((0xFFFF, 0x0000), maybe16=False) == 0xFFFF


def test_pack_unpack() -> None:
    """Test pack_value and unpack_value functions."""
    # Test 16-bit values
    assert pack_value(-1, bits=16) == (0xFFFF,)
    assert pack_value(32767, bits=16) == (0x7FFF,)
    assert pack_value(65535, bits=16, signed=False) == (0xFFFF,)
    # Test 32-bit values
    assert pack_value(-1, bits=32) == (0xFFFF, 0xFFFF)
    assert pack_value(0x7FFFFFFF, bits=32) == (0xFFFF, 0x7FFF)
    # Test round-trip
    val = -12345
    assert unpack_value(pack_value(val, bits=16)) == val
    assert unpack_value(pack_value(val, bits=32)) == val

    # Test error cases
    with pytest.raises(struct.error):
        pack_value(-1, bits=16, signed=False)
    with pytest.raises(ValueError):
        pack_value(1, bits=8)  # Invalid bit length


def test_patch_bitmask() -> None:
    """Test patch_bitmask function."""
    assert patch_bitmask(2, 1, 1) == 3
    assert patch_bitmask(1, 2, 2) == 3

    assert patch_bitmask(0xFFF, 0, 1) == 0xFFE
    assert patch_bitmask(0xFFFF, 0, 1) == 0xFFFE
    assert patch_bitmask(0xFFF, 0, 2) == 0xFFD


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
    """Test SSTime class."""
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
