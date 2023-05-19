"""State of a sensor & entity."""
import logging
from typing import Callable, Optional, Union

import attrs
from filter import Filter
from mqtt_entity import (
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
from mqtt_entity.helpers import hass_default_rw_icon, hass_device_class
from mqtt_entity.utils import tostr
from options import OPT, InverterOptions

from sunsynk.helpers import ValType
from sunsynk.rwsensors import (
    NumberRWSensor,
    RWSensor,
    SelectRWSensor,
    SwitchRWSensor,
    TimeRWSensor,
    resolve_num,
)
from sunsynk.sensors import BinarySensor
from sunsynk.sunsynk import Sensor, Sunsynk

SENSOR_PREFIX: dict[str, str] = {}
"""Sensor prefix per mqtt device id."""

SS_TOPIC = "SUNSYNK/status"
_LOGGER = logging.getLogger(__name__)
"""An array of the Sunsynk driver instances."""
MQTT = MQTTClient()
"""The MQTTClient instance."""


@attrs.define(slots=True)
class State:  # pylint: disable=too-few-public-methods
    """State of a sensor / entity."""

    filter: Optional[Filter] = attrs.field()
    sensor: Optional[Sensor] = attrs.field()
    istate: int = attrs.field()
    entity: Optional[Entity] = attrs.field(default=None)
    "The entity will be None if hidden."
    hidden: bool = attrs.field(default=False)
    "Hide state from HA."

    _last: ValType = None
    retain: bool = False

    @property
    def value(self) -> ValType:
        """Return the last value."""
        return self._last

    async def publish(self, val: ValType) -> None:
        """Set the value through MQTT."""
        if self.entity is None:
            _LOGGER.error("no entity %s", self.sensor)
            return
        if val is None or (self._last == val and self.retain):
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
        """Return the name of the sensor and filter."""
        nme = self.sensor.name if self.sensor else ""
        # nme = getattr(self.sensor, "name", str(self.sensor))
        # if isinstance(self, SCFilter):
        #     nme += ":step"
        if not self.filter:
            return nme
        return f"{nme}:{self.filter._filter.__name__}"  # pylint: disable=no-member,protected-access

    @property
    def get_state(self) -> Callable:
        """Get the inverter state."""
        return STATE[self.istate].inv.state.get

    def create_entity(self, dev: Union[Device, Entity, None]) -> Entity:
        """Create HASS entities out of an existing list of filters.

        get_state = SS[0].state.get
        """
        # def create_on_change_handler(sensor: RWSensor, value_func: Callable) -> Callable:
        #     def _handler(value: Any) -> None:

        #     return _handler

        if self.hidden:
            raise ValueError(f"Do not create hidden entities! {self}")
        if self.sensor is None:
            raise ValueError(f"Cannot create entity if no sensor specified! {self}")
        if dev is None:
            raise ValueError(f"No device specified for create_entity! {self}")
        if isinstance(dev, Entity):
            dev = dev.device

        sensor = self.sensor

        state_topic = f"{SS_TOPIC}/{dev.id}/{sensor.id}"
        command_topic = f"{state_topic}_set"

        ent = {  # type:ignore
            "device": dev,
            "name": f"{SENSOR_PREFIX[dev.id]} {sensor.name}".strip(),
            "state_topic": state_topic,
            "unique_id": f"{dev.id}_{sensor.id}",
            "unit_of_measurement": sensor.unit,
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
                "on_change": lambda v: SENSOR_WRITE_QUEUE.update(
                    {(self.istate, sensor): v}
                ),
            }
        )

        if isinstance(sensor, NumberRWSensor):
            self.entity = NumberEntity(
                **ent,
                min=resolve_num(self.get_state, sensor.min, 0),
                max=resolve_num(self.get_state, sensor.max, 100),
                mode=OPT.number_entity_mode,
                step=0.1 if sensor.factor < 1 else 1,
            )

        elif isinstance(sensor, SwitchRWSensor):
            self.entity = SwitchEntity(**ent)

        elif isinstance(sensor, SelectRWSensor):
            self.entity = SelectEntity(
                **ent,
                options=sensor.available_values(),
            )

        elif isinstance(sensor, TimeRWSensor):
            ent["icon"] = "mdi:clock"
            self.entity = SelectEntity(
                **ent,
                options=sensor.available_values(15, self.get_state),
            )

        else:
            RWEntity._path = "text"  # pylint: disable=protected-access
            self.entity = RWEntity(**ent)
        return self.entity


@attrs.define(slots=True)
class TimeoutState(State):
    """Entity definition for the timeout sensor."""

    retain = True

    def create_entity(self, dev: Union[Device, Entity, None]) -> Entity:
        """MQTT entities for stats."""
        if dev is None:
            raise ValueError(f"No device specified for create_entity! {self}")
        if isinstance(dev, Entity):
            dev = dev.device

        self.entity = SensorEntity(
            name=f"{SENSOR_PREFIX[dev.id]} RS485 timeouts",
            unique_id=f"{dev.id}_timeouts",
            state_topic=f"{SS_TOPIC}/{dev.id}/timeouts",
            entity_category="config",
            device=dev,
        )
        return self.entity


SENSOR_WRITE_QUEUE: dict[tuple[int, Sensor], Union[str, int, float]] = {}


@attrs.define(slots=True)
class AllStates:
    """Multiple inverter states."""

    # pylint: disable=too-few-public-methods

    inv: Sunsynk
    state: dict[str, State]
    opt: InverterOptions


STATE: list[AllStates] = []
