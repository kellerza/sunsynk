"""Addon options."""

from __future__ import annotations

import logging
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

    mqtt_host: str = ""
    mqtt_port: int = 0
    mqtt_username: str = ""
    mqtt_password: str = ""
    number_entity_mode: str = "auto"
    prog_time_interval: int = 15
    inverters: list[InverterOptions] = []
    sensor_definitions: str = "single-phase"
    sensors: list[str] = []
    sensors_first_inverter: list[str] = []
    read_allow_gap: int = 10
    read_sensors_batch_size: int = 60
    schedules: list[Schedule] = []
    timeout: int = 10
    debug: int = 0
    driver: str = "umodbus"
    manufacturer: str = "Sunsynk"
    debug_device: str = ""


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
