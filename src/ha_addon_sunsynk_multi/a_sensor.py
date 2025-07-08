"""State of a sensor & entity."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import attrs
from mqtt_entity import (
    MQTTBinarySensorEntity,
    MQTTClient,
    MQTTEntity,
    MQTTNumberEntity,
    MQTTSelectEntity,
    MQTTSensorEntity,
    MQTTSwitchEntity,
    MQTTTextEntity,
)
from mqtt_entity.helpers import (
    MQTTEntityOptions,
    hass_default_rw_icon,
    hass_device_class,
)

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
from sunsynk.sensors import BinarySensor, EnumSensor

from .options import OPT
from .sensor_options import SensorOption

if TYPE_CHECKING:
    from .a_inverter import AInverter


SS_TOPIC = "SS"
_LOGGER = logging.getLogger(__name__)
"""An array of the Sunsynk driver instances."""
MQTT = MQTTClient(devs=[], origin_name="Sunsynk Add-on")
"""The MQTTClient instance."""


@attrs.define(slots=True)
class ASensor:
    """Addon Sensor state & entity."""

    opt: SensorOption
    # istate: int = attrs.field()
    entity: MQTTEntity | None = None
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
        await self.entity.send_state(MQTT, val, retain=self.retain)
        self._last = val

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self.opt.sensor.name

    def is_measurement(self, units: str) -> bool:
        """Return True if the units are a measurement."""
        return units in {"W", "V", "A", "Hz", "°C", "°F", "%", "Ah", "VA"}

    def visible_on(self, ist: AInverter) -> bool:
        """Is entity visible on this inverter."""
        if not self.opt.visible:
            return False
        if self.opt.first and ist.index > 0:
            return False
        if self.opt.sensor is None:
            return False
        return True

    def create_entity(self, ist: AInverter, /) -> MQTTEntity:
        """Create HASS entity."""
        dev_id = ist.opt.serial_nr
        # pylint: disable=too-many-branches,too-many-return-statements
        if not self.visible_on(ist):
            raise ValueError("Entity not visible")
        if self.opt.sensor is None:
            raise ValueError(f"Cannot create entity if no sensor specified: {self}")
        if not dev_id:
            raise ValueError(f"No device specified for create_entity: {self}")

        sensor = self.opt.sensor

        state_topic = f"{SS_TOPIC}/{ist.opt.ha_prefix}/{sensor.id}"
        command_topic = f"{state_topic}_set"

        ent: MQTTEntityOptions = {
            "name": sensor.name,
            "object_id": slug(f"{ist.opt.ha_prefix} {sensor.name}".strip()),
            "state_topic": state_topic,
            "unique_id": f"{dev_id}_{sensor.id}",
            "unit_of_measurement": sensor.unit,
        }

        if isinstance(sensor, EnumSensor):
            self.entity = MQTTSensorEntity(
                **ent,
                # options=sensor.available_values(),
            )
            return self.entity

        if not isinstance(sensor, RWSensor):
            ent["device_class"] = hass_device_class(unit=sensor.unit)
            if isinstance(sensor, BinarySensor):
                self.entity = MQTTBinarySensorEntity(**ent)
            else:
                if self.is_measurement(sensor.unit):
                    ent["state_class"] = "measurement"
                self.entity = MQTTSensorEntity(**ent, suggested_display_precision=1)
            return self.entity

        async def on_change(val: float | str | bool) -> None:
            """On change callback."""
            _LOGGER.info("Queue update %s=%s", sensor.id, val)
            ist.write_queue.update({sensor: val})
            await self.publish(val)

        ent["entity_category"] = "config"
        ent["icon"] = hass_default_rw_icon(unit=sensor.unit)

        if isinstance(sensor, NumberRWSensor):
            self.entity = MQTTNumberEntity(
                **ent,
                command_topic=command_topic,
                min=resolve_num(ist.get_state, sensor.min, 0),
                max=resolve_num(ist.get_state, sensor.max, 100),
                mode=OPT.number_entity_mode,
                step=0.1 if sensor.factor < 1 else 1,
                suggested_display_precision=1,
                on_command=on_change,
            )
            return self.entity

        if isinstance(sensor, (SwitchRWSensor | SwitchRWSensor0)):
            self.entity = MQTTSwitchEntity(
                **ent,
                command_topic=command_topic,
                on_command=on_change,
            )
            return self.entity

        if isinstance(sensor, SelectRWSensor):
            self.entity = MQTTSelectEntity(
                **ent,
                command_topic=command_topic,
                options=sensor.available_values(),
                on_command=on_change,
            )
            return self.entity

        if isinstance(sensor, TimeRWSensor):
            ent["icon"] = "mdi:clock"
            self.entity = MQTTSelectEntity(
                **ent,
                command_topic=command_topic,
                options=sensor.available_values(OPT.prog_time_interval, ist.get_state),
                on_command=on_change,
            )
            return self.entity

        ent["entity_category"] = "diagnostic"

        self.entity = MQTTTextEntity(
            **ent,
            command_topic=command_topic,
            on_command=on_change,
        )
        return self.entity


@attrs.define(slots=True)
class TimeoutState(ASensor):
    """Entity definition for the timeout sensor."""

    def create_entity(self, ist: AInverter, /) -> MQTTEntity:
        """MQTT entities for stats."""
        dev_id = ist.opt.serial_nr
        if not dev_id:
            raise ValueError(f"No device specified for create_entity! {self}")

        self.entity = MQTTSensorEntity(
            name="RS485 timeouts",
            unique_id=f"{dev_id}_timeouts",
            state_topic=f"{SS_TOPIC}/{ist.opt.ha_prefix}/timeouts",
            entity_category="config",
        )
        return self.entity
