#!/usr/bin/env python3
"""Run the addon."""
import asyncio
import logging
import sys
from asyncio.events import AbstractEventLoop
from json import loads
from math import modf
from pathlib import Path
from typing import Dict, List

import yaml
from filter import Filter, getfilter, suggested_filter
from mqtt import MQTT, Device, Entity, SensorEntity
from options import OPT, SS_TOPIC
from profiles import profile_add_entities, profile_poll

import sunsynk.definitions as ssdefs
from sunsynk import Sunsynk

_LOGGER = logging.getLogger(__name__)


SENSORS: List[Filter] = []


SUNSYNK = Sunsynk()


async def publish_sensors(sensors: List[Filter], *, force: bool = False) -> None:
    """Publish sensors."""
    for fsen in sensors:
        res = fsen.sensor.value
        if not force:
            res = fsen.update(res)
            if res is None:
                continue
        if isinstance(res, float):
            if modf(res)[0] == 0:
                res = int(res)
            else:
                res = f"{res:.2f}".rstrip("0")

        await MQTT.connect(OPT)
        await MQTT.publish(
            topic=f"{SS_TOPIC}/{OPT.sunsynk_id}/{fsen.sensor.id}", payload=str(res)
        )


async def hass_discover_sensors(serial: str) -> None:
    """Discover all sensors."""
    ents: List[Entity] = []
    dev = Device(
        identifiers=[OPT.sunsynk_id],
        name=f"Sunsynk Inverter {serial}",
        model=f"Inverter {serial}",
        manufacturer="Sunsynk",
    )

    for filt in SENSORS:
        sensor = filt.sensor
        ents.append(
            SensorEntity(
                name=f"{OPT.sensor_prefix} {sensor.name}".strip(),
                state_topic=f"{SS_TOPIC}/{OPT.sunsynk_id}/{sensor.id}",
                unit_of_measurement=sensor.unit,
                unique_id=f"{OPT.sunsynk_id}_{sensor.id}",
                device=dev,
            )
        )

    profile_add_entities(entities=ents, device=dev)

    await MQTT.connect(OPT)
    await MQTT.publish_discovery_info(entities=ents)


def startup() -> None:
    """Read the hassos configuration."""
    logging.basicConfig(
        format="%(asctime)s %(levelname)-7s %(message)s", level=logging.DEBUG
    )

    hassosf = Path("/data/options.json")
    if hassosf.exists():
        _LOGGER.info("Loading HASS OS configuration")
        OPT.update(loads(hassosf.read_text(encoding="utf-8")))
    else:
        _LOGGER.info(
            "Local test mode - Defaults apply. Pass MQTT host & password as arguments"
        )
        configf = Path(__file__).parent / "config.yaml"
        OPT.update(yaml.safe_load(configf.read_text()).get("options", {}))
        OPT.mqtt_host = sys.argv[1]
        OPT.mqtt_password = sys.argv[2]
        OPT.debug = 1

    MQTT.availability_topic = f"{SS_TOPIC}/{OPT.sunsynk_id}/availability"

    SUNSYNK.port = OPT.port

    if OPT.debug < 2:
        logging.basicConfig(
            format="%(asctime)s %(levelname)-7s %(message)s",
            level=logging.INFO,
            force=True,
        )

    sens = {}

    msg: Dict[str, str] = {}

    for sensor_def in OPT.sensors:
        name, _, fstr = sensor_def.partition(":")
        if name in sens:
            _LOGGER.warning("Sensor %s only allowed once", name)
            continue
        sens[name] = True

        sen = getattr(ssdefs, name, None)
        if not sen:
            log_bold(f"Unknown sensor in config: {sensor_def}")
            continue
        if not fstr:
            fstr = suggested_filter(sen)
            msg.setdefault(f"*{fstr}", []).append(name)  # type: ignore
        else:
            msg.setdefault(fstr, []).append(name)  # type: ignore

        SENSORS.append(getfilter(fstr, sensor=sen))

    for nme, val in msg.items():
        _LOGGER.info("Filter %s used for %s", nme, val)


def log_bold(msg: str) -> None:
    """Log a message."""
    _LOGGER.info("#" * 60)
    _LOGGER.info(f"{msg:^60}".rstrip())
    _LOGGER.info("#" * 60)


async def main(loop: AbstractEventLoop) -> None:  # noqa
    """Main async loop."""
    loop.set_debug(OPT.debug > 0)

    try:
        await SUNSYNK.connect(timeout=OPT.timeout)
        await SUNSYNK.read([ssdefs.serial])
    except asyncio.TimeoutError:
        log_bold(
            "No response on the Modbus interface, try checking the "
            "wiring to the Inverter, the USB-to-RS485 converter port, etc"
        )
        _LOGGER.info(
            "This Add-On will terminate in 60 seconds, "
            "use the Supervisor Watchdog to restart automatically."
        )
        asyncio.sleep(20)
        return
    log_bold(f"Inverter serial number '{ssdefs.serial.value}'")

    if OPT.sunsynk_id != ssdefs.serial.value and not OPT.sunsynk_id.startswith("_"):
        log_bold("SUNSYNK_ID should be set to the serial number of your Inverter!")
        return

    await hass_discover_sensors(str(ssdefs.serial.value))

    # Read all & publish immediately
    await asyncio.sleep(0.01)
    try:
        await SUNSYNK.read([f.sensor for f in SENSORS])
    except asyncio.TimeoutError:
        _LOGGER.error("Timeout on initial read. Sensors: %s", [f.name for f in SENSORS])
        for fil in SENSORS:
            await asyncio.sleep(0.01)
            try:
                await SUNSYNK.read([fil.sensor])
            except asyncio.TimeoutError:
                _LOGGER.error("Timeout reading single sensor: %s", fil.name)
    await publish_sensors(SENSORS, force=True)

    async def poll_sensors() -> None:
        """Poll sensors."""
        fsensors = []
        # 1. collect sensors to read
        for fil in SENSORS:
            if fil.should_update():
                fsensors.append(fil)
        if fsensors:
            # 2. read
            await SUNSYNK.read([f.sensor for f in fsensors])
            # 3. decode & publish
            await publish_sensors(fsensors)

    while True:
        polltask = asyncio.create_task(poll_sensors())
        await asyncio.sleep(1)
        try:
            await polltask
        except asyncio.TimeoutError as exc:
            _LOGGER.error("TimeOut %s", exc)
            continue
        except AttributeError:
            # The read failed. Exit and let the watchdog restart
            return
        if OPT.profiles:
            await profile_poll(SUNSYNK)


if __name__ == "__main__":
    startup()
    LOOP = asyncio.get_event_loop()
    LOOP.run_until_complete(main(LOOP))
    LOOP.close()
