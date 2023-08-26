"""State of a sensor & entity."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional, Union

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
    TimeRWSensor,
    resolve_num,
)
from sunsynk.sensors import BinarySensor

if TYPE_CHECKING:
    from ha_addon_sunsynk_multi.a_inverter import AInverter


SS_TOPIC = "SUNSYNK/status"
_LOGGER = logging.getLogger(__name__)
"""An array of the Sunsynk driver instances."""
MQTT = MQTTClient()
"""The MQTTClient instance."""


@attrs.define(slots=True)
class ASensor:
    """Addon Sensor state & entity."""

    opt: SensorOption = attrs.field()
    # istate: int = attrs.field()
    entity: Optional[Entity] = attrs.field(default=None)
    "The entity will be None if hidden."

    def __hash__(self) -> int:
        """Hasable."""
        return self.opt.sensor.__hash__()

    @property
    def hidden(self) -> bool:
        """Hide state from HA."""
        return not self.opt.visible

    # hidden: bool = attrs.field(default=False)
    # "Hide state from HA."

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
            _LOGGER.warning("Cannot publish %s: value is None", self.name)
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

    def create_entity(
        self, dev: Union[Device, Entity, None], *, ist: AInverter
    ) -> Entity:
        """Create HASS entity."""
        # pylint: disable=too-many-branches
        if self.hidden:
            raise ValueError(f"Do not create hidden entities! {self}")
        if self.opt.sensor is None:
            raise ValueError(f"Cannot create entity if no sensor specified! {self}")
        if dev is None:
            raise ValueError(f"No device specified for create_entity! {self}")
        if isinstance(dev, Entity):
            dev = dev.device

        sensor = self.opt.sensor

        state_topic = f"{SS_TOPIC}/{dev.id}/{sensor.id}"
        command_topic = f"{state_topic}_set"

        ent = {  # type:ignore
            "device": dev,
            "name": sensor.name,
            "state_topic": state_topic,
            "unique_id": f"{dev.id}_{sensor.id}",
            "unit_of_measurement": sensor.unit,
            # https://github.com/kellerza/sunsynk/issues/165
            "discovery_extra": {
                "object_id": slug(f"{ist.opt.ha_prefix} {sensor.name}".strip()),
            },
        }

        if not isinstance(sensor, RWSensor):
            ent["device_class"] = hass_device_class(unit=sensor.unit)
            if isinstance(sensor, BinarySensor):
                self.entity = BinarySensorEntity(**ent)
            else:
                self.entity = SensorEntity(**ent)
            return self.entity

        ent.update(
            {
                "entity_category": "config",
                "icon": hass_default_rw_icon(unit=sensor.unit),
                "command_topic": command_topic,
                "on_change": lambda v: ist.write_queue.update({sensor: v}),
            }
        )

        if isinstance(sensor, NumberRWSensor):
            self.entity = NumberEntity(
                **ent,
                min=resolve_num(ist.get_state, sensor.min, 0),
                max=resolve_num(ist.get_state, sensor.max, 100),
                mode=OPT.number_entity_mode,
                step=0.1 if sensor.factor < 1 else 1,
            )
            return self.entity

        if isinstance(sensor, SwitchRWSensor):
            self.entity = SwitchEntity(**ent)
            return self.entity

        if isinstance(sensor, SelectRWSensor):
            self.entity = SelectEntity(
                **ent,
                options=sensor.available_values(),
            )
            return self.entity

        if isinstance(sensor, TimeRWSensor):
            ent["icon"] = "mdi:clock"
            self.entity = SelectEntity(
                **ent,
                options=sensor.available_values(15, ist.get_state),
            )
            return self.entity

        RWEntity._path = "text"  # pylint: disable=protected-access
        self.entity = RWEntity(**ent)
        return self.entity


@attrs.define(slots=True)
class TimeoutState(ASensor):
    """Entity definition for the timeout sensor."""

    retain = True

    def create_entity(
        self, dev: Union[Device, Entity, None], *, ist: AInverter
    ) -> Entity:
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
