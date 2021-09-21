"""Optionally test filters."""
import logging
from typing import Callable, List, Tuple, Union

import pytest

from tests.conftest import import_module

_LOGGER = logging.getLogger(__name__)


@pytest.fixture
def getfilter() -> Callable:
    """Import & return the getfilter function."""
    filter = import_module("filter", "hass-addon-sunsynk")
    _LOGGER.warning("Module filter: %s", dir(filter))
    return filter.getfilter


@pytest.mark.addon
def test_last(getfilter):
    """Last filter."""
    fut = getfilter("last", None)

    assert fut.should_update() is True
    res = fut.update(55)
    assert res == 55

    for i in range(59):
        _LOGGER.error(i)
        if fut.should_update():
            assert i is False

    assert fut.should_update() is True
    res = fut.update(44)
    assert res == 44


def run_filter_seq(
    fut, *, updates: List[int], first1: bool, interval: int
) -> Tuple[int, int, Union[float, int]]:
    """Run the filter through a sequence."""
    tick_cnt, upd_cnt, res = 0, 0, None
    for oi in range(len(updates)):
        assert res is None
        if first1 and oi == 0:
            pass  # filters always have a quick start...
        else:
            for i in range(interval - 1):
                tick_cnt += 1
                if fut.should_update():
                    assert (
                        i is False
                    ), f"expected no updates, got one at {i}/{interval-1}"
        tick_cnt += 1
        upd_cnt += 1
        assert fut.should_update() is True
        res = fut.update(updates[oi])

    assert res is not None, "the filter should have returned a value"
    return tick_cnt, upd_cnt, res


@pytest.mark.addon
def test_min(getfilter):
    """Min filter."""
    fut = getfilter("min", None)

    tick, iup, res = run_filter_seq(
        fut, updates=[50, 44, 100, 100, 100, 100], first1=True, interval=10
    )
    assert tick == 51
    assert iup == 6
    assert res == 44

    tick, iup, res = run_filter_seq(
        fut, updates=[50, 44, 22, 100, 100, 100], first1=False, interval=10
    )
    assert tick == 60
    assert iup == 6
    assert res == 22


@pytest.mark.addon
def test_mean(getfilter):
    """Mean filter."""
    fut = getfilter("mean", None)

    tick, iup, res = run_filter_seq(
        fut, updates=[50, 50, 50, 100, 100, 100], first1=True, interval=10
    )
    assert tick == 51
    assert iup == 6
    assert res == 75

    tick, iup, res = run_filter_seq(
        fut, updates=[0, 100, 50, 50, 50, 50], first1=False, interval=10
    )
    assert tick == 60
    assert iup == 6
    assert res == 50


@pytest.mark.addon
def test_step(getfilter):
    """Step filter."""
    fut = getfilter("", None)

    assert fut.should_update()
    assert fut.update(20) is None
    assert fut.should_update()
    assert fut.update(20) is None
    assert fut.should_update()
    assert fut.update(120) == 120
    assert fut.should_update()
    assert fut.update(140) is None
