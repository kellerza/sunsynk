"""Sensors for ESP."""
from __future__ import annotations

import json
import logging
import traceback
from pathlib import Path
from typing import Any

import aiohttp
import attrs
from jmespath import search
from mqtt_entity import Device, SensorEntity  # type: ignore[import]
from mqtt_entity.helpers import Entity, MQTTClient  # type: ignore[import]

from ha_addon_sunsynk_multi.a_sensor import MQTT
from ha_addon_sunsynk_multi.helpers import get_root
from ha_addon_sunsynk_multi.timer_callback import CALLBACKS, AsyncCallback
from sunsynk.helpers import slug

_LOGGER = logging.getLogger(__name__)

API_STATE = "https://developer.sepush.co.za/business/2.0/area"
API_ALLOWANCE = "https://developer.sepush.co.za/business/2.0/api_allowance"
ESP_TOPIC = "ESP/status"


@attrs.define(slots=True)
class ESP:
    """ESP Class."""

    api_key: str = attrs.field()
    area_id: str = attrs.field()
    ha_prefix: str = attrs.field()
    state: dict[str, Any] = attrs.field(factory=dict)
    """State of the area."""
    statefile: Path = attrs.field(init=False)
    """Persistent storage for the area's state."""
    sensors: list[ESPSensor] = attrs.field(factory=list)
    allowance: AllowanceSensor = attrs.field(init=False)
    """API allowance."""

    def __attrs_post_init__(self) -> None:
        """Init."""
        self.sensors.extend(
            (
                JMESSensor(name="Next", state="events[0].start", attr="events[0]"),
                JMESSensor(name="Events", state="info.name", attr="events"),
                JMESSensor(name="Schedule", state="info.name", attr="schedule"),
                JMESSensor(name="Area", state="info.name", attr="info"),
            )
        )
        self.allowance = AllowanceSensor()
        CALLBACKS.append(
            AsyncCallback(
                name="ESP",
                callback=self.callback,
                every=60 * 60,  # run every hour
                offset=15 * 60,  # run hh:45
            ),
        )

    async def hass_discover_sensors(self) -> None:
        """Discover all sensors."""
        ids = self.api_key[-8:]
        ids += slug(self.area_id)
        dev = Device(
            identifiers=[ids],
            name="ESP integration",
            model="",
            manufacturer="",
        )
        ent = [sen.init_entity(dev, self.ha_prefix) for sen in self.sensors]
        ent.append(self.allowance.init_entity(dev, self.ha_prefix))
        await MQTT.publish_discovery_info(entities=ent)

    async def query(self, uri: str, params: dict[str, Any]) -> dict[str, Any]:
        """Query the API."""
        try:
            headers = {"token": self.api_key}
            async with aiohttp.ClientSession() as session:
                async with session.get(uri, headers=headers, params=params) as resp:
                    return await resp.json()
        except aiohttp.ClientError as err:
            _LOGGER.error("Read Error: %s: %s", type(err), err)
            return {}

    async def query_api(self) -> None:
        """Read the sensor value from the API."""
        val = await self.query(API_STATE, {"id": self.area_id})
        if not val:
            return
        self.state = val
        self.statefile.write_text(json.dumps(val, indent=2), encoding="utf-8")

    async def callback(self, _now: int) -> None:
        """Callback for ESP."""
        try:
            if not self.state:
                await self.init()
                return
            _LOGGER.info("Updating ESP state")

            await self.allowance.get_state(self)
            # await self.query_api()
            for sen in self.sensors:
                await sen.get_state(self)
        except Exception:  # pylint:disable=broad-except
            traceback.print_exc()
            raise

    async def init(self) -> None:
        """Initialize ESP."""
        self.statefile = get_root(True) / "state.json"
        if self.statefile.exists():
            txt = self.statefile.read_text(encoding="utf-8")
            self.state = json.loads(txt)
        else:
            self.state = {}

        if not self.state:
            _LOGGER.info("No state history, querying API")
            await self.query_api()
        else:
            _LOGGER.debug("Using state history: %s", self.state)

        # Start MQTT
        # MQTT.availability_topic = f"{ESP_TOPIC}/availability"
        await self.hass_discover_sensors()
        await self.allowance.get_state(self)
        for sen in self.sensors:
            await sen.get_state(self)


@attrs.define(slots=True)
class ESPSensor:
    """Base class for ESP sensors."""

    name: str = attrs.field()
    entity: SensorEntity = attrs.field(init=False)

    def init_entity(self, dev: Device, ha_prefix: str) -> SensorEntity:
        """Init entity."""
        ids = dev.identifiers[0]
        nme = slug(self.name)
        unique_id = f"{ids}_{nme}"
        self.entity = SensorEntity(
            unique_id=unique_id,
            name=self.name,
            device=dev,
            state_topic=f"{ESP_TOPIC}/{unique_id}/state",
            json_attributes_topic=f"{ESP_TOPIC}/{unique_id}/attributes",
            discovery_extra={"object_id": f"{ha_prefix}_{nme}"},
        )
        return self.entity

    async def get_state(self, esp: ESP) -> Any:
        """Read the sensor value from the API."""
        raise NotImplementedError()


@attrs.define(slots=True)
class JMESSensor(ESPSensor):
    """JMES Sensor."""

    state: str = attrs.field()
    attr: str = attrs.field()

    async def get_state(self, esp: ESP) -> Any:
        """Get state from ESP state."""
        val = search(self.state, esp.state)
        await MQTT.publish(self.entity, val, retain=True)
        atr = search(self.attr, esp.state)
        try:
            await set_attributes(atr, entity=self.entity, client=MQTT)
        except TypeError as err:
            _LOGGER.error("%s", err)
        return val


@attrs.define(slots=True)
class AllowanceSensor(ESPSensor):
    """Allowance Sensor."""

    name: str = attrs.field(default="Allowance")

    async def get_state(self, esp: ESP) -> Any:
        """Read the sensor value from the API."""
        api = await esp.query(API_ALLOWANCE, {})
        api = api.get("allowance", {})
        v_count = api.get("count", -1)
        v_limit = api.get("limit", 50)
        if api:
            await MQTT.publish(self.entity, payload=str(v_limit - v_count), retain=True)
            try:
                await set_attributes(api, entity=self.entity, client=MQTT, retain=True)
            except TypeError as err:
                _LOGGER.error("%s", err)


async def set_attributes(
    attributes: dict[str, Any],
    *,
    entity: Entity,
    client: MQTTClient,
    retain: bool = False,
) -> None:
    """Set attributes on an entity."""
    if not entity.json_attributes_topic:
        raise ValueError(f"Entity '{entity.name}' needs an json_attributes_topic.")
    if attributes is None:
        attributes = {}
    if isinstance(attributes, list):
        attributes = dict(enumerate(attributes))
    try:
        payload = json.dumps(attributes)
    except TypeError as err:
        raise TypeError(f"Invalid attributes: {attributes} (dict expected)") from err
    await client.publish(
        topic=entity.json_attributes_topic, payload=payload, retain=retain
    )
