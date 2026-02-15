"""Addon fixtures."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

from mqtt_entity import MQTTDevice

from ha_addon_sunsynk_multi.a_inverter import AInverter, InverterOptions
from ha_addon_sunsynk_multi.timer_schedule import Schedule
from sunsynk.sunsynk import InverterState

NOSCHEDULE = Schedule("no_unit", read_every=1, report_every=1)


def ist_factory(
    serial: str = "888",
    ha_prefix: str = "ss1",
    modbus_id: int = 1,
    *,
    port: str = "tcp://test:123",
) -> AInverter:
    """Return an inverter test instance."""
    state = MagicMock(InverterState)
    state.historynn = MagicMock()
    state.history = MagicMock()

    res = AInverter(
        index=0,
        opt=InverterOptions(
            ha_prefix=ha_prefix,
            serial_nr=serial,
            modbus_id=modbus_id,
            port=port,
            driver="",
        ),
        mqtt_dev=MQTTDevice(identifiers=[serial], components={}),
        state=state,  # type:ignore[arg-type]
    )

    res.connectors[(port, "")] = (AsyncMock(), asyncio.Lock())  # type:ignore[assignment]
    res.read_sensors = AsyncMock()  # type: ignore[method-assign]
    res.publish_sensors = AsyncMock()  # type: ignore[method-assign]
    return res
