"""Test 3ph defs."""
from sunsynk.definitions import SENSORS as SENSORS1P
from sunsynk.definitions3ph import SENSORS as SENSORS3P


def test_ok() -> None:
    """Test."""
    assert len(SENSORS1P.serial.address) == len(SENSORS3P.serial.address)
    assert SENSORS1P.rated_power
    assert SENSORS3P.rated_power
