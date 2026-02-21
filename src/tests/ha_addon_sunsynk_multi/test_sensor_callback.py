"""Test sensor callbacks."""

from collections import defaultdict
from inspect import iscoroutinefunction
from unittest.mock import Mock, patch

import pytest

from ha_addon_sunsynk_multi.a_inverter import AInverter
from ha_addon_sunsynk_multi.sensor_callback import SensorRun, build_callback_schedule
from ha_addon_sunsynk_multi.sensor_options import SOPT, Sensor, SensorOption
from ha_addon_sunsynk_multi.timer_schedule import Schedule

from .conftest import ist_factory

pytestmark = pytest.mark.asyncio


async def test_build_callback_schedule() -> None:
    """Test build_callback_schedule."""
    SOPT.clear()
    SOPT.update({s.sensor: s for s in TEST1})
    ist = ist_factory("888", "ss1", 1)
    assert list(SOPT.values()) == list(TEST1)
    AInverter.init_sensors(ist, SOPT)
    # ist.init_sensors(SOPT)
    # assert ist.ss == {"test": TEST1[0], "test2": TEST1[1]}

    read_s: dict[int, SensorRun] = defaultdict(SensorRun)
    report_s: dict[int, SensorRun] = defaultdict(SensorRun)
    dds = Mock()
    dds.side_effect = [read_s, report_s]

    ist.write_queue = {}
    ist.index = 0

    with patch("ha_addon_sunsynk_multi.sensor_callback.defaultdict", dds):
        build_callback_schedule(ist)
        mycb = ist.cb
        if not iscoroutinefunction(mycb.callback):
            raise AssertionError("Callback is not a coroutine")

        assert mycb is not None
        assert read_s == {
            1: SensorRun(next_run=0, sensors={TEST1[0], TEST1[1]}),
        }
        assert report_s == {
            10: SensorRun(next_run=0, sensors={TEST1[0]}),
            20: SensorRun(next_run=0, sensors={TEST1[1]}),
        }

        def call_count() -> tuple[int, int, int]:
            return (  # type: ignore[attr-defined]
                ist.connector[0].connect.call_count,  # type: ignore[attr-defined]
                ist.read_sensors.call_count,  # type: ignore[attr-defined]
                ist.publish_sensors.call_count,  # type: ignore[attr-defined]
            )

        def publish_sensors() -> list[str]:
            return [k.name for k in ist.publish_sensors.call_args.kwargs["states"]]  # type: ignore[attr-defined]

        def next_run() -> tuple[int, int, int]:
            return (
                read_s[1].next_run,
                report_s[10].next_run,
                report_s[20].next_run,
            )

        assert call_count() == (0, 0, 0)
        assert next_run() == (0, 0, 0)

        await mycb.callback(1)
        assert call_count() == (1, 1, 1)
        assert next_run() == (2, 11, 21)

        await mycb.callback(10)
        assert call_count() == (2, 2, 2)
        assert next_run() == (11, 20, 21)
        assert publish_sensors() == ["test"]

        await mycb.callback(11)
        assert call_count() == (3, 3, 2)  # no publish on 11
        assert next_run() == (12, 20, 21)

        await mycb.callback(15)
        assert call_count() == (4, 4, 2)  # no publish on 15
        assert next_run() == (16, 20, 21)

        await mycb.callback(19)
        assert call_count() == (5, 5, 2)
        assert next_run() == (20, 20, 21)

        await mycb.callback(20)
        assert call_count() == (6, 6, 3)
        assert next_run() == (21, 30, 40)
        assert publish_sensors() == ["test", "test2"]

        await mycb.callback(100)
        assert call_count() == (7, 7, 4)  # single publish for 2 commands
        assert next_run() == (101, 110, 120)
        assert publish_sensors() == ["test", "test2"]


TEST1 = (
    SensorOption(
        sensor=Sensor(1, name="test", unit="kWh"),
        schedule=Schedule(read_every=1, report_every=10),
        visible=True,
    ),
    SensorOption(
        sensor=Sensor(2, name="test2", unit="kWh"),
        schedule=Schedule(read_every=1, report_every=20),
        visible=True,
    ),
)
