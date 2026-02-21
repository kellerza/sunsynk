"""Inverter state."""

import asyncio
import logging
import traceback
from collections.abc import AsyncGenerator, Callable, Iterable
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar

from mqtt_entity import MQTTDevice, MQTTSensorEntity

from sunsynk.helpers import slug
from sunsynk.rwsensors import RWSensor
from sunsynk.state import InverterState
from sunsynk.sunsynk import Sensor, Sunsynk, ValType
from sunsynk.utils import pretty_table_sensors

from .a_sensor import MQTT, SS_TOPIC, ASensor
from .options import OPT, InverterOptions
from .sensor_options import DEFS, SOPT, SensorOptions
from .timer_callback import AsyncCallback

if TYPE_CHECKING:
    from .sensor_callback import SensorSchedule

_LOG = logging.getLogger(__name__)


@dataclass(kw_only=True)
class AInverter:
    """Addon Inverter state (per inverter)."""

    index: int
    opt: InverterOptions
    ss: dict[str, ASensor] = field(default_factory=dict)
    """Sensor states."""

    sched: "SensorSchedule" = field(init=False)

    mqtt_dev: MQTTDevice = field(
        default_factory=lambda: MQTTDevice(components={}, identifiers=[""])
    )
    """MQTT Device for the inverter."""

    read_errors: int = field(default=0, init=False)

    write_queue: dict[Sensor, str | int | float | bool] = field(default_factory=dict)
    """Write queue for RWSensors."""

    # Reporting stats
    entity_timeout: MQTTSensorEntity = field(init=False)
    entity_cbstats: MQTTSensorEntity = field(init=False)
    cb: AsyncCallback = field(init=False)

    state: InverterState = field(default_factory=InverterState)
    """The inverter state, which tracks all sensors and their values.

    During a lock_io this will be the state on the sunsynk driver."""

    connectors: ClassVar[dict[tuple[str, str], tuple[Sunsynk, asyncio.Lock]]] = {}
    """Inverter connectors and locks, keyed by (port, driver)."""

    @classmethod
    def add_connector(cls, inv_opt: InverterOptions, ss: Sunsynk) -> None:
        """Add a connector."""
        if (inv_opt.port, inv_opt.driver) in cls.connectors:
            raise ValueError(
                f"Connector for port {inv_opt.port} and driver {inv_opt.driver} already exists"
            )
        cls.connectors[(inv_opt.port, inv_opt.driver)] = (ss, asyncio.Lock())

    @property
    def connector(self) -> tuple[Sunsynk, asyncio.Lock]:
        """Get the connector for this inverter."""
        return self.connectors[(self.opt.port, self.opt.driver)]

    @asynccontextmanager
    async def lock_io(self) -> AsyncGenerator[Sunsynk]:
        """Lock the IO."""
        inv, lock = self.connector
        async with lock:
            inv.server_id = self.opt.modbus_id
            inv.state = self.state
            yield inv

    async def read_sensors(self, *, sensors: Iterable[Sensor], msg: str = "") -> None:
        """Read from the Modbus interface."""
        async with self.lock_io() as inv:
            try:
                await asyncio.sleep(0.005)
                await inv.read_sensors(sensors)
                self.read_errors = 0
            except (
                Exception,
                asyncio.exceptions.CancelledError,
            ) as err:
                self.read_errors += 1
                if msg:
                    arg0, *argn = err.args if err.args else ("",)
                    err.args = tuple([f"{arg0} {msg}".strip(), *argn])

                if OPT.debug > 1:
                    traceback.print_exc()
                raise

    async def write_sensor(
        self, sensor: RWSensor, value: ValType, *, msg: str = ""
    ) -> None:
        """Write to the Modbus interface."""
        async with self.lock_io() as inv:
            await inv.write_sensor(sensor, value, msg=msg)

    async def read_sensors_retry(self, *, sensors: list[Sensor], msg: str = "") -> bool:
        """Read sensors with a retry."""
        while True:
            try:
                await self.read_sensors(sensors=sensors, msg=msg)
                return True
            except asyncio.exceptions.CancelledError as err:
                _LOG.error("Timeout %s", err)
            except Exception as err:
                _LOG.error("%s", err)
            await asyncio.sleep(0.1)
            if self.read_errors > 2:
                break

        if len(sensors) == 1:
            return False

        _LOG.warning("Retrying individual sensors: %s", [s.id for s in sensors])
        errs = []
        for sen in sensors:
            await asyncio.sleep(0.02)
            if not await self.read_sensors_retry(sensors=[sen], msg=sen.name):
                errs.append(sen.name)

        if errs:
            _LOG.critical("Could not read sensors: %s", errs)
            return False
        return True

    async def publish_sensors(self, *, states: dict[ASensor, ValType]) -> None:
        """Publish state to HASSH."""
        for state, value in states.items():
            # Entity was never created, don't publish state
            if not state.entity:
                continue
            if value is None:
                await state.publish(self.state[state.opt.sensor])
            else:
                await state.publish(value)

    async def connect(self) -> None:
        """Connect."""
        async with self.lock_io() as inv:
            _LOG.info("Connecting to %s", inv.port)
            try:
                await inv.connect()
            except ConnectionError as exc:
                raise ConnectionError(
                    f"Could not connect to {inv.port}: {exc}"
                ) from exc

        sensors = list(SOPT.startup)
        _LOG.info("Reading startup sensors %s", ", ".join(s.name for s in sensors))

        if not await self.read_sensors_retry(sensors=sensors):
            raise ConnectionError(
                f"No response on the Modbus interface {self.opt.port}, "
                "see https://kellerza.github.io/sunsynk/guide/fault-finding"
            )
        expected_ser = self.opt.serial_nr.replace("_", "")
        actual_ser = str(self.state[DEFS.serial])
        if expected_ser != actual_ser:
            raise ValueError(
                f"Serial number mismatch. Expected {expected_ser}, got {actual_ser}"
            )

        # All seem ok
        add_info = {"device_type": [f"config: {OPT.sensor_definitions}"]}
        tab = pretty_table_sensors(sensors, self.state, ["Info"], add_info)
        _LOG.info("Inverter %s - startup sensors\n%s", self.index, tab)

        # Initial read for all sensors
        sensors = list(SOPT)
        _LOG.info("Reading configured sensors %s", len(sensors))
        await self.read_sensors(sensors=sensors)
        # tab = pretty_table_sensors(sensors, self.inv)
        # _LOG.info("Inverter %s - active sensors\n%s", self.inv.port, tab)

    @property
    def rated_power(self) -> float:
        """Return the inverter power."""
        try:
            return float(self.state[DEFS.rated_power])  # type:ignore[arg-type]
        except (ValueError, TypeError):
            return 0

    def log_bold(self, msg: str) -> None:
        """Log a message."""
        _LOG.info("#" * 60)
        _LOG.info(f"{msg:^60}".rstrip())
        _LOG.info("#" * 60)

    def hass_create_discovery_info(self) -> None:
        """Create discovery info for the inverter."""
        serial_nr = self.opt.serial_nr

        ids = list(self.mqtt_dev.components)

        if self.mqtt_dev.id == "":
            self.mqtt_dev = MQTTDevice(
                identifiers=[serial_nr],
                # https://github.com/kellerza/sunsynk/issues/165
                # name=f"{OPT.manufacturer} AInverter {serial_nr}",
                name=self.opt.ha_prefix,
                model=f"{int(self.rated_power / 1000)}kW Inverter (**{serial_nr[-4:]})",
                manufacturer=OPT.manufacturer,
                components={},
            )
            MQTT.devs.append(self.mqtt_dev)
            self.create_stats_entities()
            for s in self.ss.values():
                if s.visible_on(self):
                    ids.append(s.opt.sensor.id)

        for s in self.ss.values():
            if s.opt.sensor.id not in ids:
                continue
            try:
                s.entity = s.create_entity(self)
                self.mqtt_dev.components[s.opt.sensor.id] = s.entity
            except Exception as err:
                _LOG.error("Could not create MQTT entity for %s: %s", s, err)

            # if hasattr(s.opt.sensor, "rated_power"):
            #     s.opt.sensor.rated_power = int(self.rated_power)  # type:ignore[]

    async def hass_discover_sensors(self) -> bool:
        """Discover all sensors."""
        self.hass_create_discovery_info()
        await MQTT.connect(OPT)
        MQTT.monitor_homeassistant_status()
        return True

    def init_sensors(self, soptions: SensorOptions | None = None) -> None:
        """Initialize the sensors."""
        soptions = soptions or SOPT
        # Track startup sensors
        for sen in soptions.startup:
            self.state.track(sen)

        # create state entry
        for sopt in soptions.values():
            sen = sopt.sensor
            self.state.track(sen)
            self.ss[sen.id] = ASensor(opt=sopt, retain=isinstance(sen, RWSensor))

    def create_stats_entities(self) -> None:
        """Create entities."""
        dev_id = self.mqtt_dev.id
        name = "timeout"
        self.entity_timeout = MQTTSensorEntity(
            name="RS485 timeout",
            unique_id=f"{dev_id}_{name}",
            unit_of_measurement=" ",
            state_topic=f"{SS_TOPIC}/{self.opt.ha_prefix}/{name}",
            entity_category="diagnostic",
            default_entity_id=slug(f"{self.opt.ha_prefix} {name}".strip()),
        )
        self.mqtt_dev.components[name] = self.entity_timeout
        name = "cb_stats"
        self.entity_cbstats = MQTTSensorEntity(
            name="Callback stats",
            unique_id=f"{self.mqtt_dev.id}_{name}",
            unit_of_measurement=" ",
            state_topic=f"{SS_TOPIC}/{self.opt.ha_prefix}/{name}",
            json_attributes_topic=f"{SS_TOPIC}/{self.opt.ha_prefix}/{name}_attr",
            entity_category="diagnostic",
            default_entity_id=slug(f"{self.opt.ha_prefix} {name}".strip()),
        )
        self.mqtt_dev.components[name] = self.entity_cbstats

    async def publish_stats(self, period: int) -> None:
        """Publish stats."""
        await self.entity_timeout.send_state(MQTT, self.connector[0].timeouts)

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
        await self.entity_cbstats.send_state(MQTT, len(self.cb.stat_time))
        await self.entity_cbstats.send_json_attributes(MQTT, attr)

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
