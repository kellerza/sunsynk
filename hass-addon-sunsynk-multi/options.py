"""Addon options."""
from __future__ import annotations

import logging
from json import loads
from pathlib import Path

import attr
import yaml

_LOGGER = logging.getLogger(__name__)


@attr.define(slots=True)
class InverterOptions:
    """Options for an inverter."""

    # pylint: disable=too-few-public-methods
    port: str = ""
    device: str = ""
    serial_nr: str = ""
    modbus_id: int = 0
    ha_prefix: str = ""

    @classmethod
    def factory(cls, opt: dict) -> InverterOptions:
        """Create a class from the options."""
        opt2 = {k.lower(): v for k, v in opt.items()}
        return InverterOptions(**opt2)

    def get_serial(self) -> str:
        """Get the serial number."""
        return self.serial_nr.partition(":")[0]

    def get_mqttid(self) -> str:
        """Get the MQTT serial number."""
        part = self.serial_nr.partition(":")
        return part[2] if part[2] else part[0]


@attr.define(slots=True)
class Options:
    """HASS Addon Options."""

    # pylint: disable=too-few-public-methods
    mqtt_host: str = ""
    mqtt_port: int = 0
    mqtt_username: str = ""
    mqtt_password: str = ""
    number_entity_mode: str = "auto"
    inverters: list[InverterOptions] = []
    sensors: list[str] = []
    read_sensors_batch_size: int = 60
    sensor_prefix: str = ""
    timeout: int = 10
    debug: int = 1
    port: str = ""
    device: str = ""
    modbus_server_id: int = 1
    driver: str = "umodbus"
    manufacturer: str = "Sunsynk"

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
        format="%(asctime)s %(levelname)-7s %(name)s %(message)s", level=logging.DEBUG
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

    if OPT.debug < 2:
        logging.basicConfig(
            format="%(asctime)s %(levelname)-7s %(message)s",
            level=logging.INFO,
            force=True,
        )
