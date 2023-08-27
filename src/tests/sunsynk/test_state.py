"""Sunsynk sensor state."""
import logging

import pytest

from sunsynk.rwsensors import SystemTimeRWSensor
from sunsynk.sensors import Sensor
from sunsynk.state import InverterState

_LOGGER = logging.getLogger(__name__)


def test_history(state: InverterState) -> None:
    """Test history with numeric values."""
    a = Sensor(1, "Some Value")
    state.track(a)

    state.update({1: 100})
    assert state[a] == 100
    assert state.history[a] == [100]

    state.update({1: 200})
    assert state[a] == 200
    assert state.history[a] == [100, 200]

    state.update({1: 300})
    assert state[a] == 300
    assert state.history[a] == [100, 200, 300]

    assert a not in state.historynn

    assert state.history_average(a) == 250
    assert state.history[a] == [250]


def test_history_raise(state: InverterState) -> None:
    """Test if we have a ValueError."""
    a = Sensor(2, "Some Value")
    state.track(a)
    with pytest.raises(ValueError):
        state.history_average(a)

    state.update({2: 100})
    assert state[a] == 100
    assert state.history_average(a) == 100
    assert state.history[a] == [100]

    state.update({2: 111})
    assert state.history[a] == [100, 111]
    assert state.history_average(a) == 111
    assert state.history[a] == [111]


def test_history_nn(state: InverterState) -> None:
    """Test history with non-numeric values."""
    a = SystemTimeRWSensor((1, 2, 3), "Some Value")
    state.track(a)

    state.update({1: 1, 2: 2, 3: 3})
    assert state.historynn[a] == [None, "2000-01-00 2:00:03"]
    assert a not in state.history

    state.update({1: 12, 2: 5, 3: 44})
    assert state.historynn[a] == ["2000-01-00 2:00:03", "2000-12-00 5:00:44"]
    assert a not in state.history
