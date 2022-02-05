"""Addon options."""
import logging
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
    sensor_prefix: str = ""
    timeout: int = 5
    debug: int = 1
    port: str = ""
    port_address: str = ""

    def update(self, json: Dict) -> None:
        """Update options."""
        logger = logging.getLogger(__name__)
        for key, val in json.items():
            setattr(self, key.lower(), val)
        self.sunsynk_id = slug(self.sunsynk_id)
        if self.port_address:
            if self.port:
                logger.warning(
                    "Your config includes PORT and PORT_ADDRESS. PORT_ADDRESS will be used"
                )
            self.port = self.port_address


OPT = Options()
