#!/usr/bin/env python3
"""Run the addon."""
import asyncio
import logging
import sys
from json import loads
from pathlib import Path
from typing import Dict, List

import attr
from filter import Filter, getfilter
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
        for k, v in json.items():
            setattr(self, k.lower(), v)
        self.sunsynk_id = slug(self.sunsynk_id)


OPTIONS = Options()

SS_TOPIC = "SUNSYNK/status"


async def publish_sensors(sensors: List[Filter]):
    """Publish sensors."""
    for fsen in sensors:
        sen = fsen.sensor
        res = fsen.update(sen.value)
        if res is None:
            continue
        await MQTT.connect(OPTIONS)
        await MQTT.publish(
            topic=f"{SS_TOPIC}/{OPTIONS.sunsynk_id}/{sen.id}", payload=res
        )


async def hass_discover_sensors():
    """Discover all sensors."""
    sensors = {}
    for (sensor, _) in SENSORS:
        sensors[sensor.id] = {
            "name": sensor.name,
            "stat_t": f"{SS_TOPIC}/{OPTIONS.sunsynk_id}/{sensor.id}",
            "unit_of_meas": sensor.unit,
            "uniq_id": f"{OPTIONS.sunsynk_id}_{sensor.id}",
        }

    device = {
        "ids": [f"sunsynk_{OPTIONS.sunsynk_id}"],
        "name": "Sunsynk Inverter",
        "mdl": "Inverter",
        "mf": "Sunsynk",
    }

    await MQTT.connect(OPTIONS)
    await MQTT.discover(device_id=OPTIONS.sunsynk_id, device=device, sensors=sensors)


def startup() -> None:
    """Read the hassos configuration."""
    logging.basicConfig(level=logging.DEBUG)

    hassosf = Path("/data/options.json")
    if hassosf.exists():
        _LOGGER.info("Loading HASS OS configuration")
        OPTIONS.update(loads(hassosf.read_text()))
    else:
        _LOGGER.info(
            "Local test mode - Defaults apply. Pass MQTT host & password as arguments"
        )
        configf = Path(__file__).parent / "config.json"
        OPTIONS.update(loads(configf.read_text()).get("options", {}))
        OPTIONS.mqtt_host = sys.argv[1]
        OPTIONS.mqtt_password = sys.argv[2]
        OPTIONS.debug = 1

    SUNSYNK.port = OPTIONS.port

    if OPTIONS.debug == 0:
        logging.basicConfig(level=logging.INFO, force=True)

    sens = {}

    for sensor_def in OPTIONS.sensors:
        name, _, fstr = sensor_def.partition(":")
        if name in sens:
            _LOGGER.warning("Sensor %s only allowed once", name)
            continue
        sens[name] = True

        sen = getattr(ssdefs, name, None)
        if not sen:
            _LOGGER.error("Unknown sensor in config: %s", sensor_def)
            continue

        SENSORS.append(getfilter(fstr, sensor=sen))


async def main(loop) -> None:
    """Main async loop."""
    loop.set_debug(OPTIONS.debug > 0)
    await hass_discover_sensors()
    while True:
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

        await asyncio.sleep(1)


if __name__ == "__main__":
    startup()
    loop = SUNSYNK.connect()
    loop.run_until_complete(main(loop))
    loop.close()
