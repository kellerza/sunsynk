"""The the timer module."""

import asyncio
import logging
from statistics import mean
from unittest.mock import MagicMock, patch

import pytest

from ha_addon_sunsynk_multi.timer_callback import (
    TICK_MS,
    AsyncCallback,
    Callback,
    SyncCallback,
    run_callbacks,
)
from ha_addon_sunsynk_multi.timer_schedule import Schedule

_LOG = logging.getLogger(__name__)
# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio

_REAL_ASYNCIO_SLEEP = asyncio.sleep


async def _tick_sleep(_delay: float) -> None:
    await _REAL_ASYNCIO_SLEEP(0)


async def test_timer() -> None:
    """Test the timer."""
    run = {1: 0, 2: 0}

    async def run1(now: int) -> None:
        run[1] += 1
        _LOG.debug("\t" * 3 + "run1: now=%s cnt=%s", now, run[1])
        await asyncio.sleep(0)

    def run2(now: int) -> None:
        run[2] += 1
        _LOG.debug("\t" * 6 + "run2: now=%s cnt=%s", now, run[2])
        # assert now % 2 == 0

    cbs: list[Callback] = [
        AsyncCallback(name="test", callback=run1, every=1, keep_stats=True),
        SyncCallback(name="test2", callback=run2, every=2, keep_stats=True),
    ]

    with (
        patch(
            "ha_addon_sunsynk_multi.timer_callback.ZonedDateTime",
        ) as mock_zdt,
        patch(
            "ha_addon_sunsynk_multi.timer_callback.asyncio.sleep",
            side_effect=_tick_sleep,
        ),
    ):
        now_ms = 2000

        def get_now() -> MagicMock:
            nonlocal now_ms
            if now_ms > 19990:
                raise IndexError
            res = MagicMock()
            res.timestamp_millis.return_value = now_ms
            now_ms += TICK_MS
            return res

        mock_zdt.now_in_system_tz.side_effect = get_now

        try:
            await run_callbacks(cbs)
        except IndexError:  # simulated time is done
            pass
        async_cb = cbs[0]
        assert isinstance(async_cb, AsyncCallback)
        if async_cb.task and not async_cb.task.done():
            await async_cb.task

    assert run == {1: 18, 2: 9}
    assert len(cbs[0].stat_time) == 18
    assert len(cbs[1].stat_time) == 9
    assert mean(cbs[0].stat_time) >= 0
    assert mean(cbs[1].stat_time) < 0.01


async def test_timer_stagger_offset() -> None:
    """Callbacks with offset_ms fire within the second, not all at once."""
    fired: dict[str, list[int]] = {"a": [], "b": [], "c": []}
    now_ms = 1000
    last_now_ms = [now_ms]

    def cb_a(_now: int) -> None:
        fired["a"].append(last_now_ms[0])

    def cb_b(_now: int) -> None:
        fired["b"].append(last_now_ms[0])

    def cb_c(_now: int) -> None:
        fired["c"].append(last_now_ms[0])

    cbs: list[Callback] = [
        SyncCallback(name="a", callback=cb_a, every=1, offset_ms=0),
        SyncCallback(name="b", callback=cb_b, every=1, offset_ms=250),
        SyncCallback(name="c", callback=cb_c, every=1, offset_ms=500),
    ]

    with (
        patch(
            "ha_addon_sunsynk_multi.timer_callback.ZonedDateTime",
        ) as mock_zdt,
        patch(
            "ha_addon_sunsynk_multi.timer_callback.asyncio.sleep",
            side_effect=_tick_sleep,
        ),
    ):

        def get_now() -> MagicMock:
            nonlocal now_ms
            if now_ms > 2990:
                raise IndexError
            last_now_ms[0] = now_ms
            res = MagicMock()
            res.timestamp_millis.return_value = now_ms
            now_ms += TICK_MS
            return res

        mock_zdt.now_in_system_tz.side_effect = get_now

        try:
            await run_callbacks(cbs)
        except IndexError:
            pass

    assert fired["a"] == [1000, 2000]
    assert fired["b"] == [1000, 2250]
    assert fired["c"] == [1000, 2500]


async def test_schedule() -> None:
    """Test the schedule."""
    s = Schedule(key="x", change_any=True)
    # no history = change
    with pytest.raises(NotImplementedError):
        s.significant_change([], 12)

    s = Schedule(key="x", change_by=80)
    # lower
    assert s.significant_change([100], 90) is False
    assert s.significant_change([100], 21) is False
    assert s.significant_change([100], 20)
    # higher
    assert s.significant_change([100], 179) is False
    assert s.significant_change([100], 180)
    assert s.significant_change([100], 200)
    # no history = no change
    assert s.significant_change([], 90) is False

    s = Schedule(key="x", change_percent=10)
    assert s.significant_change([100], 91) is False
    assert s.significant_change([100], 109) is False
    assert s.significant_change([100], 120)
    assert s.significant_change([100], 111)
    assert s.significant_change([100], 200)
