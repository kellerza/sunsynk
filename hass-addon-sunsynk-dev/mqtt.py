"""MQTT helper."""
import asyncio
import inspect
import logging
from json import dumps
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union

import attr
from paho.mqtt.client import Client, MQTTMessage  # type: ignore

_LOGGER = logging.getLogger(__name__)

# pylint: disable=too-few-public-methods, invalid-name, too-many-instance-attributes


@attr.define
class Device:
    """A Home Assistant Device, used to group entities."""

    identifiers: List[Union[str, Tuple[str, Any]]] = attr.field()
    connections: List[str] = attr.field(factory=list)
    configuration_url: str = attr.field(default="")
    manufacturer: str = attr.field(default="")
    model: str = attr.field(default="")
    name: str = attr.field(default="")
    suggested_area: str = attr.field(default="")
    sw_version: str = attr.field(default="")
    via_device: str = attr.field(default="")

    def __attrs_post_init__(self) -> None:
        """Init the class."""
        assert self.identifiers  # Must at least have 1 identifier

    @property
    def id(self) -> str:
        """The device identifier."""
        return str(self.identifiers[0])


@attr.define
class Availability:
    """Represent Home Assistant entity availability."""

    topic: str = attr.field()
    payload_available: str = attr.field(default="online")
    payload_not_available: str = attr.field(default="offline")
    value_template: str = attr.field(default="")


@attr.define
class Entity:
    """A generic Home Assistant entity used as the base class for other entities."""

    unique_id: str = attr.field()
    device: Device = attr.field()
    state_topic: str = attr.field()
    name: str = attr.field()
    availability: List[Availability] = attr.field(factory=list)
    availability_mode: str = attr.field(default="")
    device_class: str = attr.field(default="")
    unit_of_measurement: str = attr.field(default="")
    state_class: str = attr.field(default="")
    expire_after: int = attr.field(default=0)  # unavailable if not updated
    enabled_by_default: bool = attr.field(default=True)
    entity_category: str = attr.field(default="")
    icon: str = attr.field(default="")

    _path = ""

    def __attrs_post_init__(self) -> None:
        """Init the class."""
        if not self.state_class and self.device_class == "energy":
            self.state_class = "total_increasing"

    @property
    def asdict(self) -> Dict:
        """Represent the entity as a dictionary, without empty values and defaults."""

        def _filter(atrb: Any, value: Any) -> bool:
            return (
                bool(value) and atrb.default != value and not inspect.isfunction(value)
            )

        return attr.asdict(self, filter=_filter)

    @property
    def topic(self) -> str:
        """Discovery topic."""
        uid, did = self.unique_id, self.device.id
        if uid.startswith(did):
            uid = uid[len(did) :].strip("_")
        return f"homeassistant/{self._path}/{did}/{uid}/config"


def required(_obj: Any, attr_obj: Any, val: Any) -> None:
    """A property validator, mostly used in child classes."""
    assert val is not None, f"Attribute '{attr_obj.name}' must be defined (not None)"


@attr.define
class SensorEntity(Entity):
    """A Home Assistant Sensor entity."""

    _path = "sensor"


@attr.define
class BinarySensorEntity(Entity):
    """A Home Assistant Binary Sensor entity."""

    payload_on: str = attr.field(default="ON")
    payload_off: str = attr.field(default="OFF")

    _path = "binary_sensor"


@attr.define
class SelectEntity(Entity):
    """A HomeAssistant Select entity."""

    command_topic: str = attr.field(default=None, validator=required)
    options: Sequence[str] = attr.field(default=None, validator=required)

    on_change: Callable = attr.field(default=None)

    _path = "select"


@attr.define
class NumberEntity(Entity):
    """A HomeAssistant Number entity."""

    command_topic: str = attr.field(default=None, validator=required)
    min: float = attr.field(default=0.0)
    max: float = attr.field(default=100.0)
    mode: float = attr.field(default="auto")
    step: float = attr.field(default=1.0)

    on_change: Callable = attr.field(default=None)

    _path = "number"


