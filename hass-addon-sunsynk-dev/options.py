"""Addon options."""
from typing import Dict, List

import attr

from sunsynk.sensor import slug

SS_TOPIC = "SUNSYNK/status"


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
    profiles: int = 0
    sensor_prefix: str = "SS"
    timeout: int = 10
    debug: int = 1
    port_url: str = ""

    def update(self, json: Dict) -> None:
        """Update options."""
        for key, val in json.items():
            setattr(self, key.lower(), val)
        self.sunsynk_id = slug(self.sunsynk_id)


OPT = Options()
