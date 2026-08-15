"""Tests for ha_addon_sunsynk_multi.a_inverter."""

import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ha_addon_sunsynk_multi.a_inverter import AInverter
from ha_addon_sunsynk_multi.a_sensor import MQTT
from ha_addon_sunsynk_multi.options import OPT, InverterOptions
from ha_addon_sunsynk_multi.sensor_options import DEFS, import_definitions
from sunsynk.definitions.single_phase import SENSORS
from sunsynk.state import InverterState
from sunsynk.sunsynk import Sunsynk

# Avoid lifecycle MQTT publish calling wait_connected() (no broker in unit tests).
P_MOCK_MQTT_PUBLISH_AVAILABILITY = patch(
    "ha_addon_sunsynk_multi.a_inverter.MQTT.publish_availability",
    new_callable=AsyncMock,
)


def _ist(inv_opt: InverterOptions, inv: Sunsynk, *, state: InverterState) -> AInverter:
    """Build an AInverter with the given Sunsynk."""
    return AInverter(index=0, opt=inv_opt, inv=inv, state=state, ss={})  # type: ignore[arg-type]


async def test_set_lifecycle_publish_availability_uses_retain() -> None:
    """Per-inverter lifecycle MQTT must be retained (HA after broker restart)."""
    inv_opt = InverterOptions(
        modbus_id=1, ha_prefix="my_inv", serial_nr="1", port="tcp://x:502"
    )
    mock_ss = MagicMock(spec=Sunsynk)
    mock_ss.read_sensors = AsyncMock()
    mock_ss.connect = AsyncMock()
    ist = AInverter(index=0, opt=inv_opt, inv=mock_ss, ss={})  # type: ignore[arg-type]

    mock_client = MagicMock()
    mock_client.is_connected.return_value = True
    with patch.object(MQTT, "client", mock_client):
        with patch.object(
            MQTT, "publish_availability", new_callable=AsyncMock
        ) as pub_av:
            await ist.set_lifecycle("running")
    pub_av.assert_awaited_once_with("SS/availability_1_my_inv", True, retain=True)


