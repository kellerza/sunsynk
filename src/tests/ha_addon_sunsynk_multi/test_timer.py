"""The the timer module."""

import asyncio
import logging
from statistics import mean
from unittest.mock import MagicMock, patch

import pytest

from ha_addon_sunsynk_multi.timer_callback import (
    AsyncCallback,
    Callback,
    SyncCallback,
    run_callbacks,
)
from ha_addon_sunsynk_multi.timer_schedule import Schedule

_LOG = logging.getLogger(__name__)
# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


async def test_timer() -> None:
    """Test the timer."""
    run = {1: 0, 2: 0}

    async def run1(now: int) -> None:
        run[1] += 1
        _LOG.debug("\t" * 3 + "run1: now=%s cnt=%s", now, run[1])
        await asyncio.sleep(0.02)

    def run2(now: int) -> None:
        run[2] += 1
        _LOG.debug("\t" * 6 + "run2: now=%s cnt=%s", now, run[2])
        # assert now % 2 == 0

    cbs: list[Callback] = [
        AsyncCallback(name="test", callback=run1, every=1, keep_stats=True),
        SyncCallback(name="test2", callback=run2, every=2, keep_stats=True),
    ]

    with patch(
        "ha_addon_sunsynk_multi.timer_callback.ZonedDateTime",
    ) as mock_zdt:
        # loop duration should be 950ms, so sleep is short (1000ms - 950ms = 50ms)
        lst = [per_loop for t in range(2000, 20000, 1000) for per_loop in (t, t + 950)]

        def get_now():

            val = lst.pop(0)
            res = MagicMock()
            res.timestamp_millis.return_value = val
            _LOG.debug("get_now: %s", res.timestamp_millis())
            return res

        mock_zdt.now_in_system_tz.side_effect = get_now

        try:
            await run_callbacks(cbs)
        except IndexError:  # seconds are done
            pass

    assert run == {1: 18, 2: 9}
    assert len(cbs[0].stat_time) == 18
    assert len(cbs[1].stat_time) == 9
    assert mean(cbs[0].stat_time) >= 0.02
    assert mean(cbs[1].stat_time) < 0.01


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
