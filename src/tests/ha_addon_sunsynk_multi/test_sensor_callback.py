"""Test sensor callbacks."""

import asyncio
import time
from collections import defaultdict
from inspect import iscoroutinefunction
from unittest.mock import AsyncMock, Mock, call, patch

import pytest

from ha_addon_sunsynk_multi.a_inverter import AInverter
from ha_addon_sunsynk_multi.a_sensor import ASensor
from ha_addon_sunsynk_multi.options import OPT
from ha_addon_sunsynk_multi.sensor_callback import SensorRun, build_callback_schedule
from ha_addon_sunsynk_multi.sensor_options import SOPT, Sensor, SensorOption
from ha_addon_sunsynk_multi.timer_schedule import Schedule
from sunsynk.rwsensors import NumberRWSensor

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
                ist.inv.connect.call_count,  # type: ignore[attr-defined]
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


async def test_write_debounce_queues_latest_value() -> None:
    """Only write the latest command after the sensor debounce window."""
    # This sensor waits 0.5 seconds after the most recent command before writing.
    sensor = NumberRWSensor(1, name="test", debounce=0.5)
    option = SensorOption(sensor=sensor, schedule=Schedule("no_write"))
    SOPT.clear()
    SOPT[sensor] = option
    ist = ist_factory()
    ist.state.history = {}
    ist.state.historynn = {}
    ist.write_sensor = AsyncMock()  # type: ignore[method-assign]
    ist.ss[sensor.id] = ASensor(opt=option)
    first_value = 0
    second_value = 1

    build_callback_schedule(ist)

    class FakeClock:
        """Clock whose current time the test can move forward."""

        now = 0.0

        def monotonic(self) -> float:
            """Return the simulated current time."""
            return self.now

    clock = FakeClock()

    # The client changes its mind at 0.8 seconds, before the first command is
    # written. The queue keeps only this latest value and restarts the timer.
    with (
        patch(
            "ha_addon_sunsynk_multi.sensor_callback.time.monotonic",
            side_effect=clock.monotonic,
        ),
        patch("ha_addon_sunsynk_multi.sensor_callback.asyncio.sleep", new=AsyncMock()),
    ):
        # The first command arrives at 0.3 seconds. At 0.7 seconds, only 0.4
        # seconds have passed, so the callback must leave it queued.
        clock.now = 0.3
        ist.write_queue[sensor] = first_value
        ist.write_queue_at[sensor] = clock.monotonic()

        # Write any pending commands if their debounce window has elapsed.
        # This should not trigger a write yet because the debounce window has not elapsed.
        clock.now = 0.7
        await ist.cb.callback(0)

        # The second command arrives at the current time, 0.8 seconds. Its
        # debounce timer starts from this timestamp, not from a fixed value.
        clock.now = 0.8
        ist.write_queue[sensor] = second_value
        ist.write_queue_at[sensor] = clock.monotonic()

        # At 1.0 seconds, only 0.2 seconds have elapsed since the latest
        # command, so it must still be queued.
        clock.now = 1.0
        await ist.cb.callback(0)

        # At 1.3 seconds, the 0.5-second window has elapsed. The old value
        # must never be written; only the latest value should be sent.
        clock.now = 1.3
        await ist.cb.callback(0)

    # The complete call list must contain exactly one write, and it must use
    # the second value. This also proves the first value was never written.
    assert ist.write_sensor.await_args_list == [call(sensor, second_value)]


@pytest.mark.parametrize(
    ("local_debounce", "global_debounce", "write_after"),
    [
        (None, 0.5, 0.5),  # No local setting: use the global setting.
        (0.1, 0.5, 0.1),  # Local setting: use it instead of the global setting.
        (0, 0.5, 0),  # Local zero: disable the global setting.
    ],
)
async def test_write_debounce_global_and_local_settings(
    local_debounce: float | None,
    global_debounce: float,
    write_after: float,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Use the global setting unless an RWSensor has a local override."""
    monkeypatch.setattr(OPT, "write_debounce", global_debounce)
    sensor = NumberRWSensor(1, name="test", debounce=local_debounce)
    option = SensorOption(sensor=sensor, schedule=Schedule("no_write"))
    SOPT.clear()
    SOPT[sensor] = option
    ist = ist_factory()
    ist.state.history = {}
    ist.state.historynn = {}
    ist.write_sensor = AsyncMock()  # type: ignore[method-assign]
    ist.ss[sensor.id] = ASensor(opt=option)
    build_callback_schedule(ist)

    class FakeClock:
        """Clock whose current time the test can move forward."""

        now = 0.0

        def monotonic(self) -> float:
            """Return the simulated current time."""
            return self.now

    clock = FakeClock()
    with (
        patch(
            "ha_addon_sunsynk_multi.sensor_callback.time.monotonic",
            side_effect=clock.monotonic,
        ),
        patch("ha_addon_sunsynk_multi.sensor_callback.asyncio.sleep", new=AsyncMock()),
    ):
        # Queue one value at time zero, then run just before the selected
        # debounce period expires. A non-zero period must not write yet.
        ist.write_queue[sensor] = 1
        ist.write_queue_at[sensor] = clock.monotonic()
        if write_after:
            clock.now = write_after - 0.01
            await ist.cb.callback(0)
            ist.write_sensor.assert_not_awaited()

        # At the selected expiry time, exactly one write should occur.
        clock.now = write_after
        await ist.cb.callback(0)

    ist.write_sensor.assert_awaited_once_with(sensor, 1)


# A belt-and-braces test to ensure the write debounce mechanism works with real time.
async def test_write_debounce_uses_real_time() -> None:
    """Use the real monotonic clock and sleep before writing."""
    sensor = NumberRWSensor(1, name="test", debounce=0.05)
    option = SensorOption(sensor=sensor, schedule=Schedule("no_write"))
    SOPT.clear()
    SOPT[sensor] = option
    ist = ist_factory()
    ist.state.history = {}
    ist.state.historynn = {}
    ist.write_sensor = AsyncMock()  # type: ignore[method-assign]
    ist.ss[sensor.id] = ASensor(opt=option)
    build_callback_schedule(ist)

    # Record the real enqueue time, then run the normal callback before the
    # 0.05-second debounce period has expired.
    ist.write_queue[sensor] = 1
    ist.write_queue_at[sensor] = time.monotonic()
    await asyncio.sleep(0.02)
    await ist.cb.callback(0)
    ist.write_sensor.assert_not_awaited()

    # After the debounce period expires, the next callback sends the value.
    await asyncio.sleep(0.05)
    await ist.cb.callback(0)
    ist.write_sensor.assert_awaited_once_with(sensor, 1)


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
