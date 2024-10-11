"""Addon options."""

from __future__ import annotations

import logging
import os
from json import loads
from pathlib import Path

import attrs
import yaml

from ha_addon_sunsynk_multi.timer_schedule import Schedule

_LOGGER = logging.getLogger(__name__)


def unmarshal(target: object, json: dict) -> object:
    """Update options."""
    if not isinstance(json, dict):
        _LOGGER.error("invalid options %s", json)
    _lst = getattr(target, "_LISTS", {})
    for key, val in json.items():
        key = fixkey(key)
        if key in _lst:
            newcls = _lst[key]
            newv = [unmarshal(newcls(), item) for item in val]
            setattr(target, key, newv)
            continue
        target_old = getattr(target, key)
        setattr(target, key, val)
        for thetype in [int, str]:
            if isinstance(target_old, thetype):
                setattr(target, key, thetype(val))
                break
    return target


@attrs.define(slots=True)
class InverterOptions:
    """Options for an inverter."""

    port: str = ""
    modbus_id: int = 0
    ha_prefix: str = ""
    serial_nr: str = ""
    dongle_serial_number: str = ""


@attrs.define(slots=True)
class Options:
    """HASS Addon Options."""

    _LISTS = {"inverters": InverterOptions, "schedules": Schedule}

    mqtt_host: str = os.getenv("MQTT_HOST", "")
    mqtt_port: int = int(os.getenv("MQTT_PORT", 0))
    mqtt_username: str = os.getenv("MQTT_USERNAME", "")
    mqtt_password: str = os.getenv("MQTT_PASSWORD", "")
    number_entity_mode: str = os.getenv("NUMBER_ENTITY_MODE", "auto")
    prog_time_interval: int = int(os.getenv("PROG_TIME_INTERVAL", "15"))
    inverters: list[InverterOptions] = []
    sensor_definitions: str = os.getenv("SENSOR_DEFINITIONS", "single-phase")
    sensors: list[str] = []
    sensors_first_inverter: list[str] = []
    read_allow_gap: int = int(os.getenv("READ_ALLOW_GAP", 10))
    read_sensors_batch_size: int = int(os.getenv("READ_SENSORS_BATCH_SIZE", 60))
    schedules: list[Schedule] = []
    timeout: int = int(os.getenv("TIMEOUT", 10))
    debug: int = int(os.getenv("DEBUG", 0))
    driver: str = os.getenv("DRIVER", "umodbus")
    manufacturer: str = os.getenv("MANUFACTURER", "Sunsynk")
    debug_device: str = os.getenv("DEBUG_DEVICE", "")


OPT = Options()


def init_options() -> None:
    """Load the options & setup the logger."""
    logging.basicConfig(
        format="%(asctime)s %(levelname)-7s %(message)s",
        level=logging.INFO,
        force=True,
        datefmt="%H:%M:%S",
    )

    opt = None

    config_files = ("/data/options.json", "/data/options.yaml", ".data/options.yaml")
    for fname in config_files:
        fpath = Path(fname)
        if fpath.exists():
            _LOGGER.info("Loading configuration: %s", fpath)
            txt = fpath.read_text(encoding="utf-8")
            opt = loads(txt) if fname.endswith(".json") else yaml.safe_load(txt)
            break

    if opt is None:
        _LOGGER.error("No configuration file found")
        return

    unmarshal(OPT, opt)

    if OPT.debug != 0:
        logging.basicConfig(
            format="%(asctime)s %(levelname)-7s %(name)s %(message)s",
            level=logging.DEBUG,
            force=True,
        )


#     for handler in logging.getLogger().handlers:
#         handler.addFilter(Whitelist('foo', 'bar'))


# class Whitelist(logging.Filter):
#     def __init__(self, *whitelist):
#         self.whitelist = [logging.Filter(name) for name in whitelist]

#     def filter(self, record):
#         return any(f.filter(record) for f in self.whitelist)


def fixkey(key: str) -> str:
    """Return the correct lowercase key.

    Replacements for old keys.
    """
    replace = {
        "change_significant": "change_by",
        "change_significant_percent": "change_percent",
    }
    key = key.lower()
    return replace.get(key.lower(), key)
