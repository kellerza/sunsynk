"""Addon options."""
from typing import Dict, List

import attr

from sunsynk.rwsensors import slug

SS_TOPIC = "SUNSYNK/status"


@attr.define(slots=True)
class Options:
    """HASS Addon Options."""

    # pylint: disable=too-few-public-methods
    mqtt_host: str = ""
    mqtt_port: int = 0
    mqtt_username: str = ""
    mqtt_password: str = ""
    number_entity_mode: str = "auto"
    sunsynk_id: str = ""
    sensors: List[str] = []
    read_sensors_batch_size: int = 60
    profiles: List[str] = []
    sensor_prefix: str = "SS"
    timeout: int = 10
    debug: int = 1
    port: str = ""
    device: str = ""
    modbus_server_id: int = 1
    driver: str = "umodbus"

    def update(self, json: Dict) -> None:
        """Update options."""
        for key, val in json.items():
            setattr(self, key.lower(), val)
        self.sunsynk_id = slug(self.sunsynk_id)


OPT = Options()
