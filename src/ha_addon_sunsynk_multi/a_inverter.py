"""Inverter state."""

import asyncio
import logging
import traceback
from typing import Callable, Iterable

import attrs
from mqtt_entity import Device, Entity, SensorEntity  # type: ignore[import]
from mqtt_entity.helpers import set_attributes  # type: ignore[import]
from mqtt_entity.utils import tostr  # type: ignore[import]

from ha_addon_sunsynk_multi.a_sensor import MQTT, SS_TOPIC, ASensor
from ha_addon_sunsynk_multi.options import OPT, InverterOptions
from ha_addon_sunsynk_multi.sensor_options import DEFS, SOPT
from ha_addon_sunsynk_multi.timer_callback import Callback
from sunsynk.helpers import slug
from sunsynk.rwsensors import RWSensor
from sunsynk.sunsynk import Sensor, Sunsynk, ValType

_LOGGER = logging.getLogger(__name__)


@attrs.define(slots=True, kw_only=True)
class AInverter:
    """Addon Inverter state (per inverter)."""

    # pylint:disable=too-many-instance-attributes

    index: int
    inv: Sunsynk
    opt: InverterOptions
    ss: dict[str, ASensor] = attrs.field(factory=dict)
    """Sensor states."""

    read_errors: int = attrs.field(default=0, init=False)

    write_queue: dict[Sensor, str | int | float | bool] = attrs.field(factory=dict)
    """Write queue for RWSensors."""

    # Reporting stats
    entity_timeout: SensorEntity = attrs.field(init=False)
    entity_cbstats: SensorEntity = attrs.field(init=False)
    cb: Callback = attrs.field(init=False)

    @property
    def get_state(self) -> Callable:
        """Return the get_state function on the inverter."""
        return self.inv.state.get

    async def read_sensors(self, *, sensors: Iterable[Sensor], msg: str = "") -> None:
        """Read from the Modbus interface."""
        try:
            await asyncio.sleep(0.005)
            await self.inv.read_sensors(sensors)
            self.read_errors = 0
        except (
            Exception,  # pylint:disable=broad-except
            asyncio.exceptions.CancelledError,
        ) as err:
            self.read_errors += 1
            if msg:
                arg0, *argn = err.args if err.args else ("",)
                err.args = tuple([f"{arg0} {msg}".strip()] + argn)

            if OPT.debug > 1:
                traceback.print_exc()
            raise

    async def read_sensors_retry(self, *, sensors: list[Sensor], msg: str = "") -> bool:
        """Read sensors with a retry."""
        while True:
            try:
                await self.read_sensors(sensors=sensors, msg=msg)
                return True
            except asyncio.exceptions.CancelledError as err:
                _LOGGER.error("Timeout %s", err)
            except Exception as err:  # pylint:disable=broad-except
                _LOGGER.error("%s", err)
            await asyncio.sleep(0.1)
            if self.read_errors > 2:
                break

        if len(sensors) == 1:
            return False

        _LOGGER.warning("Retrying individual sensors: %s", [s.id for s in sensors])
        errs = []
        for sen in sensors:
            await asyncio.sleep(0.02)
            if not await self.read_sensors_retry(sensors=[sen], msg=sen.name):
                errs.append(sen.name)

        if errs:
            _LOGGER.critical("Could not read sensors: %s", errs)
            return False
        return True

    async def publish_sensors(self, *, states: dict[ASensor, ValType]) -> None:
        """Publish state to HASS."""
        for state, value in states.items():
            # Entity was never created, don't publish state
            if not state.entity:
                continue
            if value is None:
                value = self.inv.state[state.opt.sensor]
            await state.publish(value)

    async def connect(self) -> None:
        """Connect."""
        _LOGGER.info("Connecting to %s", self.inv.port)
        try:
            await self.inv.connect()
        except ConnectionError as exc:
            raise ConnectionError(
                f"Could not connect to {self.inv.port}: {exc}"
            ) from exc

        sensors = list(SOPT.startup)
        _LOGGER.info("Reading startup sensors %s", ", ".join(s.name for s in sensors))

        if not await self.read_sensors_retry(sensors=sensors):
            raise ConnectionError(
                f"No response on the Modbus interface {self.inv.port}, "
                "see https://kellerza.github.io/sunsynk/guide/fault-finding"
            )
        expected_ser = self.opt.serial_nr.replace("_", "")
        actual_ser = str(self.inv.state[DEFS.serial])
        if expected_ser != actual_ser:
            raise ValueError(
                f"Serial number mismatch. Expected {expected_ser}, got {actual_ser}"
            )
        self.log_bold(f"Inverter serial number '****{actual_ser[-4:]}'")

        _LOGGER.info(
            "Device type: %s, using the %s sensor definitions",
            self.inv.state[DEFS.device_type],
            OPT.sensor_definitions,
        )

        # Initial read for all sensors
        sensors = list(SOPT)
        _LOGGER.info("Reading all sensors %s", ", ".join(s.name for s in sensors))
        await self.read_sensors(sensors=sensors)

    @property
    def rated_power(self) -> float:
        """Return the inverter power."""
        try:
            return float(self.inv.state[DEFS.rated_power])  # type:ignore
        except (ValueError, TypeError):
            return 0

    def log_bold(self, msg: str) -> None:
        """Log a message."""
        _LOGGER.info("#" * 60)
        _LOGGER.info(f"{msg:^60}".rstrip())
        _LOGGER.info("#" * 60)

    async def hass_discover_sensors(self) -> bool:
        """Discover all sensors."""
        serial_nr = self.opt.serial_nr

        dev = Device(
            identifiers=[serial_nr],
            # https://github.com/kellerza/sunsynk/issues/165
            # name=f"{OPT.manufacturer} AInverter {serial_nr}",
            name=self.opt.ha_prefix,
            # OPT.manufacturer,  # new option?
            model=f"{int(self.rated_power/1000)}kW Inverter (**{serial_nr[-4:]})",
            manufacturer=OPT.manufacturer,
        )

        ents: list[Entity] = []
        for s in self.ss.values():
            if not s.visible_on(self):
                continue
            try:
                ents.append(s.create_entity(dev, ist=self))
            except Exception as err:  # pylint:disable=broad-except
                _LOGGER.error("Could not create MQTT entity for %s: %s", s, err)
        ents.extend(self.create_stats_entities(dev))
        await MQTT.connect(OPT)
        await MQTT.publish_discovery_info(entities=ents)
        return True

    def init_sensors(self) -> None:
        """Initialize the sensors."""
        # Track startup sensors
        for sen in SOPT.startup:
            self.inv.state.track(sen)

        # create state entry
        for sopt in SOPT.values():
            sen = sopt.sensor
            self.inv.state.track(sen)
            self.ss[sen.id] = ASensor(opt=sopt, retain=isinstance(sen, RWSensor))

    def create_stats_entities(self, dev: Device) -> list[SensorEntity]:
        """Create entities."""
        name = "timeout"
        self.entity_timeout = SensorEntity(
            name="RS485 timeout",
            unique_id=f"{dev.id}_{name}",
            unit_of_measurement=" ",
            state_topic=f"{SS_TOPIC}/{dev.id}/{name}",
            entity_category="diagnostic",
            device=dev,
            discovery_extra={
                "object_id": slug(f"{self.opt.ha_prefix} {name}".strip()),
            },
        )
        name = "cb_stats"
        self.entity_cbstats = SensorEntity(
            name="Callback stats",
            unique_id=f"{dev.id}_{name}",
            unit_of_measurement=" ",
            state_topic=f"{SS_TOPIC}/{dev.id}/{name}",
            json_attributes_topic=f"{SS_TOPIC}/{dev.id}/{name}_attr",
            entity_category="diagnostic",
            device=dev,
            discovery_extra={
                "object_id": slug(f"{self.opt.ha_prefix} {name}".strip()),
            },
        )
        return [self.entity_cbstats, self.entity_timeout]

    async def publish_stats(self, period: int) -> None:
        """Publish stats."""
        await MQTT.connect(OPT)
        await MQTT.publish(
            topic=self.entity_timeout.state_topic,
            payload=tostr(self.inv.timeouts),
            retain=False,
        )

        # calc stats
        lc_avg, lc_i = stats(self.cb.stat_time, include=lambda x: x > self.cb.every)
        slip_a, slip_i = stats(self.cb.stat_slip)
        attr = {
            "period": f"{period}s",
            "long_calls": lc_i,
            "long_calls_avg": f"{lc_avg}s",
            "slips": slip_i,
            "slips_avg": f"{slip_a}s",
            "busy": self.cb.stat_busy,
        }
        await MQTT.publish(
            topic=self.entity_cbstats.state_topic,
            payload=tostr(len(self.cb.stat_time)),
            retain=False,
        )
        await set_attributes(attr, entity=self.entity_cbstats, client=MQTT)

        self.cb.stat_busy = 0
        self.cb.stat_time.clear()
        self.cb.stat_slip.clear()


STATE: list[AInverter] = []


def stats(
    samples: list[int] | list[float],
    *,
    include: Callable[[int | float], bool] = bool,
) -> tuple[str, str]:
    """Calculate average for the samples."""
    subset = [t for t in samples if include(t)]
    ssinfo = f"{len(subset)}/{len(samples)}"
    if subset:
        return (f"{sum(subset) / len(subset):.2f}", ssinfo)
    return ("0", ssinfo)
