#!/usr/bin/env python3
"""Run the addon."""

import logging
from typing import cast

from modbus_connection.tmodbus import ModbusConnection

from sunsynk import Sensor, Sunsynk, ValType
from sunsynk.connection import open_connection
from sunsynk.solarman import SolarmanUnit
from sunsynk.sunsynk import HoldingUnit

from .a_inverter import STATE, AInverter
from .a_sensor import MQTT
from .options import InverterOptions, Options, is_solarman_port
from .sensor_options import SOPT

_LOG = logging.getLogger(":")


HASS_DISCOVERY_INFO_UPDATE_QUEUE: set[Sensor] = set()
"""Update Sensor discovery info."""


async def callback_discovery_info(now: int) -> None:
    """Update HASS discovery & write RWSensors."""
    # Flush any pending discovery info updates
    if HASS_DISCOVERY_INFO_UPDATE_QUEUE:
        for ist in STATE:
            ist.hass_create_discovery_info()
        await MQTT.publish_discovery_info()
        HASS_DISCOVERY_INFO_UPDATE_QUEUE.clear()

    # Publish statistics
    if now % 120 == 0:
        for ist in STATE:
            await ist.publish_stats(120)


def sensor_on_update(sen: Sensor, _new: ValType, _old: ValType) -> None:
    """React to sensor updates."""
    if sen not in SOPT or not SOPT[sen].affects:
        return
    _LOG.debug(
        "%s changed: Enqueue discovery info updates for %s",
        sen.name,
        ", ".join(s.id for s in SOPT[sen].affects),
    )
    HASS_DISCOVERY_INFO_UPDATE_QUEUE.update(SOPT[sen].affects)


def _shared_modbus_connection(opt: Options, *, port: str) -> ModbusConnection:
    """One ``ModbusConnection`` per port; reused across MODBUS_IDs."""
    conn = AInverter.connections.get(port)
    if conn is None:
        conn = open_connection(
            port, timeout=opt.timeout, message_spacing=opt.read_message_spacing
        )
        AInverter.connections[port] = conn
        _LOG.debug("Opened Modbus connection for %s", port)
    else:
        _LOG.debug("Reusing Modbus connection for %s", port)
    return conn


def create_sunsynk(opt: Options, iopt: InverterOptions) -> Sunsynk:
    """Build a per-inverter ``Sunsynk`` (shared connection when Modbus)."""
    port = iopt.port or opt.debug_device

    if is_solarman_port(port):
        if port in AInverter.solarman_ports:
            _LOG.warning("Reusing a Solarman port is not supported (%s)", port)
        AInverter.solarman_ports.add(port)
        unit = SolarmanUnit(
            port=port,
            dongle_serial_number=iopt.dongle_serial_number,
            server_id=iopt.modbus_id,
            timeout=opt.timeout,
        )
        ss = Sunsynk(
            unit=unit,
            port=port,
            timeout=opt.timeout,
            read_sensors_batch_size=opt.read_sensors_batch_size,
            allow_gap=opt.read_allow_gap,
        )
    else:
        conn = _shared_modbus_connection(opt, port=port)
        ss = Sunsynk(
            # ponytail: see Sunsynk.from_url — TmodbusUnit vs HoldingUnit Coroutine typing
            unit=cast(HoldingUnit, conn.for_unit(iopt.modbus_id)),
            connection=conn,
            port=port,
            timeout=opt.timeout,
            read_sensors_batch_size=opt.read_sensors_batch_size,
            allow_gap=opt.read_allow_gap,
        )

    _LOG.debug("Sunsynk: %s - inv:%s", ss, iopt)
    return ss


def init_driver(opt: Options) -> None:
    """Init Sunsynk driver for each inverter."""
    STATE.clear()
    AInverter.connections.clear()
    AInverter.solarman_ports.clear()
    for idx, inv in enumerate(opt.inverters):
        ss = create_sunsynk(opt, inv)
        ist = AInverter(opt=inv, index=idx, inv=ss)
        ss.state = ist.state
        ist.state.onchange = sensor_on_update
        STATE.append(ist)
