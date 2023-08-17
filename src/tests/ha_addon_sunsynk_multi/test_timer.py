"""The the timer module."""
import pytest

from ha_addon_sunsynk_multi.timer_callback import Callback, run_callbacks
from ha_addon_sunsynk_multi.timer_schedule import Schedule

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


async def test_timer() -> None:
    """Test the timer."""
    cbs: list[Callback] = []

    a = False

    async def run1(s: int) -> None:
        nonlocal a
        a = True

        cbs.clear()

    cbs.append(Callback(name="test", callback=run1, every=1))

    await run_callbacks(cbs)

    assert a


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
