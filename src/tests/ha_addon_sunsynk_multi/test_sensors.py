"""States."""
import logging

from ha_addon_sunsynk_multi.sensor_options import OPT, SOPT

_LOGGER = logging.getLogger(__name__)


def test_opt1() -> None:
    """Sensors."""
    SOPT.init_sensors()
    assert sorted(s.id for s in SOPT.startup) == ["rated_power", "serial"]
    assert sorted(s.id for s in SOPT) == ["rated_power", "serial"]

    OPT.sensors = ["prog1_time"]
    SOPT.init_sensors()
    assert sorted(s.id for s in SOPT.startup) == [
        "prog2_time",
        "prog6_time",
        "rated_power",
        "serial",
    ]
    assert sorted(s.id for s in SOPT) == [
        "prog1_time",
        "prog2_time",
        "prog6_time",
        "rated_power",
        "serial",
    ]
    # assert SOPT.filter_str == {
    #     "prog1_time": "round_robin",
    #     "prog2_time": "round_robin",
    #     "prog6_time": "round_robin",
    # }
    # assert SOPT["prog1_time"].visible