async def test_ss_tcp_read(
    state: InverterState,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Simulate a timeout during retry read.

    https://github.com/kellerza/sunsynk/issues/180
    """
    unit = MagicMock()
    unit.read_holding_registers = AsyncMock(side_effect=TimeoutError("test"))
    ss = Sunsynk(unit=unit, port="tcp://1.1.1.1", state=state)
    ss.state.track(SENSORS.rated_power)
    ss.state.track(SENSORS.serial)

    inv_opt = InverterOptions(modbus_id=1, ha_prefix="test")
    ist = _ist(inv_opt, ss, state=state)
    # Default _stale_enter_at is inf until a successful read arms the deadline.

    sensors = [SENSORS.rated_power]

    assert await ist.read_sensors(sensors=sensors) is False

    res = await ist.read_sensors_retry(sensors=sensors)
    assert res is False
    assert "Could not read" not in caplog.text

    # more sensors to retry individual
    sensors.append(SENSORS.serial)

    res = await ist.read_sensors_retry(sensors=sensors)
    assert res is False
    assert "Could not read" in caplog.text


async def test_stale_skip_after_successive_read_errors(state: InverterState) -> None:
    """Enter stale quiet after read failures once the grace window (seconds) has elapsed."""
    old_a = OPT.stale_inverter_after_seconds
    old_s = OPT.stale_inverter_skip_seconds
    try:
        OPT.stale_inverter_after_seconds = 2
        OPT.stale_inverter_skip_seconds = 60

        inv_opt = InverterOptions(
            modbus_id=1,
            ha_prefix="st",
            serial_nr="888",
            port="tcp://stale-skip-test:502",
        )
        mock_ss = MagicMock(spec=Sunsynk)
        eg_fail = ExceptionGroup("read", (RuntimeError("crc"),))
        mock_ss.read_sensors = AsyncMock(side_effect=[eg_fail, eg_fail])
        mock_ss.connect = AsyncMock()

        import_definitions()
        state.track(DEFS.serial)
        ist = _ist(inv_opt, mock_ss, state=state)

        with P_MOCK_MQTT_PUBLISH_AVAILABILITY:
            # Finite deadline: failures before deadline only increment read_errors.
            ist._stale_enter_at = time.monotonic() + 100.0
            assert await ist.read_sensors(sensors=[DEFS.serial]) is False
            assert ist.lifecycle == "starting"
            assert ist.read_errors == 1

            ist._stale_enter_at = time.monotonic() - 1.0
            assert await ist.read_sensors(sensors=[DEFS.serial]) is False
            assert ist.lifecycle == "stale_quiet"
            assert ist._stale_quiet_until > 0
            assert ist.read_errors == 2
    finally:
        OPT.stale_inverter_after_seconds = old_a
        OPT.stale_inverter_skip_seconds = old_s


async def test_attempt_stale_recovery_quiet_period_skips_connect(
    state: InverterState,
) -> None:
    """During stale quiet, attempt_stale_recovery does not call connect."""
    old_a = OPT.stale_inverter_after_seconds
    old_skip = OPT.stale_inverter_skip_seconds
    try:
        OPT.stale_inverter_after_seconds = 1
        OPT.stale_inverter_skip_seconds = 60

        inv_opt = InverterOptions(
            modbus_id=1,
            ha_prefix="q",
            serial_nr="888",
            port="tcp://stale-quiet-test:502",
        )
        mock_ss = MagicMock(spec=Sunsynk)
        mock_ss.read_sensors = AsyncMock(
            side_effect=ExceptionGroup("read", (TimeoutError("timeout"),))
        )
        mock_ss.connect = AsyncMock()

        import_definitions()
        state.track(DEFS.serial)
        ist = _ist(inv_opt, mock_ss, state=state)
        # Arm stale: failures only count after a successful read set a finite deadline;
        # simulate "deadline already passed" for this scenario.
        ist._stale_enter_at = time.monotonic() - 1.0

        with P_MOCK_MQTT_PUBLISH_AVAILABILITY:
            assert await ist.read_sensors(sensors=[DEFS.serial]) is False
            assert ist.lifecycle == "stale_quiet"

            await ist.lifecycle_attempt_recovery()
        mock_ss.connect.assert_not_called()
    finally:
        OPT.stale_inverter_after_seconds = old_a
        OPT.stale_inverter_skip_seconds = old_skip


async def test_attempt_stale_recovery_probe_success_returns_to_running(
    state: InverterState,
) -> None:
    """After quiet elapses, probe reads serial and resumes when it matches config."""
    old_skip = OPT.stale_inverter_skip_seconds
    try:
        OPT.stale_inverter_skip_seconds = 60

        inv_opt = InverterOptions(
            modbus_id=1,
            ha_prefix="ok",
            serial_nr="888",
            port="tcp://stale-probe-ok:502",
        )
        mock_ss = MagicMock()

        async def probe_sets_serial(*_a: object, **_k: object) -> None:
            state.values[DEFS.serial] = "888"

        mock_ss.read_sensors = AsyncMock(side_effect=probe_sets_serial)
        mock_ss.connect = AsyncMock()

        import_definitions()
        state.track(DEFS.serial)
        ist = _ist(inv_opt, mock_ss, state=state)

        mono = [0.0]

        def fake_monotonic() -> float:
            return mono[0]

        with (
            patch(
                "ha_addon_sunsynk_multi.a_inverter.time.monotonic",
                new=fake_monotonic,
            ),
            patch(
                "ha_addon_sunsynk_multi.a_inverter.asyncio.sleep",
                new_callable=AsyncMock,
            ),
            P_MOCK_MQTT_PUBLISH_AVAILABILITY,
        ):
            await ist.lifecycle_enter_stale("test setup")
            mono[0] = 10_000.0
            await ist.lifecycle_attempt_recovery()

        mock_ss.connect.assert_called_once()
        mock_ss.read_sensors.assert_called_once()
        assert ist.lifecycle == "running"
    finally:
        OPT.stale_inverter_skip_seconds = old_skip


async def test_attempt_stale_recovery_probe_failure_reenters_stale(
    state: InverterState,
) -> None:
    """If the serial probe read fails, lifecycle returns to stale_quiet."""
    old_skip = OPT.stale_inverter_skip_seconds
    try:
        OPT.stale_inverter_skip_seconds = 60

        inv_opt = InverterOptions(
            modbus_id=1,
            ha_prefix="bad",
            serial_nr="888",
            port="tcp://stale-probe-fail:502",
        )
        mock_ss = MagicMock()
        mock_ss.read_sensors = AsyncMock(side_effect=OSError("bus"))
        mock_ss.connect = AsyncMock()

        import_definitions()
        state.track(DEFS.serial)
        ist = _ist(inv_opt, mock_ss, state=state)

        mono = [0.0]

        def fake_monotonic() -> float:
            return mono[0]

        with (
            patch(
                "ha_addon_sunsynk_multi.a_inverter.time.monotonic",
                new=fake_monotonic,
            ),
            patch(
                "ha_addon_sunsynk_multi.a_inverter.asyncio.sleep",
                new_callable=AsyncMock,
            ),
            P_MOCK_MQTT_PUBLISH_AVAILABILITY,
        ):
            await ist.lifecycle_enter_stale("test setup")
            mono[0] = 10_000.0
            await ist.lifecycle_attempt_recovery()

        mock_ss.connect.assert_called_once()
        assert ist.lifecycle == "stale_quiet"
    finally:
        OPT.stale_inverter_skip_seconds = old_skip
