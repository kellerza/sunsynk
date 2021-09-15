#!/usr/bin/env python3
"""Run the addon."""
import asyncio
import logging
import sys
from json import dumps, loads
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import attr
from icecream import ic
from mqtt import MQTTClient

import sunsynk.definitions as ssdefs
from sunsynk import Sensor, Sunsynk

_LOGGER = logging.getLogger(__name__)
_MQTT = MQTTClient()

SENSORS: List[Sensor] = []

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
    interval: int = 60
    port: str = ""


OPTIONS = Options()

SS_TOPIC = "SUNSYNK/status"


async def publish_sensors(sensors: Sequence[Sensor]):
    """Publish sensors."""
    ss_id = OPTIONS.sunsynk_id
    for sen in sensors:
        await mqtt_publish(topic=f"{SS_TOPIC}/{ss_id}/{sen.id}", payload=sen.value)


async def mqtt_publish(topic: str, payload: Any, retain: bool = False) -> None:
    """Publish to MQTT."""
    await _MQTT.connect(
        username=OPTIONS.mqtt_username,
        password=OPTIONS.mqtt_password,
        host=OPTIONS.mqtt_host,
        port=OPTIONS.mqtt_port,
    )
    if not topic:
        return
    ic(topic, payload)
    await _MQTT.publish(topic=topic, payload=payload, retain=retain)


def hass_device_class(*, unit: str) -> Optional[str]:
    """Get the HASS device_class from the unit."""
    return {
        "W": "power",
        "kW": "power",
        "kVA": "power",
        "V": "voltage",
        "Hz": None,
    }.get(
        unit, "energy"
    )  # kwh, kVa,


async def hass_discover_sensor(*, ss_id: str, sensor: Sensor) -> None:
    """Send a retained message for this sensor."""


async def hass_discover_sensors():
    """Discover all sensors."""
    for sensor in SENSORS:
        topic = f"homeassistant/sensor/{OPTIONS.sunsynk_id}/{sensor.id}/config"
        dev_class = hass_device_class(unit=sensor.unit)
        payload = {
            "name": sensor.name,
            "dev_cla": dev_class,
            "stat_t": f"{SS_TOPIC}/{OPTIONS.sunsynk_id}/{sensor.id}",
            "unit_of_meas": sensor.unit,
            "uniq_id": f"{OPTIONS.sunsynk_id}_{sensor.id}",
            "dev": {
                "ids": [f"sunsynk_{OPTIONS.sunsynk_id}"],
                "name": "Sunsynk Inverter",
                "mdl": "Inverter",
                "mf": "Sunsynk",
            },
        }
        if dev_class == "energy":
            payload["state_class"] = "total_increasing"

        await mqtt_publish(topic, dumps(payload), retain=True)


def update_options(json: Dict) -> None:
    """Update global options."""
    for k, v in json.items():
        setattr(OPTIONS, k.lower(), v)


def startup():
    """Read the hassos configuration."""
    logging.basicConfig(level=logging.DEBUG)

    hassosf = Path("/data/options.json")
    if hassosf.exists():
        _LOGGER.info("Loading HASS OS configuration")
        update_options(loads(hassosf.read_text()))
    else:
        _LOGGER.info(
            "Local test mode - defaults apply. MQTT_PASSWORD taken from 1st argument"
        )
        configf = Path("./config.json")
        update_options(loads(configf.read_text()).get("options", {}))
        OPTIONS.mqtt_host = "192.168.88.128"
        OPTIONS.mqtt_password = sys.argv[1]
        OPTIONS.debug = 1

    global ic
    ic(OPTIONS)

    SUNSYNK.port = OPTIONS.port

    if OPTIONS.debug == 0:

        def blank(*args) -> None:
            pass

        ic = blank
        logging.basicConfig(level=logging.INFO, force=True)

    for sensor_def in OPTIONS.sensors:
        name, _, _mod = sensor_def.partition(":")

        sen = getattr(ssdefs, name, None)
        if not sen:
            _LOGGER.error("Unknown sensor in config: %s", sensor_def)
            continue
        SENSORS.append(sen)


async def main(loop) -> None:
    """Main async loop."""
    loop.set_debug(OPTIONS.debug > 0)
    await hass_discover_sensors()
    ic(SENSORS)
    while True:
        await SUNSYNK.read(SENSORS)
        await publish_sensors(SENSORS)
        await asyncio.sleep(OPTIONS.interval)


if __name__ == "__main__":
    startup()
    loop = SUNSYNK.connect()
    loop.run_until_complete(main(loop))
    loop.close()
