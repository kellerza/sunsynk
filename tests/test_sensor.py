import logging
from typing import Sequence

import pytest

import sunsynk.definitions as defs
from sunsynk.sensor import Sensor, group_sensors

_LOGGER = logging.getLogger(__name__)

pytestmark = pytest.mark.asyncio


# @pytest.fixture
# def sensors():
#     """Fixture to create some sensors."""
#     yield [
#         (402, True, Sensor("6400_00262200", "s_402", "W")),
#         (3514, True, Sensor("6400_00260100", "s_3514", "W", 1000)),
#     ]


async def test_sen():

    a = []
    s = Sensor(0, "t1").append_to(a)

    assert a[0] is s


async def test_group() -> None:
    sen = [
        Sensor(10, "10"),
        Sensor(11, "11"),
        Sensor(12, "12"),
        Sensor(20, "20"),
    ]
    g = group_sensors(sen)
    assert g == [[10, 11, 12], [20]]


async def test_all_groups() -> None:
    s = [getattr(defs, s) for s in dir(defs) if isinstance(getattr(defs, s), Sensor)]
    for i in range(2, 6):
        _LOGGER.warning("waste with %d gap: %s", i, waste(group_sensors(s, i)))

    grp = group_sensors(s)

    grplen = [len(i) for i in grp]

    assert grplen[:1] == [5]
    assert grplen[-1:] == [1]


def waste(groups) -> Sequence[int]:
    """Calculate amount of unused registers in this grouping."""
    return [sum(b - a for a, b in zip(g[:-1], g[1:])) for g in groups]


def test_ids() -> None:
    """test sensor ids."""
    for nme, val in defs.all_sensors().items():
        assert nme == val.id
