"""States."""

import logging

from ha_addon_sunsynk_multi.sensor_options import OPT, SOPT

_LOGGER = logging.getLogger(__name__)


def test_opt1() -> None:
    """Sensors."""
    SOPT.init_sensors()
    assert sorted(s.id for s in SOPT.startup) == ["device_type", "serial"]
    assert sorted(s.id for s in SOPT) == ["device_type", "serial"]

    OPT.sensors = ["prog1_time"]
    SOPT.init_sensors()
    assert sorted(s.id for s in SOPT.startup) == [
        "device_type",
        "serial",
    ]
    assert sorted(s.id for s in SOPT) == [
        "device_type",
        "prog1_time",
        "prog2_time",
        "prog3_time",
        "prog4_time",
        "prog5_time",
        "prog6_time",
        "serial",
    ]
    assert sorted(s.id for s in SOPT if SOPT[s].visible) == [
        "prog1_time",
    ]
