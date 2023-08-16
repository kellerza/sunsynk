"""Register."""
# type: ignore
from typing import cast
from unittest.mock import MagicMock, call

from sunsynk.rwsensors import NumberRWSensor, Sensor
from sunsynk.state import InverterState


def test_on_changed(state: InverterState) -> None:
    """Test update and on_change."""
    onchange = cast(MagicMock, state.onchange)

    s1 = NumberRWSensor((1,), "S1", min=1, max=50)
    state.track(s1)

    assert state.values[s1] is None

    state.update({1: 5})
    assert state.values[s1] == 5
    assert onchange.call_count == 1
    assert onchange.call_args == call(s1, 5, None)

    state.update({1: 10})
    assert state.values[s1] == 10
    assert onchange.call_count == 2
    assert onchange.call_args == call(s1, 10, 5)

    s2 = Sensor(1, "S2", "")
    state.track(s2)
    assert state.values[s2] is None

    onchange.call_args_list.clear()
    state.update({1: 20})
    assert state.values[s1] == 20
    assert state.values[s2] == 20
    assert onchange.call_count == 4
    assert onchange.call_args_list == [
        call(s1, 20, 10),
        call(s2, 20, None),
    ]
