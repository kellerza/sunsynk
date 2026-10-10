"""Tests for re-sending states when Home Assistant comes back online."""

from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, MagicMock, call

import pytest

from ha_addon_sunsynk_multi import a_inverter
from ha_addon_sunsynk_multi.a_inverter import AInverter, republish_all_states
from ha_addon_sunsynk_multi.a_sensor import MQTT, ASensor
from ha_addon_sunsynk_multi.sensor_options import SensorOption
from sunsynk.sensors import Sensor
from sunsynk.sunsynk import ValType

from .conftest import NOSCHEDULE, ist_factory


def _asensor(
    name: str, value: ValType, *, retain: bool = False, entity: bool = True
) -> ASensor:
    """Return an ASensor whose last published value is `value`."""
    ent = None
    if entity:
        ent = MagicMock()
        ent.send_state = AsyncMock()
    return ASensor(
        opt=SensorOption(
            sensor=Sensor(1, name, "W"), schedule=NOSCHEDULE, visible=True
        ),
        entity=ent,
        retain=retain,
        _last=value,
    )


def _running_ist() -> AInverter:
    ist = ist_factory()
    ist.lifecycle = "running"
    ist.ss = {
        "power": _asensor("power", 100),
        "energy": _asensor("energy", 12.3),
        "never": _asensor("never", None),
        "rw": _asensor("rw", 50, retain=True),
        "hidden": _asensor("hidden", 7, entity=False),
    }
    return ist


async def test_republish_states_sends_last_published_non_retained() -> None:
    """Only non-retained sensors with an entity and a published value are re-sent."""
    ist = _running_ist()

    assert await ist.republish_states() == 2

    ist.ss["power"].entity.send_state.assert_awaited_once_with(MQTT, 100)  # type: ignore[union-attr]
    ist.ss["energy"].entity.send_state.assert_awaited_once_with(MQTT, 12.3)  # type: ignore[union-attr]
    ist.ss["never"].entity.send_state.assert_not_awaited()  # type: ignore[union-attr]
    ist.ss["rw"].entity.send_state.assert_not_awaited()  # type: ignore[union-attr]
    # never written by a republish
    assert ist.ss["power"].value == 100


@pytest.mark.parametrize("lifecycle", ["starting", "stale_quiet", "stale_probing"])
async def test_republish_states_only_when_running(lifecycle: str) -> None:
    """Do not re-send values from an inverter that is not being read."""
    ist = _running_ist()
    ist.lifecycle = lifecycle  # type: ignore[assignment]

    assert await ist.republish_states() == 0
    ist.ss["power"].entity.send_state.assert_not_awaited()  # type: ignore[union-attr]


async def test_republish_states_resends_value_published_meanwhile() -> None:
    """A publish in flight updates _last after our send: re-send the newer value."""
    ist = _running_ist()
    power = ist.ss["power"]

    async def send_state(_client: Any, payload: Any, **_kw: Any) -> None:
        if payload == 100:
            power._last = 900  # the in-flight ASensor.publish(900) completes

    power.entity.send_state.side_effect = send_state  # type: ignore[union-attr]

    await ist.republish_states()

    assert power.entity.send_state.await_args_list == [call(MQTT, 100), call(MQTT, 900)]  # type: ignore[union-attr]
    assert power.value == 900


async def test_republish_states_send_failure_does_not_stop_the_pass() -> None:
    """A failed send is logged and the other sensors are still re-sent."""
    ist = _running_ist()
    ist.ss["power"].entity.send_state.side_effect = ConnectionError("broker gone")  # type: ignore[union-attr]

    assert await ist.republish_states() == 1

    ist.ss["energy"].entity.send_state.assert_awaited_once_with(MQTT, 12.3)  # type: ignore[union-attr]


async def test_republish_all_states_every_running_inverter_every_pass(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Each pass re-sends the states of every running inverter, and only those."""
    ist1, ist2 = _running_ist(), _running_ist()
    ist2.lifecycle = "starting"
    monkeypatch.setattr(a_inverter, "STATE", [ist1, ist2])

    await republish_all_states(delays=(0, 0))

    assert ist1.ss["power"].entity.send_state.await_count == 2  # type: ignore[union-attr]
    assert ist1.ss["energy"].entity.send_state.await_count == 2  # type: ignore[union-attr]
    ist2.ss["power"].entity.send_state.assert_not_awaited()  # type: ignore[union-attr]


async def test_republish_all_states_default_delays_from_ha_online(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The passes run 10 s and 60 s after HA came online, not 60 s after pass one."""
    clock = [1000.0]
    sleeps: list[float] = []

    async def fake_sleep(seconds: float) -> None:
        sleeps.append(seconds)
        clock[0] += seconds

    async def pass_takes_2s() -> int:
        clock[0] += 2
        return 1

    ist = _running_ist()
    monkeypatch.setattr(ist, "republish_states", pass_takes_2s)
    monkeypatch.setattr(a_inverter, "STATE", [ist])
    monkeypatch.setattr(a_inverter, "asyncio", SimpleNamespace(sleep=fake_sleep))
    monkeypatch.setattr(a_inverter, "time", SimpleNamespace(monotonic=lambda: clock[0]))

    await republish_all_states()

    assert sleeps == [10, 48]
