"""Optionally test filter."""
import logging
from itertools import repeat
from typing import Any, List

from sunsynk.definitions import SENSORS
from sunsynk.rwsensors import RWSensor
from tests.hass_addon_sunsynk_multi import filter

_LOGGER = logging.getLogger(__name__)


def assert_sequence(fut, updates: List[Any], counts=None):
    upd_cnt, i_cnt = 0, 0
    try:
        for upd in updates:
            i_cnt += 1
            if upd is None:
                assert not fut.should_update()
                continue

            assert fut.should_update()
            upd_cnt += 1

            if isinstance(upd, tuple):  # expecting a result!
                ures = fut.update(upd[0])
                if ures is None or ures != upd[1]:
                    assert 0, f"{upd}: update({upd[0]}) expected {upd[1]} got {ures}"
            else:
                ures = fut.update(upd)
                if ures is not None:
                    assert 0, f"update({upd}) expected None, got {ures}"

    except AssertionError as err:
        assert False, f"Index {i_cnt} Update {upd_cnt} - {err}"

    if counts:
        assert counts == (i_cnt, upd_cnt)


def add_intervals(count, val0, *vals):
    """Generator to insert count intervals between values of an array."""
    assert not isinstance(val0, list)
    yield val0
    for val in vals:
        # an interval is represented as None
        yield from repeat(None, count)
        yield val


def test_last():
    """Last filter."""
    fut = filter.getfilter("last", None)

    assert_sequence(fut, add_intervals(59, *[(55, 55), (44, 44), (43, 43)]))


def test_min():
    """Min filter."""
    fut = filter.getfilter("min", None)

    sq0 = (50, 50)
    sq1 = [44, 100, 100, 100, 100, (100, 44)]
    sq2 = [100, 100, 100, 55, 100, (100, 55)]

    assert_sequence(fut, add_intervals(9, sq0, sq1, sq2))

    assert fut.should_update() is False


def test_mean():
    """Mean filter."""
    fut = filter.getfilter("mean", None)

    assert_sequence(
        fut,
        add_intervals(9, *[(50, 50), 50, 50, 50, 100, 100, (100, 75)]),
        counts=(61, 7),
    )

    assert_sequence(  # a single interval
        fut,
        [None] * 9,
        counts=(9, 0),
    )

    assert_sequence(
        fut,
        add_intervals(9, *[50, 100, 50, 50, 100, (100, 75)]),
        counts=(51, 6),
    )


def test_step():
    """Step filter."""
    fut = filter.getfilter("", None)
    assert_sequence(
        fut,
        [(20, 20), 20, 20, 20, (120, 120), 140, 140],
    )

    fut = filter.getfilter("step:100", None)
    assert_sequence(
        fut,
        [(90, 90)] + [90] * 58 + [(90, 90)],
    )

    fut = filter.getfilter("step:100", None)
    sq0 = [(10, 10)]
    sq0 += [21] * 58 + [(50, 21.3)]
    sq0 += [(150, 150), (20, 20)]
    sq0 += [21] * 58 + [(50, 21.5)]
    sq0 += [20] * 58 + [(50, 20.5)]
    sq0 += [20] * 58 + [(50, 20.5)]
    sq0 += [(1000, 1000)] + [950] * 58 + [(950, 950.8)]

    assert_sequence(fut, sq0)


def test_step_text():
    """Step filter."""
    fut = filter.getfilter("step", None)
    assert_sequence(
        fut,
        [("a", "a"), ("b", "b")],
    )


def test_rr():
    """Test round robin."""
    RROBIN = filter.RROBIN
    RROBIN.tick()

    sen = [filter.Sensor(1, "a"), filter.Sensor(2, "b"), filter.Sensor(3, "c")]
    fil = [filter.getfilter("round_robin", s) for s in sen]

    for idx in range(2):
        assert fil[idx].sensor_name is sen[idx].name
    assert RROBIN.list == list(fil)

    assert [RROBIN.idx, RROBIN.active] == [-1, []]
    RROBIN.tick()
    assert [RROBIN.idx, RROBIN.active] == [0, [fil[0]]]

    # Cycle through should_update()
    assert [f.should_update() for f in fil] == [True, False, False]
    RROBIN.tick()
    assert [f.should_update() for f in fil] == [False, True, False]
    RROBIN.tick()
    assert [f.should_update() for f in fil] == [False, False, True]
    RROBIN.tick()
    assert [f.should_update() for f in fil] == [True, False, False]


def test_suggest():
    assert filter.suggested_filter(SENSORS.all["environment_temperature"]) == "avg"
    assert filter.suggested_filter(SENSORS.all["day_battery_charge"]) == "last"
    # assert filter.suggested_filter(SENSORS.all["grid_ct_load"]) == "step"
    assert filter.suggested_filter(SENSORS.all["sd_status"]) == "last"

    rw_sensors = [s for s in SENSORS.all.values() if isinstance(s, RWSensor)]
    for s in rw_sensors:
        assert filter.suggested_filter(s) == "round_robin"
