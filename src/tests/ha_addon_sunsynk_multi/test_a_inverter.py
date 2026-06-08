"""Tests for ha_addon_sunsynk_multi.a_inverter."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

import pytest

from ha_addon_sunsynk_multi.a_inverter import AInverter
from ha_addon_sunsynk_multi.options import OPT, InverterOptions
from ha_addon_sunsynk_multi.sensor_options import DEFS, import_definitions
from sunsynk.definitions.single_phase import SENSORS
from sunsynk.pysunsynk import PySunsynk
from sunsynk.state import InverterState
from sunsynk.sunsynk import Sunsynk

P_ASYNC_CONNECTED = "sunsynk.pysunsynk.AsyncModbusTcpClient.connected"
P_CONNECT = "sunsynk.pysunsynk.AsyncModbusTcpClient.connect"
P_READ_HR = "sunsynk.pysunsynk.AsyncModbusTcpClient.read_holding_registers"


@patch(P_ASYNC_CONNECTED, new_callable=PropertyMock)
@patch(P_CONNECT, new_callable=AsyncMock)
@patch(P_READ_HR, new_callable=AsyncMock)
async def test_ss_tcp_read(
    read_holding_reg: AsyncMock,
    _connect: AsyncMock,
    async_connect: PropertyMock,
    state: InverterState,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Simulate a timeout during retry read.

    https://github.com/kellerza/sunsynk/issues/180
    Also see sunsynk.test_pysunsynk.
    """
    read_holding_reg.side_effect = asyncio.exceptions.CancelledError

    ss = PySunsynk(port="tcp://1.1.1.1")
    ss.state = state
    ss.state.track(SENSORS.rated_power)
    ss.state.track(SENSORS.serial)

    # Ensure we can read
    async_connect.return_value = 1

    inv_opt = InverterOptions(modbus_id=1, ha_prefix="test")
    AInverter.add_connector(inv_opt, ss)

    # AInverter.read_sensors_retry
    ist = AInverter(index=0, opt=inv_opt, state=state, ss={})  # type:ignore[arg-type]

    sensors = [SENSORS.rated_power]

    with pytest.raises(asyncio.exceptions.CancelledError):
        await ist.read_sensors(sensors=sensors)

    res = await ist.read_sensors_retry(sensors=sensors)
    assert res is False
    assert "Could not read" not in caplog.text

    # more sensors to retry individual
    sensors.append(SENSORS.serial)

    res = await ist.read_sensors_retry(sensors=sensors)
    assert res is False
    assert "Could not read" in caplog.text


async def test_stale_skip_after_successive_read_errors(state: InverterState) -> None:
    """Enter stale quiet after successive read failures; last failure does not raise."""
    AInverter.connectors.clear()
    old_a = OPT.stale_inverter_after_timeouts
    old_s = OPT.stale_inverter_skip_seconds
    try:
        OPT.stale_inverter_after_timeouts = 2
        OPT.stale_inverter_skip_seconds = 60

        inv_opt = InverterOptions(
            modbus_id=1,
            ha_prefix="st",
            serial_nr="888",
            port="tcp://stale-skip-test:502",
            driver="",
        )
        mock_ss = MagicMock(spec=Sunsynk)
        mock_ss.read_sensors = AsyncMock(
            side_effect=[ValueError("crc"), TimeoutError("timeout")]
        )
        mock_ss.connect = AsyncMock()
        AInverter.add_connector(inv_opt, mock_ss)

        import_definitions()
        state.track(DEFS.serial)
        ist = AInverter(index=0, opt=inv_opt, state=state, ss={})  # type:ignore[arg-type]

        with pytest.raises(ValueError):
            await ist.read_sensors(sensors=[DEFS.serial])
        assert ist.lifecycle == "starting"
        assert ist.read_errors == 1

        await ist.read_sensors(sensors=[DEFS.serial])
        assert ist.lifecycle == "stale_quiet"
        assert ist._stale_quiet_until > 0
        assert ist.read_errors == 2
    finally:
        OPT.stale_inverter_after_timeouts = old_a
        OPT.stale_inverter_skip_seconds = old_s
        AInverter.connectors.clear()


