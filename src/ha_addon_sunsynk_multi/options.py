"""Addon options."""

from __future__ import annotations

import logging
import os
import typing as t
from json import load, loads
from pathlib import Path

import attrs
from cattrs import Converter, transform_error
from cattrs.gen import make_dict_structure_fn
from yaml import safe_load

from ha_addon_sunsynk_multi.timer_schedule import Schedule

_LOGGER = logging.getLogger(__name__)


T = t.TypeVar("T", str, int, list)


@attrs.define(slots=True)
class InverterOptions:
    """Options for an inverter."""

    port: str = ""
    modbus_id: int = 0
    ha_prefix: str = ""
    serial_nr: str = ""
    dongle_serial_number: int = 0


@attrs.define(slots=True)
class Options:
    """HASS Addon Options."""

    mqtt_host: str = ""
    mqtt_port: int = 1883
    mqtt_username: str = ""
    mqtt_password: str = ""
    number_entity_mode: str = "auto"
    prog_time_interval: int = 15
    inverters: list[InverterOptions] = attrs.field(factory=list)
    sensor_definitions: str = "single-phase"
    sensors: list[str] = attrs.field(factory=list)
    sensors_first_inverter: list[str] = attrs.field(factory=list)
    read_allow_gap: int = 2
    read_sensors_batch_size: int = 20
    schedules: list[Schedule] = attrs.field(factory=list)
    timeout: int = 10
    debug: int = 0
    driver: str = "pymodbus"
    manufacturer: str = "Sunsynk"
    debug_device: str = ""

    def load(self, value: dict) -> None:
        """Structure and copy result to self."""
        try:
            _LOGGER.debug("Loading config: %s", value)
            val = CONVERTER.structure(value, Options)
        except Exception as exc:
            msg = "Error loading config: " + "\n".join(transform_error(exc))
            _LOGGER.error(msg)
            raise ValueError(msg)  # pylint:disable=raise-missing-from
        for key in value:
            setattr(self, key.lower(), getattr(val, key.lower()))

    def load_env(self) -> bool:
        """Get attrs fields from the environment."""
        res = {}
        atts: tuple[attrs.Attribute, ...] = attrs.fields(attrs.resolve_types(Options))
        for att in atts:
            val = os.getenv(att.name.upper())
            if not val:
                continue
            if t.get_origin(att.type) is list:
                res[att.name.upper()] = loads(val) if "[" in val else val.split(",")
                continue
            res[att.name.upper()] = val
        if res:
            _LOGGER.info("Loading config from environment variables: %s", res)
            self.load(res)
        return bool(res)


OPT = Options()


def init_options() -> None:
    """Load the options & setup the logger."""
    logging.basicConfig(
        format="%(asctime)s %(levelname)-7s %(message)s",
        level=logging.INFO,
        force=True,
        datefmt="%H:%M:%S",
    )

    env_ok = OPT.load_env()

    cfg_names = (
        "/data/options.json",  # HA OS config location
        "/data/options.yaml",  # Recommended for standalone deployment
        ".data/options.yaml",  # Pytest
    )
    cfg_files = [f for f in (Path(s) for s in cfg_names) if f.exists()]
    if not cfg_files and not env_ok:
        _LOGGER.error("No config file or environment variables found.")
        os._exit(1)

    for fpath in cfg_files:
        _LOGGER.info("Loading config: %s", fpath)
        with fpath.open("r", encoding="utf-8") as fptr:
            opt = load(fptr) if fpath.suffix == ".json" else safe_load(fptr)
            OPT.load(opt)

    if OPT.debug != 0:
        logging.basicConfig(
            format="%(asctime)s %(levelname)-7s %(name)s %(message)s",
            level=logging.DEBUG,
            force=True,
        )


CONVERTER = Converter(forbid_extra_keys=True)


def structure_ensure_lowercase_keys(cls: t.Type) -> t.Callable[[t.Any, t.Any], t.Any]:
    """Convert any uppercase keys to lowercase."""
    struct = make_dict_structure_fn(cls, CONVERTER)  # type: ignore

    def structure(d: dict[str, t.Any], cl: t.Any) -> t.Any:
        lower = [k for k in d if k.lower() != k]
        for k in lower:
            if k.lower() in d:
                _LOGGER.warning("Key %s already exists in lowercase", k.lower())
            d[k.lower()] = d.pop(k)
        return struct(d, cl)

    return structure


CONVERTER.register_structure_hook_factory(attrs.has, structure_ensure_lowercase_keys)
