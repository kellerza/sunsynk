#!/usr/bin/env python3
"""Run the addon."""

import logging

from sunsynk import Sensor, Sunsynk, ValType

from .a_inverter import STATE, AInverter
from .a_sensor import MQTT
from .options import InverterOptions, Options
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


def init_connector(opt: Options, iopt: InverterOptions) -> None:
    """Sunsynk driver factory."""
    iopt.driver = iopt.driver or opt.driver
    if (iopt.port, iopt.driver) in AInverter.connectors:
        _LOG.debug("Reusing driver for port, driver (%s, %s)", iopt.port, iopt.driver)
        return

    factory: type[Sunsynk]
    port_prefix = ""
    kwargs = {}

    if iopt.driver == "pymodbus":
        from sunsynk.pysunsynk import PySunsynk  # noqa: PLC0415

        factory = PySunsynk
    elif iopt.driver == "umodbus":
        from sunsynk.usunsynk import USunsynk  # noqa: PLC0415

        factory = USunsynk
        port_prefix = "serial://"
    elif iopt.driver == "solarman":
        from sunsynk.solarmansunsynk import SolarmanSunsynk  # noqa: PLC0415

        factory = SolarmanSunsynk
        port_prefix = "tcp://"
        kwargs["dongle_serial_number"] = iopt.dongle_serial_number
    else:
        raise ValueError(
            f"Invalid DRIVER: {iopt.driver}. Expected umodbus, pymodbus, solarman"
        )

    if "dongle_serial_number" not in kwargs and iopt.dongle_serial_number:
        _LOG.warning("Ignoring dongle_serial_number for non-solarman driver")

    ss = factory(
        port=iopt.port if iopt.port else port_prefix + opt.debug_device,
        server_id=iopt.modbus_id,
        timeout=opt.timeout,
        read_sensors_batch_size=opt.read_sensors_batch_size,
        allow_gap=opt.read_allow_gap,
        state=None,  # type:ignore[arg-type]
        **kwargs,  # type:ignore[arg-type]
    )
    _LOG.debug("Driver: %s - inv:%s", ss, iopt)
    AInverter.add_connector(iopt, ss)


def init_driver(opt: Options) -> None:
    """Init Sunsynk driver for each inverter."""
    STATE.clear()
    for idx, inv in enumerate(opt.inverters):
        init_connector(opt, inv)
        ist = AInverter(opt=inv, index=idx)
        ist.state.onchange = sensor_on_update
        STATE.append(ist)