async def test_attempt_stale_recovery_quiet_period_skips_connect(
    state: InverterState,
) -> None:
    """During stale quiet, attempt_stale_recovery does not call connect."""
    AInverter.connectors.clear()
    old_a = OPT.stale_inverter_after_timeouts
    old_skip = OPT.stale_inverter_skip_seconds
    try:
        OPT.stale_inverter_after_timeouts = 1
        OPT.stale_inverter_skip_seconds = 60

        inv_opt = InverterOptions(
            modbus_id=1,
            ha_prefix="q",
            serial_nr="888",
            port="tcp://stale-quiet-test:502",
            driver="",
        )
        mock_ss = MagicMock(spec=Sunsynk)
        mock_ss.read_sensors = AsyncMock(side_effect=TimeoutError("timeout"))
        mock_ss.connect = AsyncMock()
        AInverter.add_connector(inv_opt, mock_ss)

        import_definitions()
        state.track(DEFS.serial)
        ist = AInverter(index=0, opt=inv_opt, state=state, ss={})  # type:ignore[arg-type]

        await ist.read_sensors(sensors=[DEFS.serial])
        assert ist.lifecycle == "stale_quiet"

        await ist.lifecycle_attempt_recovery()
        mock_ss.connect.assert_not_called()
    finally:
        OPT.stale_inverter_after_timeouts = old_a
        OPT.stale_inverter_skip_seconds = old_skip
        AInverter.connectors.clear()


async def test_attempt_stale_recovery_probe_success_returns_to_running(
    state: InverterState,
) -> None:
    """After quiet elapses, probe reads serial and resumes when it matches config."""
    AInverter.connectors.clear()
    old_skip = OPT.stale_inverter_skip_seconds
    try:
        OPT.stale_inverter_skip_seconds = 60

        inv_opt = InverterOptions(
            modbus_id=1,
            ha_prefix="ok",
            serial_nr="888",
            port="tcp://stale-probe-ok:502",
            driver="",
        )
        mock_ss = MagicMock()

        async def probe_sets_serial(*_a: object, **_k: object) -> None:
            state.values[DEFS.serial] = "888"

        mock_ss.read_sensors = AsyncMock(side_effect=probe_sets_serial)
        mock_ss.connect = AsyncMock()
        AInverter.add_connector(inv_opt, mock_ss)

        import_definitions()
        state.track(DEFS.serial)
        ist = AInverter(index=0, opt=inv_opt, state=state, ss={})  # type:ignore[arg-type]

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
        ):
            await ist.lifecycle_enter_stale("test setup")
            mono[0] = 10_000.0
            await ist.lifecycle_attempt_recovery()

        mock_ss.connect.assert_called_once()
        mock_ss.read_sensors.assert_called_once()
        assert ist.lifecycle == "running"
    finally:
        OPT.stale_inverter_skip_seconds = old_skip
        AInverter.connectors.clear()


async def test_attempt_stale_recovery_probe_failure_reenters_stale(
    state: InverterState,
) -> None:
    """If the serial probe read fails, lifecycle returns to stale_quiet."""
    AInverter.connectors.clear()
    old_skip = OPT.stale_inverter_skip_seconds
    try:
        OPT.stale_inverter_skip_seconds = 60

        inv_opt = InverterOptions(
            modbus_id=1,
            ha_prefix="bad",
            serial_nr="888",
            port="tcp://stale-probe-fail:502",
            driver="",
        )
        mock_ss = MagicMock()
        mock_ss.read_sensors = AsyncMock(side_effect=OSError("bus"))
        mock_ss.connect = AsyncMock()
        AInverter.add_connector(inv_opt, mock_ss)

        import_definitions()
        state.track(DEFS.serial)
        ist = AInverter(index=0, opt=inv_opt, state=state, ss={})  # type:ignore[arg-type]

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
        ):
            await ist.lifecycle_enter_stale("test setup")
            mono[0] = 10_000.0
            await ist.lifecycle_attempt_recovery()

        mock_ss.connect.assert_called_once()
        assert ist.lifecycle == "stale_quiet"
    finally:
        OPT.stale_inverter_skip_seconds = old_skip
        AInverter.connectors.clear()
