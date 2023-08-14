"""Inverter state."""
import asyncio
import logging
import traceback
from typing import Callable, Iterable, Union

import attrs
from mqtt_entity import Device  # type: ignore[import]

from ha_addon_sunsynk_multi.a_sensor import MQTT, ASensor, TimeoutState
from ha_addon_sunsynk_multi.options import OPT, InverterOptions
from ha_addon_sunsynk_multi.sensor_options import DEFS, SOPT, SensorOption
from sunsynk.rwsensors import RWSensor
from sunsynk.sunsynk import Sensor, Sunsynk

_LOGGER = logging.getLogger(__name__)


@attrs.define(slots=True)
class AInverter:
    """Addon Inverter state (per inverter)."""

    # pylint: disable=too-few-public-methods

    inv: Sunsynk = attrs.field()
    opt: InverterOptions = attrs.field()
    ss: dict[str, ASensor] = attrs.field(factory=dict)  # pylint: disable=invalid-name
    """Sensor states."""

    read_errors: int = attrs.field(default=0)

    write_queue: dict[Sensor, Union[str, int, float]] = attrs.field(factory=dict)
    """Write queue for RWSensors."""

    @property
    def get_state(self) -> Callable:
        """Return the get_state function on the inverter."""
        return self.inv.state.get

    async def read_sensors(
        self,
        *,
        sensors: Iterable[Sensor],
        msg: str = "",
        retry_single: bool = False,
    ) -> bool:
        """Read from the Modbus interface."""
        try:
            await self.inv.read_sensors(sensors)
            self.read_errors = 0
            return True
        except asyncio.TimeoutError:
            pass
        except Exception as err:  # pylint:disable=broad-except
            _LOGGER.error("Read Error%s: %s: %s", msg, type(err), err)
            if OPT.debug > 1:
                traceback.print_exc()
            self.read_errors += 1
            await asyncio.sleep(0.02 * self.read_errors)
            if self.read_errors > 3:
                raise IOError(f"Multiple Modbus read errors: {err}") from err

        if retry_single:
            _LOGGER.info("Retrying individual sensors: %s", [s.id for s in sensors])
            for sen in sensors:
                await asyncio.sleep(0.02)
                await self.read_sensors(sensors=[sen], msg=sen.name, retry_single=False)

        return False

    async def publish_sensors(self, *, states: list[ASensor]) -> None:
        """Publish state to HASS."""
        for state in states:
            if state.hidden or state.opt.sensor is None:
                continue
            val = self.inv.state[state.opt.sensor]
            await state.publish(val)

    async def connect(self) -> None:
        """Connect."""
        _LOGGER.info("Connecting to %s", self.inv.port)
        try:
            await self.inv.connect()
        except ConnectionError as exc:
            raise ConnectionError(
                f"Could not connect to {self.inv.port}: {exc}"
            ) from exc

        _LOGGER.info(
            "Reading startup sensors %s", ", ".join(s.name for s in SOPT.startup)
        )

        if not await self.read_sensors(sensors=SOPT.startup):
            raise ConnectionError(
                f"No response on the Modbus interface {self.inv.port}, try checking the "
                "wiring to the Inverter, the USB-to-RS485 converter, etc"
            )

        expected_ser = self.opt.serial_nr.replace("_", "")
        if expected_ser != self.inv.state[DEFS.serial]:
            raise ValueError(
                f"Serial number mismatch. Expected {expected_ser}, got {self.inv.state[DEFS.serial]}"
            )

        self.log_bold(f"Inverter serial number '{self.inv.state[DEFS.serial]}'")

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

        ents = [
            s.create_entity(dev, ist=self) for s in self.ss.values() if not s.hidden
        ]
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

        self.ss["timeout"] = TimeoutState(
            entity=None, opt=SensorOption(sensor=DEF_TIMEOUT, visible=True)
        )
        # , istate=istate)


STATE: list[AInverter] = []


DEF_TIMEOUT = Sensor((), "timeout")
