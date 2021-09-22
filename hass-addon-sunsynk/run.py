#!/usr/bin/env python3
"""Run the addon."""
import asyncio
import logging
import sys
from asyncio.events import AbstractEventLoop
from json import loads
from pathlib import Path
from typing import Dict, List

import attr
from filter import Filter, getfilter, suggested_filter
from mqtt import MQTTClient

import sunsynk.definitions as ssdefs
from sunsynk import Sunsynk
from sunsynk.sensor import slug

_LOGGER = logging.getLogger(__name__)
MQTT = MQTTClient()


SENSORS: List[Filter] = []


SUNSYNK = Sunsynk()


@attr.define(slots=True)
class Options:
    """HASS Addon Options."""

    # pylint: disable=too-few-public-methods
    mqtt_host: str = ""
    mqtt_port: int = 0
    mqtt_username: str = ""
    mqtt_password: str = ""
    sunsynk_id: str = ""
    sensors: List[str] = []
    debug: int = 1
    port: str = ""

    def update(self, json: Dict) -> None:
        """Update options."""
        for key, val in json.items():
            setattr(self, key.lower(), val)
        self.sunsynk_id = slug(self.sunsynk_id)


OPT = Options()

SS_TOPIC = "SUNSYNK/status"


async def publish_sensors(sensors: List[Filter]) -> None:
    """Publish sensors."""
    for fsen in sensors:
        sen = fsen.sensor
        res = fsen.update(sen.value)
        if res is None:
            continue
        await MQTT.connect(OPT)
        await MQTT.publish(
            topic=f"{SS_TOPIC}/{OPT.sunsynk_id}/{sen.id}", payload=str(res)
        )


async def hass_discover_sensors(serial: str) -> None:
    """Discover all sensors."""
    sensors = {}
    for filt in SENSORS:
        sensor = filt.sensor
        sensors[sensor.id] = {
            "name": sensor.name,
            "stat_t": f"{SS_TOPIC}/{OPT.sunsynk_id}/{sensor.id}",
            "unit_of_meas": sensor.unit,
            "uniq_id": f"{OPT.sunsynk_id}_{sensor.id}",
        }

    device = {
        "ids": [f"sunsynk_{OPT.sunsynk_id}"],
        "name": "Sunsynk Inverter",
        "mdl": f"Inverter - {serial}",
        "mf": "Sunsynk",
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

    SUNSYNK.port = OPT.port

    if OPT.debug == 0:
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
            _LOGGER.error("Unknown sensor in config: %s", sensor_def)
            continue
        if not fstr:
            fstr = suggested_filter(name)
            msg.setdefault(f"*{fstr}", []).append(name)  # type: ignore
        else:
            msg.setdefault(fstr, []).append(name)  # type: ignore

        SENSORS.append(getfilter(fstr, sensor=sen))

    for nme, val in msg.items():
        _LOGGER.info("Filter %s used for %s", nme, val)


async def main(loop: AbstractEventLoop) -> None:
    """Main async loop."""
    loop.set_debug(OPT.debug > 0)

    _LOGGER.info("#" * 50)
    await SUNSYNK.read([ssdefs.serial])
    _LOGGER.info("  SMA serial number %s", ssdefs.serial.value)
    _LOGGER.info("#" * 50)

    if OPT.sunsynk_id != ssdefs.serial.value and not OPT.sunsynk_id.startswith("_"):
        _LOGGER.error(
            "SUNSYNK_ID should be set to the serial number of your Sunsynk inverter!"
        )
        _LOGGER.info("#" * 50)
        return

    await hass_discover_sensors(str(ssdefs.serial.value))

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
        asyncio.ensure_future(poll_sensors())
        await asyncio.sleep(1)


if __name__ == "__main__":
    startup()
    LOOP = SUNSYNK.connect()
    LOOP.run_until_complete(main(LOOP))
    LOOP.close()
