"""MQTT helper."""
import asyncio
import logging
from json import dumps
from typing import Any, Callable, Dict, Optional, Sequence

from paho.mqtt.client import Client, MQTTMessage  # type: ignore

_LOGGER = logging.getLogger(__name__)


class MQTTClient:
    """Basic MQTT Client."""

    availability_topic: str = ""

    def __init__(self) -> None:
        """Init MQTT Client."""
        self._client = Client()
        self._client.on_connect = _mqtt_on_connect

    async def connect(self, options: Any) -> None:
        """Connect to MQTT server specified as attributes of the options."""
        if not self._client.is_connected():
            username = getattr(options, "mqtt_username")
            password = getattr(options, "mqtt_password")
            host = getattr(options, "mqtt_host")
            port = getattr(options, "mqtt_port")
            self._client.username_pw_set(username=username, password=password)

            if self.availability_topic:
                self._client.will_set(self.availability_topic, "offline", retain=True)

            self._client.connect_async(host=host, port=port)
            self._client.loop_start()

            retry = 10
            while retry and not self._client.is_connected():
                await asyncio.sleep(0.5)
                retry -= 0
            if not retry:
                raise ConnectionError(
                    f"Could not connect to MQTT server {username}@{host}:{port}"
                )
            # publish online (Last will sets offline on disconnect)
            await self.publish(self.availability_topic, "online", retain=True)

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

        self._client.on_message = _mqtt_on_message(
            self=self, loop=asyncio.get_running_loop(), sensors=list(sensors.keys())
        )
        self._client.subscribe(f"homeassistant/sensor/{device_id}/#")

        for s_id, sen in sensors.items():
            topic = f"homeassistant/sensor/{device_id}/{s_id}/config"
            sen["dev"] = device  # Sensors will be grouped under this device
            sen["exp_aft"] = sen.get("exp_aft", 301)  # unavailable if not updated
            dev_cla = sen.get("dev_cla") or hass_device_class(unit=sen["unit_of_meas"])
            if dev_cla:
                sen["dev_cla"] = dev_cla
            else:
                sen.pop("dev_cla", None)
            if dev_cla == "energy":
                sen["stat_cla"] = "total_increasing"
            await self.publish(topic, payload=dumps(sen), retain=True)

        await asyncio.sleep(1)  # Wait for all retained messages

        self._client.unsubscribe(f"homeassistant/sensor/{device_id}/#")
        self._client.on_message = None


def _mqtt_on_connect(
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


def _mqtt_on_message(
    *, self: MQTTClient, loop: asyncio.AbstractEventLoop, sensors: Sequence[str]
) -> Callable[[Client, Any, MQTTMessage], None]:
    """Receive retained messages & remove if not in sensors."""

    def __on_message(_client: Client, _userdata: Any, message: MQTTMessage) -> None:
        if not message.retain:
            return
        topic = str(message.topic)
        top = topic.split("/")
        if top[-1] != "config" or top[-2] in sensors:
            return
        _LOGGER.info("Removing HASS MQTT discovery info %s", topic)
        asyncio.ensure_future(self.publish(topic, None, retain=True), loop=loop)

    return __on_message


def hass_device_class(*, unit: str) -> Optional[str]:
    """Get the HASS device_class from the unit."""
    return {
        "W": "power",
        "kW": "power",
        "kVA": "power",
        "V": "voltage",
        "kWh": "energy",
        "kVa": "energy",
        "A": "current",
        "°C": "temperature",
        "%": "battery",
    }.get(unit, "")
