"""Near-realtime mode tests (#401)."""

import asyncio
from collections import defaultdict
from collections.abc import Generator
from inspect import iscoroutinefunction
from unittest.mock import Mock, patch

import pytest

from ha_addon_sunsynk_multi.a_inverter import AInverter
from ha_addon_sunsynk_multi.near_realtime import NEAR_REALTIME
from ha_addon_sunsynk_multi.sensor_callback import SensorRun, build_callback_schedule
from ha_addon_sunsynk_multi.sensor_options import SOPT, SensorOption
from ha_addon_sunsynk_multi.timer_schedule import SCHEDULES, Schedule
from sunsynk import WATT, Sensor

from .conftest import ist_factory

pytestmark = pytest.mark.asyncio


@pytest.fixture(autouse=True)
def _reset_near_realtime() -> Generator[None, None, None]:
    """Reset near-realtime flag and cancel any auto-off task."""
    NEAR_REALTIME.enabled = False
    if NEAR_REALTIME.off_task is not None:
        NEAR_REALTIME.off_task.cancel()
        NEAR_REALTIME.off_task = None
    NEAR_REALTIME.on_auto_off = None
    yield
    NEAR_REALTIME.enabled = False
    if NEAR_REALTIME.off_task is not None:
        NEAR_REALTIME.off_task.cancel()
        NEAR_REALTIME.off_task = None
    NEAR_REALTIME.on_auto_off = None


async def test_near_realtime_auto_off() -> None:
    """Auto-off clears the flag and invokes the registered callback."""
    called = asyncio.Event()

    async def on_auto_off() -> None:
        called.set()

    NEAR_REALTIME.on_auto_off = on_auto_off
    with patch("ha_addon_sunsynk_multi.near_realtime.NEAR_REALTIME_SECONDS", 0.05):
        NEAR_REALTIME.set(True)
        assert NEAR_REALTIME.enabled is True
        await asyncio.wait_for(called.wait(), timeout=1)
    assert NEAR_REALTIME.enabled is False


async def test_near_realtime_cancel_on_disable() -> None:
    """Disabling cancels the auto-off timer."""
    called = asyncio.Event()

    async def on_auto_off() -> None:
        called.set()

    NEAR_REALTIME.on_auto_off = on_auto_off
    with patch("ha_addon_sunsynk_multi.near_realtime.NEAR_REALTIME_SECONDS", 60):
        NEAR_REALTIME.set(True)
        task = NEAR_REALTIME.off_task
        assert task is not None
        NEAR_REALTIME.set(False)
        assert NEAR_REALTIME.enabled is False
        assert NEAR_REALTIME.off_task is None
        await asyncio.sleep(0.05)
        assert task.cancelled() or task.done()
        assert not called.is_set()


async def test_near_realtime_publishes_w_without_changing_schedules() -> None:
    """With near realtime on, W sensors publish last sample after each read."""
    w_before = (
        SCHEDULES["w"].read_every,
        SCHEDULES["w"].report_every,
        SCHEDULES["w"].change_by,
        SCHEDULES["w"].change_any,
    )
    watt = Sensor(1, name="Battery power", unit=WATT)
    sopt = SensorOption(
        sensor=watt,
        schedule=Schedule(key="w", read_every=1, report_every=60, change_by=80),
        visible=True,
    )
    SOPT.clear()
    SOPT[watt] = sopt

    ist = ist_factory("888", "ss1", 1)
    ist.state.history = defaultdict(list)  # type: ignore[assignment]
    ist.state.historynn = defaultdict(list)  # type: ignore[assignment]
    ist.state.history[watt].append(1234)
    AInverter.init_sensors(ist, SOPT)

    read_s: dict[int, SensorRun] = defaultdict(SensorRun)
    report_s: dict[int, SensorRun] = defaultdict(SensorRun)
    dds = Mock(side_effect=[read_s, report_s])

    with patch("ha_addon_sunsynk_multi.sensor_callback.defaultdict", dds):
        build_callback_schedule(ist)
        mycb = ist.cb
        assert iscoroutinefunction(mycb.callback)

        NEAR_REALTIME.set(True)
        await mycb.callback(1)

    assert ist.publish_sensors.call_count == 1  # type: ignore[attr-defined]
    states = ist.publish_sensors.call_args.kwargs["states"]  # type: ignore[attr-defined]
    assert list(states.values()) == [1234]
    assert [a.name for a in states] == ["Battery power"]
    assert (
        SCHEDULES["w"].read_every,
        SCHEDULES["w"].report_every,
        SCHEDULES["w"].change_by,
        SCHEDULES["w"].change_any,
    ) == w_before
