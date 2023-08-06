"""Addon options."""
# pylint: disable=too-few-public-methods
from __future__ import annotations

import logging
from json import loads
from pathlib import Path

import attrs
import yaml

_LOGGER = logging.getLogger(__name__)


@attrs.define(slots=True)
class InverterOptions:
    """Options for an inverter."""

    port: str = ""
    modbus_id: int = 0
    ha_prefix: str = ""
    serial_nr: str = ""
    dongle_serial_number: str = ""

    @classmethod
    def factory(cls, opt: dict) -> InverterOptions:
        """Create a class from the options."""
        modbus_id = int(opt.pop("MODBUS_ID"))
        iopt = InverterOptions(**{k.lower(): v for k, v in opt.items()})
        iopt.modbus_id = modbus_id

        if "_" in iopt.serial_nr:
            _LOGGER.warning(
                "The serial number contains an underscore '_' - used for testing"
            )
        return iopt


@attrs.define(slots=True)
class Options:
    """HASS Addon Options."""

    mqtt_host: str = ""
    mqtt_port: int = 0
    mqtt_username: str = ""
    mqtt_password: str = ""
    number_entity_mode: str = "auto"
    inverters: list[InverterOptions] = []
    sensor_definitions: str = "single-phase"
    sensors: list[str] = []
    sensors_first_inverter: list[str] = []
    read_sensors_batch_size: int = 60
    timeout: int = 10
    debug: int = 1
    driver: str = "umodbus"
    manufacturer: str = "Sunsynk"
    debug_device: str = ""

    def update(self, json: dict) -> None:
        """Update options."""
        for key, val in json.items():
            if key == "INVERTERS":
                self.inverters = list(map(InverterOptions.factory, val))
                continue
            setattr(self, key.lower(), val)


OPT = Options()


def init_options() -> None:
    """Initialize the options & logger."""
    logging.basicConfig(
        format="%(asctime)s %(levelname)-7s %(message)s", level=logging.INFO, force=True
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
        localf = Path(__file__).parent.parent / ".local.yaml"
        if localf.exists():
            OPT.update(yaml.safe_load(localf.read_text()))

    if OPT.debug != 0:
        logging.basicConfig(
            format="%(asctime)s %(levelname)-7s %(name)s %(message)s",
            level=logging.DEBUG,
            force=True,
        )
