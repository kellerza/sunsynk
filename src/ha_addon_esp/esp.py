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
from mqtt_entity import MQTTClient, MQTTDevice, MQTTSensorEntity

from ha_addon_sunsynk_multi.helpers import get_root
from sunsynk.helpers import slug

_LOGGER = logging.getLogger(__name__)

URI = "https://developer.sepush.co.za/business/2.0"
API_STATE = f"{URI}/area"
API_ALLOWANCE = f"{URI}/api_allowance"


@attrs.define(slots=True)
class ESP:
    """ESP Class."""

    api_key: str
    area_id: str
    ha_prefix: str
    client: MQTTClient
    area: str = ""

    mqtt_dev: MQTTDevice = attrs.field(
        factory=lambda: MQTTDevice(
            identifiers=[""],
            components={},
            manufacturer="EskomSePush API",
        )
    )

    state: dict[str, Any] = attrs.field(factory=dict)
    """State of the area."""
    statefile: Path = attrs.field(init=False)
    """Persistent storage for the area's state."""
    sensors: list[ESPSensor] = attrs.field(factory=list)

    def __attrs_post_init__(self) -> None:
        """Init."""
        self.statefile = get_root(True) / f"esp_{slug(self.area_id)}.json"
        if self.statefile.exists():
            _LOGGER.debug("Loading state from %s", self.statefile)
            with self.statefile.open(encoding="utf-8") as jsf:
                self.state = json.load(jsf)

        name_sensor = JMESSensor(name="Area", state_expr="info.name", attr_expr="info")
        self.sensors = [
            name_sensor,
            JMESSensor(
                name="Next", state_expr="events[0].start", attr_expr="events[0]"
            ),
            JMESSensor(name="Events", state_expr="info.name", attr_expr="events"),
            JMESSensor(name="Schedule", state_expr="info.name", attr_expr="schedule"),
            AllowanceSensor(name="Allowance"),
        ]

        # Set up the MQTT device
        self.mqtt_dev.identifiers[0] = self.id()
        self.area = search(name_sensor.state_expr, self.state) or self.area_id
        self.mqtt_dev.name = f"ESP area {self.area}"
        for sen in self.sensors:
            sen.init_entity(self.mqtt_dev, self.ha_prefix)

    def id(self) -> str:
        """Return the identifiers for the ESP."""
        return self.api_key[-8:] + slug(self.area_id)

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
        _LOGGER.debug("Saving state to %s", self.statefile)
        with self.statefile.open("w", encoding="utf-8") as jsf:
            json.dump(val, jsf, indent=2)

    async def callback(self, client: MQTTClient) -> None:
        """ESP callback - run every hour."""
        try:
            if not self.state:
                await self.init()
                return
            _LOGGER.info("Updating ESP state")
            await self.query_api()
            for sen in self.sensors:
                await sen.get_state(self)
        except Exception:  # pylint:disable=broad-except
            traceback.print_exc()
            raise

    async def init(self) -> None:
        """Initialize ESP."""
        if not self.state:
            _LOGGER.info("No state history, querying API")
            await self.query_api()
        else:
            _LOGGER.debug("Using state history: %s", self.state)

        for sen in self.sensors:
            await sen.get_state(self)


@attrs.define(slots=True)
class ESPSensor:
    """Base class for ESP sensors."""

    name: str = attrs.field()
    entity: MQTTSensorEntity = attrs.field(init=False)

    def init_entity(self, dev: MQTTDevice, ha_prefix: str) -> None:
        """Init entity."""
        nme = slug(self.name)
        unique_id = f"{dev.id}_{nme}"
        self.entity = MQTTSensorEntity(
            unique_id=unique_id,
            name=self.name,
            state_topic=f"ESP/{unique_id}/state",
            json_attributes_topic=f"ESP/{unique_id}/attributes",
            object_id=f"{ha_prefix}_{nme}",
        )
        dev.components[self.entity.object_id] = self.entity

    async def get_state(self, esp: ESP) -> Any:
        """Read the sensor value from the API."""
        raise NotImplementedError


@attrs.define(slots=True)
class JMESSensor(ESPSensor):
    """JMES Sensor."""

    state_expr: str = attrs.field()
    attr_expr: str = attrs.field()

    async def get_state(self, esp: ESP) -> Any:
        """Get state from ESP state."""
        val = search(self.state_expr, esp.state)
        await self.entity.send_state(esp.client, val, retain=True)
        atr = search(self.attr_expr, esp.state)
        _LOGGER.debug("Attributes %s = %s", self.name, json.dumps(atr))
        try:
            await self.entity.send_json_attributes(esp.client, atr)
        except TypeError as err:
            _LOGGER.error("%s", err)
        return val


@attrs.define(slots=True)
class AllowanceSensor(ESPSensor):
    """Allowance Sensor."""

    async def get_state(self, esp: ESP) -> Any:
        """Read the sensor value from the API."""
        api = await esp.query(API_ALLOWANCE, {})
        api = api.get("allowance", {})
        v_count = api.get("count", -1)
        v_limit = api.get("limit", 50)
        if api:
            await self.entity.send_state(esp.client, v_limit - v_count, retain=True)
            try:
                await self.entity.send_json_attributes(esp.client, api, retain=True)
            except TypeError as err:
                _LOGGER.error("%s", err)


AST = "areas_search"


async def search_area(name: str, api_key: str) -> None:
    """Search for an area."""
    res = {}
    sfile = get_root(True) / "esp_search.json"
    if sfile.exists():
        with sfile.open("r", encoding="utf8") as fjson:
            res = json.load(fjson)
        cname = res.get(AST)
        if cname == name:
            res["cached"] = True
        else:
            res = {}

    if not res:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{URI}/{AST}", headers={"token": api_key}, params={"text": name}
            ) as resp:
                res = await resp.json()
                res[AST] = name
                with sfile.open("w", encoding="utf8") as fjson:
                    json.dump(res, fjson)

    _LOGGER.info("Search result:\n%s", json.dumps(res, indent=2))
