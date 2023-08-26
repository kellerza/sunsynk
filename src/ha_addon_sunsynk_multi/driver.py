#!/usr/bin/env python3
"""Run the addon."""
import logging

from ha_addon_sunsynk_multi.a_inverter import STATE, AInverter
from ha_addon_sunsynk_multi.a_sensor import MQTT
from ha_addon_sunsynk_multi.options import OPT, Options
from ha_addon_sunsynk_multi.sensor_options import SOPT
from sunsynk.helpers import ValType
from sunsynk.sunsynk import Sensor, Sunsynk, SunsynkInitParameters

_LOGGER = logging.getLogger(":")


HASS_DISCOVERY_INFO_UPDATE_QUEUE: set[Sensor] = set()
"""Update Sensor discovery info."""


async def callback_discovery_info(now: int) -> None:
    """Called every tick to update HASS discovery & write RWSensors."""
    # Flush any pending discovery info updates
    if HASS_DISCOVERY_INFO_UPDATE_QUEUE:
        for ist in STATE:
            states = [ist.ss[s.id] for s in HASS_DISCOVERY_INFO_UPDATE_QUEUE]
            ents = [s.create_entity(s.entity, ist=ist) for s in states if not s.hidden]
            await MQTT.connect(OPT)
            await MQTT.publish_discovery_info(entities=ents, remove_entities=False)
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
    """Setup the Sunsynk drivers for each inverter and inits STATE."""
    # pylint: disable=import-outside-toplevel

    factory = Sunsynk
    port_prefix = ""

    if opt.driver == "pymodbus":
        from sunsynk.pysunsynk import PySunsynk

        factory = PySunsynk
    elif opt.driver == "umodbus":
        from sunsynk.usunsynk import USunsynk

        factory = USunsynk
        port_prefix = "serial://"
    elif opt.driver == "solarman":
        from sunsynk.solarmansunsynk import SolarmanSunsynk

        factory = SolarmanSunsynk
        port_prefix = "tcp://"
    else:
        raise ValueError(
            f"Invalid DRIVER: {opt.driver}. Expected umodbus, pymodbus, solarman"
        )

    STATE.clear()

    for inv in opt.inverters:
        kwargs: SunsynkInitParameters = {
            "port": inv.port if inv.port else port_prefix + opt.debug_device,
            "server_id": inv.modbus_id,
            "timeout": opt.timeout,
            "read_sensors_batch_size": opt.read_sensors_batch_size,
            "allow_gap": opt.read_allow_gap,
        }

        if opt.driver == "solarman":
            kwargs["dongle_serial_number"] = inv.dongle_serial_number  # type: ignore

        _LOGGER.debug("%s driver options: %s", opt.driver, kwargs)
        suns = factory(**kwargs)
        suns.state.onchange = sensor_on_update

        STATE.append(AInverter(inv=suns, ss={}, opt=inv))
