"""State of a sensor & entity."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, NotRequired, TypedDict

import attrs
from mqtt_entity import (  # type: ignore[import]
    BinarySensorEntity,
    Device,
    Entity,
    MQTTClient,
    NumberEntity,
    RWEntity,
    SelectEntity,
    SensorEntity,
    SwitchEntity,
)
from mqtt_entity.helpers import (  # type: ignore[import]
    hass_default_rw_icon,
    hass_device_class,
)
from mqtt_entity.utils import tostr  # type: ignore[import]

from ha_addon_sunsynk_multi.options import OPT
from ha_addon_sunsynk_multi.sensor_options import SensorOption
from sunsynk.helpers import ValType, slug
from sunsynk.rwsensors import (
    NumberRWSensor,
    RWSensor,
    SelectRWSensor,
    SwitchRWSensor,
    SwitchRWSensor0,
    TimeRWSensor,
    resolve_num,
)
from sunsynk.sensors import BinarySensor, EnumSensor, TextSensor

if TYPE_CHECKING:
    from ha_addon_sunsynk_multi.a_inverter import AInverter


SS_TOPIC = "SUNSYNK/status"
_LOGGER = logging.getLogger(__name__)
"""An array of the Sunsynk driver instances."""
MQTT = MQTTClient()
"""The MQTTClient instance."""


# NotRequired need Python 3.11 - Already standard in HASS
class MqttEntityOptions(TypedDict):
    """Shared MQTTEntity options."""

    name: str
    state_topic: str
    unique_id: str
    device_class: NotRequired[str]
    state_class: NotRequired[str]
    icon: NotRequired[str]
    entity_category: NotRequired[str]
    unit_of_measurement: str
    # command_topic: str
    discovery_extra: dict[str, Any]


@attrs.define(slots=True)
class ASensor:
    """Addon Sensor state & entity."""

    opt: SensorOption
    # istate: int = attrs.field()
    entity: Entity | None = None
    "The entity will be None if hidden."

    def __hash__(self) -> int:
        """Hasable."""
        return self.opt.sensor.__hash__()

    # @property
    # def hidden(self) -> bool:
    #     """Hide state from HA."""
    #     return not self.opt.visible

    _last: ValType = None
    retain: bool = False

    @property
    def value(self) -> ValType:
        """Return the last value."""
        return self._last

    async def publish(self, val: ValType) -> None:
        """Set the value through MQTT."""
        if self.entity is None:
            _LOGGER.error("no entity %s", self.name)
            return
        if val is None:
            _LOGGER.debug("Cannot publish %s: value is None", self.name)
            return
        if self._last == val and self.retain:
            return
        await MQTT.connect(OPT)
        await MQTT.publish(
            topic=self.entity.state_topic,
            payload=tostr(val),
            retain=self.retain,
        )
        self._last = val

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self.opt.sensor.name

    def is_measurement(self, units: str) -> bool:
        """Return True if the units are a measurement."""
        return units in {"W", "V", "A", "Hz", "°C", "°F", "%", "Ah", "VA"}

    def visible_on(self, ist: AInverter) -> bool:
        """Should entity be visible on this inverter."""
        if not self.opt.visible:
            return False
        if self.opt.first and ist.index > 0:
            return False
        if self.opt.sensor is None:
            return False
        return True

    def create_entity(self, dev: Device | Entity | None, *, ist: AInverter) -> Entity:
        """Create HASS entity."""
        # pylint: disable=too-many-branches,too-many-return-statements
        if not self.visible_on(ist):
            raise ValueError("Entity not visible")
        if self.opt.sensor is None:
            raise ValueError(f"Cannot create entity if no sensor specified: {self}")
        if dev is None:
            raise ValueError(f"No device specified for create_entity: {self}")
        if isinstance(dev, Entity):
            dev = dev.device

        sensor = self.opt.sensor

        state_topic = f"{SS_TOPIC}/{dev.id}/{sensor.id}"
        command_topic = f"{state_topic}_set"

        discovery_extra: dict[str, str | int] = {
            "object_id": slug(f"{ist.opt.ha_prefix} {sensor.name}".strip()),
            "suggested_display_precision": 1,
        }

        ent: MqttEntityOptions = {
            "name": sensor.name,
            "state_topic": state_topic,
            "unique_id": f"{dev.id}_{sensor.id}",
            "unit_of_measurement": sensor.unit,
            # https://github.com/kellerza/sunsynk/issues/165
            "discovery_extra": discovery_extra,
        }

        if isinstance(sensor, TextSensor):
            discovery_extra.pop("suggested_display_precision")

        if isinstance(sensor, EnumSensor):
            self.entity = SensorEntity(
                device=dev,
                **ent,
                # options=sensor.available_values(),
            )
            return self.entity

        if not isinstance(sensor, RWSensor):
            ent["device_class"] = hass_device_class(unit=sensor.unit)
            if isinstance(sensor, BinarySensor):
                self.entity = BinarySensorEntity(device=dev, **ent)
            else:
                if self.is_measurement(sensor.unit):
                    ent["state_class"] = "measurement"
                self.entity = SensorEntity(device=dev, **ent)
            return self.entity

        async def on_change(val: float | int | str | bool) -> None:
            """On change callback."""
            _LOGGER.info("Queue update %s=%s", sensor.id, val)
            ist.write_queue.update({sensor: val})
            await self.publish(val)

        ent["entity_category"] = "config"
        ent["icon"] = hass_default_rw_icon(unit=sensor.unit)

        if isinstance(sensor, NumberRWSensor):
            self.entity = NumberEntity(
                device=dev,
                **ent,
                command_topic=command_topic,
                min=resolve_num(ist.get_state, sensor.min, 0),
                max=resolve_num(ist.get_state, sensor.max, 100),
                mode=OPT.number_entity_mode,
                step=0.1 if sensor.factor < 1 else 1,
                on_change=on_change,
            )
            return self.entity

        if isinstance(sensor, (SwitchRWSensor, SwitchRWSensor0)):
            self.entity = SwitchEntity(
                device=dev,
                **ent,
                command_topic=command_topic,
                on_change=on_change,
            )
            return self.entity

        if isinstance(sensor, SelectRWSensor):
            self.entity = SelectEntity(
                device=dev,
                **ent,
                command_topic=command_topic,
                options=sensor.available_values(),
                on_change=on_change,
            )
            return self.entity

        if isinstance(sensor, TimeRWSensor):
            ent["icon"] = "mdi:clock"
            self.entity = SelectEntity(
                device=dev,
                **ent,
                command_topic=command_topic,
                options=sensor.available_values(OPT.prog_time_interval, ist.get_state),
                on_change=on_change,
            )
            return self.entity

        RWEntity._path = "text"  # pylint: disable=protected-access

        ent["entity_category"] = "diagnostic"

        self.entity = RWEntity(
            device=dev,
            **ent,
            command_topic=command_topic,
            on_change=on_change,
        )
        return self.entity


@attrs.define(slots=True)
class TimeoutState(ASensor):
    """Entity definition for the timeout sensor."""

    retain = True

    def create_entity(self, dev: Device | Entity | None, *, ist: AInverter) -> Entity:
        """MQTT entities for stats."""
        if dev is None:
            raise ValueError(f"No device specified for create_entity! {self}")
        if isinstance(dev, Entity):
            dev = dev.device

        self.entity = SensorEntity(
            name="RS485 timeouts",
            unique_id=f"{dev.id}_timeouts",
            state_topic=f"{SS_TOPIC}/{dev.id}/timeouts",
            entity_category="config",
            device=dev,
        )
        return self.entity
