"""Run the energy meter."""
import logging
import sys
from json import dumps, loads
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import attr
from icecream import ic
from mqtt import MQTTClient

import sunsynk.definitions as ssdefs
from sunsynk.sensor import Sensor

_LOGGER = logging.getLogger(__name__)
_MQTT = MQTTClient()

SENSORS: Dict[str, Sequence[Sensor]] = {}


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
    poll_interval: int = 60
    port: str = ""


OPTIONS = Options()

SS_TOPIC = "SUNSYNK/status"


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


async def hass_discover_sensor(*, ss_id: str, sensor_id: str, sensor: Sensor) -> None:
    """Send a retained message for this sensor."""
    topic = f"homeassistant/sensor/{ss_id}/{sensor_id}/config"
    dev_class = hass_device_class(unit=sensor.unit)
    payload = {
        "name": sensor_id,
        "dev_cla": dev_class,
        "stat_t": f"{SS_TOPIC}/{ss_id}/{sensor_id}",
        "unit_of_meas": sensor.unit,
        "uniq_id": f"{ss_id}_{sensor_id}",
        "dev": {
            "ids": [f"sunsynk_{ss_id}"],
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


async def startup():
    """Read the hassos configuration."""
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

    if OPTIONS.debug == 0:

        def blank(*args) -> None:
            pass

        ic = blank

    res = []
    for sensor_def in OPTIONS.sensors:
        name, _, _mod = sensor_def.partition(":")

        sen = getattr(ssdefs, name, None)
        if not sen:
            _LOGGER.error("Unknown sensor in config: %s", sensor_def)
            continue
        await hass_discover_sensor(
            ss_id=OPTIONS.sunsynk_id, sensor_id=sensor_def, sensor=sen
        )
        SENSORS[sensor_def] = sen
        res.append(sen)

    ic(res)

    return res