class MQTTClient:
    """Basic MQTT Client."""

    availability_topic: str = ""
    topic_on_change: Dict[str, Callable] = {}

    def __init__(self) -> None:
        """Init MQTT Client."""
        self._client = Client()
        self._client.on_connect = _mqtt_on_connect

    async def connect(
        self,
        options: Any = None,
        *,
        username: Optional[str] = None,
        password: Optional[str] = None,
        host: Optional[str] = None,
        port: int = 1883,
    ) -> None:
        """Connect to MQTT server specified as attributes of the options."""
        if not self._client.is_connected():
            username = getattr(options, "mqtt_username", username)
            password = getattr(options, "mqtt_password", password)
            host = getattr(options, "mqtt_host", host)
            port = getattr(options, "mqtt_port", port)
            self._client.username_pw_set(username=username, password=password)

            if self.availability_topic:
                self._client.will_set(self.availability_topic, "offline", retain=True)

            _LOGGER.info("MQTT: Connecting to %s@%s:%s", username, host, port)
            self._client.connect_async(host=host, port=port)
            self._client.loop_start()

            retry = 10
            while retry and not self._client.is_connected():
                await asyncio.sleep(0.5)
                retry -= 0
            if not retry:
                raise ConnectionError(
                    f"MQTT: Could not connect to {username}@{host}:{port}"
                )
            # publish online (Last will sets offline on disconnect)
            if self.availability_topic:
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

    async def publish_discovery_info(
        self, entities: Sequence[Entity], remove_entities: bool = True
    ) -> None:
        """Home Assistant MQTT discovery helper.

        https://www.home-assistant.io/docs/mqtt/discovery/
        Publish discovery topics on "homeassistant/(sensor|switch)/{device_id}/{sensor_id}/config"
        """
        if not self._client.is_connected():
            raise ConnectionError()

        await self.on_change_handler(entities=entities)

        task_remove = None
        if remove_entities:
            task_remove = asyncio.create_task(
                self.remove_discovery_info(
                    device_ids=list(set(e.device.id for e in entities)),
                    keep_topics=[e.topic for e in entities],
                )
            )

        for ent in entities:
            if self.availability_topic and not ent.availability:
                ent.availability = [Availability(topic=self.availability_topic)]
            _LOGGER.debug("publish %s", ent.topic)
            await self.publish(ent.topic, payload=dumps(ent.asdict), retain=True)

        await asyncio.sleep(0.01)

        if task_remove:
            await task_remove

    async def remove_discovery_info(
        self, device_ids: Sequence[str], keep_topics: Sequence[str], sleep: float = 0.5
    ) -> None:
        """Remove previously discovered entities."""

        def __on_message(client: Client, _userdata: Any, message: MQTTMessage) -> None:
            if not message.retain:
                return
            topic = str(message.topic)
            device = topic.split("/")[-3]
            _LOGGER.debug("Rx retained msg: topic=%s -- device=%s", topic, device)
            if device not in device_ids or topic in keep_topics:
                return
            _LOGGER.info("Removing HASS MQTT discovery info %s", topic)
            # Not in the event loop, execute directly
            client.publish(topic=topic, payload=None, qos=1, retain=True)

        self._client.on_message = __on_message

        subs = [f"homeassistant/+/{did}/+/config" for did in device_ids]
        for sub in subs:
            self._client.subscribe(sub)
        await asyncio.sleep(sleep)  # Wait for all retained messages to be reported
        for sub in subs:
            self._client.unsubscribe(sub)

        # re-assign the correct on_message handler
        # self._client.on_message = None
        await self.on_change_handler()

    async def on_change_handler(self, entities: Sequence[Entity] = None) -> None:
        """Assign the MQTT on_message handler for entities' on_change."""
        _loop = asyncio.get_running_loop()

        def _on_change_handler(
            _client: Client, _userdata: Any, message: MQTTMessage
        ) -> None:
            handler = self.topic_on_change.get(str(message.topic))
            if not handler:
                return
            payload = message.payload.decode("utf-8")
            if inspect.iscoroutinefunction(handler):
                coro = handler(payload)
                _loop.call_soon_threadsafe(lambda: _loop.create_task(coro))
            else:
                handler(payload)

        self._client.on_message = _on_change_handler

        if not entities:
            return

        for ent in entities:
            handler = getattr(ent, "on_change", None)
            topic = getattr(ent, "command_topic", None)
            if topic and handler:
                self.topic_on_change[topic] = handler
                self._client.subscribe(topic)


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


def hass_device_class(*, unit: str) -> str:
    """Get the HASS device_class from the unit."""
    return {
        "W": "power",
        "kW": "power",
        "kVA": "apparent_power",
        "V": "voltage",
        "kWh": "energy",
        "kVah": "",  # Not energy
        "A": "current",
        "°C": "temperature",
        "%": "battery",
    }.get(unit, "")


def hass_default_rw_icon(*, unit: str) -> str:
    """Get the HASS default icon from the unit."""
    return {
        "W": "mdi:flash",
        "V": "mdi:sine-wave",
        "A": "mdi:current-ac",
        "%": "mdi:battery-lock",
    }.get(unit, "")


MQTT = MQTTClient()
