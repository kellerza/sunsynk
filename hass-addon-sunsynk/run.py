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

from filter import Filter, getfilter, suggested_filter
from mqtt import MQTTClient
from options import OPT

import sunsynk.definitions as ssdefs
from sunsynk import Sunsynk

_LOGGER = logging.getLogger(__name__)
MQTT = MQTTClient()


SENSORS: List[Filter] = []


SUNSYNK = Sunsynk()


SS_TOPIC = "SUNSYNK/status"


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
    sensors = {}
    for filt in SENSORS:
        sensor = filt.sensor
        sensors[sensor.id] = {
            "name": f"{OPT.sensor_prefix} {sensor.name}".strip(),
            "state_topic": f"{SS_TOPIC}/{OPT.sunsynk_id}/{sensor.id}",
            "unit_of_measurement": sensor.unit,
            "unique_id": f"{OPT.sunsynk_id}_{sensor.id}",
            "availability": [{"topic": MQTT.availability_topic}],
        }

    device = {
        "identifiers": [f"sunsynk_{OPT.sunsynk_id}"],
        "name": f"Sunsynk Inverter {serial}",
        "model": f"Inverter {serial}",
        "manufacturer": "Sunsynk",
    }

    await MQTT.connect(OPT)
    await MQTT.discover(device_id=OPT.sunsynk_id, device=device, sensors=sensors)


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
        configf = Path(__file__).parent / "config.json"
        OPT.update(loads(configf.read_text()).get("options", {}))
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
            fstr = suggested_filter(name)
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


async def main(loop: AbstractEventLoop) -> None:
    """Main async loop."""
    loop.set_debug(OPT.debug > 0)
    await SUNSYNK.connect(timeout=OPT.timeout)

    await SUNSYNK.read([ssdefs.serial])
    log_bold(f"SMA serial number '{ssdefs.serial.value}'")

    if OPT.sunsynk_id != ssdefs.serial.value and not OPT.sunsynk_id.startswith("_"):
        log_bold("SUNSYNK_ID should be set to the serial number of your Inverter!")
        return

    await hass_discover_sensors(str(ssdefs.serial.value))

    # Read all & publish immediately
    await SUNSYNK.read([f.sensor for f in SENSORS])
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
        polltask = asyncio.ensure_future(poll_sensors())
        await asyncio.sleep(1)
        try:
            await polltask
        except AttributeError:
            # The read failed. Exit and let the watchdog restart
            return


if __name__ == "__main__":
    startup()
    LOOP = asyncio.get_event_loop()
    LOOP.run_until_complete(main(LOOP))
    LOOP.close()
