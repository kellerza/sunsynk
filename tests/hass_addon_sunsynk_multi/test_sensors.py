"""States."""
import logging

from tests.hass_addon_sunsynk_multi import sensors

_LOGGER = logging.getLogger(__name__)


def test_opt1():
    """Sesnors."""
    opt = sensors.OPT
    sopt = sensors.SOPT

    sopt.from_options()
    assert sorted(sopt.startup.keys()) == ["rated_power", "serial"]
    assert sorted(sopt.sensors.keys()) == []

    opt.sensors = ["prog1_time"]
    sopt.from_options()
    assert sorted(sopt.startup.keys()) == [
        "prog2_time",
        "prog6_time",
        "rated_power",
        "serial",
    ]
    assert sorted(sopt.sensors.keys()) == ["prog1_time", "prog2_time", "prog6_time"]
    assert sopt.filter_str == {
        "prog1_time": "round_robin",
        "prog2_time": "round_robin",
        "prog6_time": "round_robin",
    }
    assert sopt.visible == {
        "prog1_time": True,
    }
