"""The the timer module."""
import logging
from unittest.mock import patch

import pytest

from ha_addon_sunsynk_multi.timer_callback import (
    AsyncCallback,
    SyncCallback,
    run_callbacks,
)
from ha_addon_sunsynk_multi.timer_schedule import Schedule

_LOGGER = logging.getLogger(__name__)
# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


async def test_timer() -> None:
    """Test the timer."""
    run = {1: 0, 2: 0}

    async def run1(now: int) -> None:
        run[1] += 1
        _LOGGER.info("now=%s: cnt=%s", now, run[1])
        if run[1] == 17:
            cbs.clear()

    def run2(now: int) -> None:
        run[2] += 1
        _LOGGER.info("now=%s:      cnt2=%s", now, run[2])
        assert now % 2 == 0

    cbs = [
        AsyncCallback(name="test", callback=run1, every=1),
        SyncCallback(name="test2", callback=run2, every=2),
    ]

    with patch("ha_addon_sunsynk_multi.timer_callback.modf") as mock_time:
        lst = [(0.99, s) for s in range(2, 20)]
        _LOGGER.info(lst)
        mock_time.side_effect = lst
        # mock_time.return_value = 0
        await run_callbacks(cbs)
        assert mock_time.call_count == 18
        assert run[1] == 17
        assert run[2] == 9


async def test_schedule() -> None:
    """Test the schedule."""
    s = Schedule(key="x", change_any=True)
    # no history = change
    assert s.significant_change([], 12)
    assert s.significant_change([12], 12) is False

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
