from asyncio import iscoroutinefunction
from collections import defaultdict
from unittest.mock import Mock, call, patch

import pytest

from ha_addon_sunsynk_multi.a_inverter import AInverter
from ha_addon_sunsynk_multi.sensor_callback import SensorRun, build_callback_schedule
from ha_addon_sunsynk_multi.sensor_options import SOPT, Sensor, SensorOption
from ha_addon_sunsynk_multi.timer_schedule import Schedule

pytestmark = pytest.mark.asyncio


async def test_build_callback_schedule(ist: AInverter) -> None:
    """Test build_callback_schedule."""
    SOPT.clear()
    SOPT.update({s.sensor: s for s in TEST1})

    read_s: dict[str, SensorRun] = defaultdict(SensorRun)
    report_s: dict[str, SensorRun] = defaultdict(SensorRun)
    dds = Mock()
    dds.side_effect = [read_s, report_s]

    ist.write_queue = {}

    with (patch("ha_addon_sunsynk_multi.sensor_callback.defaultdict", dds),):
        mycb = build_callback_schedule(ist=ist, idx=0)
        if not iscoroutinefunction(mycb.callback):
            assert False, "Callback is not a coroutine"

        assert mycb is not None
        assert read_s == {
            1: SensorRun(next_run=0, sensors={TEST1[0], TEST1[1]}),
        }
        assert report_s == {
            10: SensorRun(next_run=0, sensors={TEST1[0]}),
            20: SensorRun(next_run=0, sensors={TEST1[1]}),
        }

        await mycb.callback(1)

        assert ist.read_sensors.call_args_list == [  # type: ignore
            call(
                sensors={TEST1[0].sensor, TEST1[1].sensor},
                msg="poll_need_to_read",
            )
        ]
        ist.read_sensors.call_args_list.clear()  # type: ignore
        assert ist.publish_sensors.call_count == 0  # type: ignore
        assert read_s == {
            1: SensorRun(next_run=2, sensors={TEST1[0], TEST1[1]}),
        }
        assert report_s == {
            10: SensorRun(next_run=11, sensors={TEST1[0]}),
            20: SensorRun(next_run=21, sensors={TEST1[1]}),
        }

        await mycb.callback(10)

        assert ist.read_sensors.call_args_list == [  # type: ignore
            call(
                sensors={TEST1[0].sensor, TEST1[1].sensor},
                msg="poll_need_to_read",
            )
        ]
        assert read_s == {
            1: SensorRun(next_run=11, sensors={TEST1[0], TEST1[1]}),
        }
        assert report_s == {
            10: SensorRun(next_run=20, sensors={TEST1[0]}),
            20: SensorRun(next_run=21, sensors={TEST1[1]}),
        }

        await mycb.callback(11)
        assert read_s == {
            1: SensorRun(next_run=12, sensors={TEST1[0], TEST1[1]}),
        }
        assert report_s == {
            10: SensorRun(next_run=20, sensors={TEST1[0]}),
            20: SensorRun(next_run=21, sensors={TEST1[1]}),
        }

        await mycb.callback(20)
        assert read_s == {
            1: SensorRun(next_run=21, sensors={TEST1[0], TEST1[1]}),
        }
        assert report_s == {
            10: SensorRun(next_run=30, sensors={TEST1[0]}),
            20: SensorRun(next_run=40, sensors={TEST1[1]}),
        }
        assert ist.publish_sensors.call_count == 0  # type: ignore


TEST1 = (
    SensorOption(
        sensor=Sensor(1, name="test", unit="kWh"),
        schedule=Schedule(read_every=1, report_every=10),
    ),
    SensorOption(
        sensor=Sensor(2, name="test2", unit="kWh"),
        schedule=Schedule(read_every=1, report_every=20),
    ),
)
