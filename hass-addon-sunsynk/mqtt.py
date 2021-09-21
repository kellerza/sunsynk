"""MQTT helper."""
import asyncio
import logging
from json import dumps
from typing import Any, Dict, Optional

from paho.mqtt.client import Client, MQTTMessage  # type: ignore

_LOGGER = logging.getLogger(__name__)


class MQTTClient:
    """Basic MQTT Client."""

    def __init__(self) -> None:
        """Init MQTT Client."""
        self._client = Client()

        def on_connect(
            _client: Client, _userdata: Any, _flags: Any, _rc: int, _prop: Any = None
        ) -> None:
            msg = {
                0: "successful",
                1: "refused - incorrect protocol version",
                2: "refused - invalid client identifier",
                3: "refused - server unavailable",
                4: "refused - bad username or password",
                5: "refused - not authorised",
            }.get(_rc, f"refused - {_rc}")
            _LOGGER.info("MQTT: Connection %s", msg)

        self._client.on_connect = on_connect

    async def connect(self, options: Any) -> None:
        """Connect to MQTT server specified as attributes of the options."""
        if not self._client.is_connected():
            _LOGGER.info("Connecting")
            username = getattr(options, "mqtt_username")
            password = getattr(options, "mqtt_password")
            host = getattr(options, "mqtt_host")
            port = getattr(options, "mqtt_port")
            self._client.username_pw_set(username=username, password=password)
            self._client.connect_async(host=host, port=port)
            self._client.loop_start()

        while not self._client.is_connected():
            await asyncio.sleep(1)

    async def disconnect(self) -> None:
        """Stop the MQTT client."""

        def _stop() -> None:
            # Do not disconnect, we want the broker to always publish will
            self._client.loop_stop()

        await asyncio.get_running_loop().run_in_executor(None, _stop)

    async def publish(
        self, topic: str, payload: Optional[str], qos: int = 0, retain: bool = False
    ) -> None:
        """Publish a MQTT message."""
        # async with self._paho_lock:
        if not isinstance(qos, int):
            qos = 0
        if retain:
            qos = 1
        _LOGGER.debug("PUBLISH %s%s %s, %s", qos, "R" if retain else "", topic, payload)
        await asyncio.get_running_loop().run_in_executor(
            None, self._client.publish, topic, payload, qos, retain is True
        )

    async def discover(
        self, *, device_id: str, device: Dict[str, Any], sensors: Dict[str, Dict]
    ) -> None:
        """Home Assistant MQTT discovery helper.

        https://www.home-assistant.io/docs/mqtt/discovery/
        Publish discovery topics on "homeassistant/sensor/{device_id}/{sensor_id}/config"

        device: Information about the device these sensors are part of to tie it into
                the device registry. Each sensor requires a unique_id
        """
        if not self._client.is_connected():
            raise ConnectionError()

        # Read all current retained messages
        extras = []

        def on_message(_client: Client, _userdata: Any, message: MQTTMessage) -> None:
            """Receive messages & detect extras."""
            if message.retain:
                top = str(message.topic).split("/")
                if len(top) == 5 and top[4] == "config":
                    if top[3] not in sensors:
                        extras.append(top[3])

        self._client.on_message = on_message
        self._client.subscribe(f"homeassistant/sensor/{device_id}/#")

        for s_id, sen in sensors.items():
            topic = f"homeassistant/sensor/{device_id}/{s_id}/config"
            sen["dev"] = device  # Sensors will be grouped under this device
            sen["exp_aft"] = sen.get("exp_aft", 301)  # unavailable if not updated
            sen["dev_cla"] = sen.get(
                "dev_cla", hass_device_class(unit=sen["unit_of_meas"])
            )
            if sen["dev_cla"] == "energy":
                sen["stat_cla"] = "total_increasing"
            await self.publish(topic, payload=dumps(sen), retain=True)

        # Remove all the extra retained topics
        for s_id in extras:
            topic = f"homeassistant/sensor/{device_id}/{s_id}/config"
            await self.publish(topic, None, qos=1, retain=True)


def hass_device_class(*, unit: str) -> Optional[str]:
    """Get the HASS device_class from the unit."""
    return {
        "W": "power",
        "kW": "power",
        "kVA": "power",
        "V": "voltage",
        "Hz": None,
        "%": None,
    }.get(
        unit, "energy"
    )  # kwh, kVa and others
