#!/usr/bin/env python3
"""Run the addon."""

import logging

from sunsynk.helpers import ValType
from sunsynk.sunsynk import Sensor, Sunsynk

from .a_inverter import STATE, AInverter
from .a_sensor import MQTT
from .options import Options
from .sensor_options import SOPT

_LOGGER = logging.getLogger(":")


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
    _LOGGER.debug(
        "%s changed: Enqueue discovery info updates for %s",
        sen.name,
        ", ".join(s.id for s in SOPT[sen].affects),
    )
    HASS_DISCOVERY_INFO_UPDATE_QUEUE.update(SOPT[sen].affects)


def init_driver(opt: Options) -> None:
    """Init Sunsynk driver for each inverter."""
    factory = Sunsynk
    port_prefix = ""

    if opt.driver == "pymodbus":
        from sunsynk.pysunsynk import PySunsynk  # noqa: PLC0415

        factory = PySunsynk
    elif opt.driver == "umodbus":
        from sunsynk.usunsynk import USunsynk  # noqa: PLC0415

        factory = USunsynk
        port_prefix = "serial://"
    elif opt.driver == "solarman":
        from sunsynk.solarmansunsynk import SolarmanSunsynk  # noqa: PLC0415

        factory = SolarmanSunsynk  # type: ignore[]
        port_prefix = "tcp://"
    else:
        raise ValueError(
            f"Invalid DRIVER: {opt.driver}. Expected umodbus, pymodbus, solarman"
        )

    STATE.clear()

    for idx, inv in enumerate(opt.inverters):
        suns = factory(
            port=inv.port if inv.port else port_prefix + opt.debug_device,
            server_id=inv.modbus_id,
            timeout=opt.timeout,
            read_sensors_batch_size=opt.read_sensors_batch_size,
            allow_gap=opt.read_allow_gap,
        )
        if hasattr(suns, "dongle_serial_number"):
            suns.dongle_serial_number = inv.dongle_serial_number  # type: ignore[]
        _LOGGER.debug("Driver: %s - inv:%s", suns, inv)
        suns.state.onchange = sensor_on_update

        STATE.append(AInverter(inv=suns, ss={}, opt=inv, index=idx))
