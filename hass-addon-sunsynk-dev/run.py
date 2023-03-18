#!/usr/bin/env python3
"""Run the addon."""
import asyncio
import logging
import sys
from asyncio.events import AbstractEventLoop
from collections import defaultdict
from json import loads
from math import modf
from pathlib import Path
from typing import Any, Callable, Dict, List, Sequence, Tuple

import yaml
from filter import RROBIN, Filter, getfilter, suggested_filter
from mqtt import (
    MQTT,
    Device,
    Entity,
    NumberEntity,
    SelectEntity,
    SensorEntity,
    hass_default_rw_icon,
    hass_device_class,
)
from options import OPT, SS_TOPIC

from sunsynk.definitions import ALL_SENSORS, DEPRECATED, RATED_POWER, WATT, MathSensor
from sunsynk.helpers import slug
from sunsynk.rwsensors import NumberRWSensor, RWSensor, SelectRWSensor, TimeRWSensor
from sunsynk.sunsynk import Sensor, Sunsynk

_LOGGER = logging.getLogger(__name__)


DEVICE: Device = None  # type:ignore
HASS_DISCOVERY_INFO_UPDATE_QUEUE: Dict[str, Filter] = {}
HIDDEN_SENSOR_IDS: set[str] = set()
SENSORS: List[Filter] = []
SENSOR_WRITE_QUEUE: Dict[str, Tuple[Filter, Any]] = {}
SERIAL = ALL_SENSORS["serial"]
STARTUP_SENSORS: List[Sensor] = []
SUNSYNK: Sunsynk = None  # type: ignore


def tostr(val: Any) -> str:
    """Convert a value to a string with maximum 3 decimal places."""
    if val is None:
        return ""
    if not isinstance(val, float):
        return str(val)
    if modf(val)[0] == 0:
        return str(int(val))
    return f"{val:.3f}".rstrip("0")


async def publish_sensors(sensors: List[Filter], *, force: bool = False) -> None:
    """Publish sensors."""
    res = None
    for fsen in sensors:
        if isinstance(fsen, Filter):
            res = fsen.update(fsen.sensor.value)
            if force and res is None:
                res = fsen.sensor.value
        if res is None:
            continue
        await MQTT.connect(OPT)
        await MQTT.publish(
            topic=f"{SS_TOPIC}/{OPT.sunsynk_id}/{fsen.sensor.id}",
            payload=tostr(res),
            retain=isinstance(fsen.sensor, RWSensor),  # where entity_category="config"
        )


async def hass_discover_sensors(serial: str, rated_power: float) -> None:
    """Discover all sensors."""
    dev = Device(
        identifiers=[OPT.sunsynk_id],
        name=f"Sunsynk Inverter {serial}",
        model=f"{int(rated_power/1000)}kW Inverter {serial}",
        manufacturer="Sunsynk",
    )
    global DEVICE  # pylint: disable=global-statement
    DEVICE = dev

    ents = create_entities(SENSORS, dev)

    await MQTT.connect(OPT)
    await MQTT.publish_discovery_info(entities=ents)


def enqueue_hass_discovery_info_update(changed_sen: Sensor, deps: List[Filter]) -> None:
    """Add a sensor's dependants to the HASS discovery info update queue."""
    if not DEVICE:
        return

    _LOGGER.debug(
        "%s changed: Enqueuing discovery info updates for %s",
        changed_sen.name,
        ", ".join(sorted(f.sensor.name for f in deps)),
    )
    HASS_DISCOVERY_INFO_UPDATE_QUEUE.update((f.sensor.id, f) for f in deps)


async def hass_update_discovery_info() -> None:
    """Update discovery info for existing sensors"""
    if not HASS_DISCOVERY_INFO_UPDATE_QUEUE:
        return

    sens = list(HASS_DISCOVERY_INFO_UPDATE_QUEUE.values())
    ents = create_entities(sens, DEVICE)
    HASS_DISCOVERY_INFO_UPDATE_QUEUE.clear()

    await MQTT.connect(OPT)
    await MQTT.publish_discovery_info(entities=ents, remove_entities=False)

    # Force state update:
    # https://github.com/home-assistant/core/issues/84844#issuecomment-1368045986
    await publish_sensors(sens, force=True)


def create_entities(sensors: list[Filter], dev: Device) -> list[Entity]:
    """Create HASS entities out of an existing list of filters"""
    ents: List[Entity] = []

    def create_on_change_handler(filt: Filter, value_func: Callable) -> Callable:
        def _handler(value: Any) -> None:
            SENSOR_WRITE_QUEUE[filt.sensor.id] = (filt, value_func(value))

        return _handler

    sensors = [s for s in sensors if s.sensor.id not in HIDDEN_SENSOR_IDS]

    for filt in sensors:
        sensor = filt.sensor

        state_topic = f"{SS_TOPIC}/{OPT.sunsynk_id}/{sensor.id}"
        command_topic = f"{state_topic}_set"

        ent = {
            "device": dev,
            "name": f"{OPT.sensor_prefix} {sensor.name}".strip(),
            "state_topic": state_topic,
            "unique_id": f"{OPT.sunsynk_id}_{sensor.id}",
            "unit_of_measurement": sensor.unit,
        }

        if isinstance(sensor, RWSensor):
            ent["entity_category"] = "config"
            ent["icon"] = hass_default_rw_icon(unit=sensor.unit)
        else:
            ent["device_class"] = hass_device_class(unit=sensor.unit)

        if isinstance(sensor, NumberRWSensor):
            ents.append(
                NumberEntity(
                    **ent,
                    command_topic=command_topic,
                    min=float(sensor.min_value),
                    max=float(sensor.max_value),
                    mode=OPT.number_entity_mode,
                    on_change=create_on_change_handler(filt, float),
                    step=0.1 if sensor.factor < 1 else 1,
                )
            )
            continue

        if isinstance(sensor, SelectRWSensor):
            ents.append(
                SelectEntity(
                    **ent,
                    command_topic=command_topic,
                    options=sensor.available_values(),
                    on_change=create_on_change_handler(filt, str),
                )
            )
            continue

        if isinstance(sensor, TimeRWSensor):
            ent["icon"] = "mdi:clock"
            ents.append(
                SelectEntity(
                    **ent,
                    command_topic=command_topic,
                    options=sensor.available_values(step_minutes=15),
                    on_change=create_on_change_handler(filt, str),
                )
            )
            continue

        ents.append(SensorEntity(**ent))

    return ents


def setup_driver() -> None:
    """Setup the correct driver."""
    # pylint: disable=import-outside-toplevel
    global SUNSYNK  # pylint: disable=global-statement
    if OPT.driver == "pymodbus":
        from sunsynk.pysunsynk import pySunsynk

        SUNSYNK = pySunsynk()
        if not OPT.port:
            OPT.port = OPT.device

    elif OPT.driver == "umodbus":
        from sunsynk.usunsynk import uSunsynk

        SUNSYNK = uSunsynk()
        if not OPT.port:
            OPT.port = "serial://" + OPT.device

    else:
        _LOGGER.critical("Invalid DRIVER: %s. Expected umodbus, pymodbus", OPT.driver)
        sys.exit(-1)

    SUNSYNK.port = OPT.port
    SUNSYNK.server_id = OPT.modbus_server_id
    SUNSYNK.timeout = OPT.timeout
    SUNSYNK.read_sensors_batch_size = OPT.read_sensors_batch_size


def startup() -> None:
    """Read the hassos configuration."""
    logging.basicConfig(
        format="%(asctime)s %(levelname)-7s %(message)s", level=logging.DEBUG
    )

    hassosf = Path("/data/options.json")
    if hassosf.exists():
        _LOGGER.info("Loading HASS OS configuration")
        OPT.update(loads(hassosf.read_text(encoding="utf-8")))
    else:
        _LOGGER.info(
            "Local test mode - Defaults apply. Pass MQTT host & password as arguments"
        )
        configf = Path(__file__).parent / "config.yaml"
        OPT.update(yaml.safe_load(configf.read_text()).get("options", {}))
        OPT.mqtt_host = sys.argv[1]
        OPT.mqtt_password = sys.argv[2]
        OPT.debug = 1

    if OPT.profiles:
        _LOGGER.info("PROFILES were deprecated. Please remove this configuration.")

    MQTT.availability_topic = f"{SS_TOPIC}/{OPT.sunsynk_id}/availability"

    setup_driver()

    if OPT.debug < 2:
        logging.basicConfig(
            format="%(asctime)s %(levelname)-7s %(message)s",
            level=logging.INFO,
            force=True,
        )

    # Add test sensors
    for sen in TEST_SENSORS:
        ALL_SENSORS[sen.id] = sen

    setup_sensors()


TEST_SENSORS = (
    MathSensor(
        (175, 167, 166), "Essential abs power", WATT, factors=(1, 1, -1), absolute=True
    ),
    # https://powerforum.co.za/topic/8646-my-sunsynk-8kw-data-collection-setup/?do=findComment&comment=147591
    MathSensor(
        (175, 169, 166), "Essential l2 power", WATT, factors=(1, 1, -1), absolute=True
    ),
)


def setup_sensors() -> None:
    """Setup the sensors."""
    sens: Dict[str, Filter] = {}
    sens_dependants: Dict[str, List[Sensor]] = defaultdict(list)
    startup_sens = {SERIAL.id, RATED_POWER.id}

    msg: Dict[str, List[str]] = defaultdict(list)

    for sensor_def in OPT.sensors:
        name, _, fstr = sensor_def.partition(":")
        name = slug(name)
        if name in sens:
            _LOGGER.warning("Sensor %s only allowed once", name)
            continue

        sen = ALL_SENSORS.get(name)
        if not isinstance(sen, Sensor):
            log_bold(f"Unknown sensor in config: {sensor_def}")
            continue
        if sen.id in DEPRECATED:
            log_bold(f"Sensor deprecated: {sen.id} -> {DEPRECATED[sen.id].id}")
        if not fstr:
            fstr = suggested_filter(sen)
            msg[f"*{fstr}"].append(name)  # type: ignore
        else:
            msg[fstr].append(name)  # type: ignore

        filt = getfilter(fstr, sensor=sen)
        SENSORS.append(filt)
        sens[sen.id] = filt

        if isinstance(sen, (NumberRWSensor, TimeRWSensor)):
            for dep in sen.dependencies:
                sens_dependants[dep.id].append(sen)

    for sen_id, deps in sens_dependants.items():
        if sen_id not in ALL_SENSORS:
            _LOGGER.fatal("Invalid sensor as dependency - %s", sen_id)
        sen = ALL_SENSORS[sen_id]

        if sen_id not in sens and sen != RATED_POWER:  # Rated power does not change
            fstr = suggested_filter(sen)
            msg[f"*{fstr}"].append(name)  # type: ignore
            filt = getfilter(fstr, sensor=sen)
            SENSORS.append(filt)
            HIDDEN_SENSOR_IDS.add(sen_id)
            sens[sen.id] = filt
            _LOGGER.info("Added hidden sensor %s as other sensors depend on it", sen_id)

        startup_sens.add(sen_id)
        sen.on_change = lambda sen=sen, deps=deps: enqueue_hass_discovery_info_update(
            sen, list(sens[d.id] for d in deps)
        )

    # Add any sensor dependencies to STARTUP_SENSORS
    STARTUP_SENSORS.clear()
    STARTUP_SENSORS.extend(ALL_SENSORS[n] for n in startup_sens)
    for nme, val in msg.items():
        _LOGGER.info("Filter %s used for %s", nme, ", ".join(sorted(val)))


def log_bold(msg: str) -> None:
    """Log a message."""
    _LOGGER.info("#" * 60)
    _LOGGER.info(f"{msg:^60}".rstrip())
    _LOGGER.info("#" * 60)


READ_ERRORS = 0


async def read_sensors(
    sensors: Sequence[Sensor], msg: str = "", retry_single: bool = False
) -> bool:
    """Read from the Modbus interface."""
    global READ_ERRORS  # pylint:disable=global-statement
    try:
        try:
            await asyncio.wait_for(SUNSYNK.read_sensors(sensors), OPT.timeout)
            READ_ERRORS = 0
            return True
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout reading: %s", msg)
        # except KeyError:
        #     _LOGGER.error("Read error%s: Timeout", msg)
    except Exception as err:  # pylint:disable=broad-except
        _LOGGER.error("Read Error%s: %s", msg, err)
        READ_ERRORS += 1
        if READ_ERRORS > 3:
            raise IOError(f"Multiple Modbus read errors: {err}") from err

    if retry_single:
        _LOGGER.info("Retrying individual sensors: %s", [s.name for s in SENSORS])
        for sen in sensors:
            await asyncio.sleep(0.02)
            await read_sensors([sen], msg=sen.name, retry_single=False)

    return False


TERM = (
    "This Add-On will terminate in 30 seconds, "
    "use the Supervisor Watchdog to restart automatically."
)


async def main(loop: AbstractEventLoop) -> None:  # noqa
    """Main async loop."""
    # pylint: disable=too-many-statements
    loop.set_debug(OPT.debug > 0)

    try:
        await SUNSYNK.connect()
    except ConnectionError:
        log_bold(f"Could not connect to {SUNSYNK.port}")
        _LOGGER.critical(TERM)
        await asyncio.sleep(30)
        return

    _LOGGER.info(
        "Reading startup sensors %s", ", ".join([s.id for s in STARTUP_SENSORS])
    )

    if not await read_sensors(STARTUP_SENSORS):
        log_bold(
            "No response on the Modbus interface, try checking the "
            "wiring to the Inverter, the USB-to-RS485 converter, etc"
        )
        _LOGGER.critical(TERM)
        await asyncio.sleep(30)
        return

    log_bold(f"Inverter serial number '{SERIAL.value}'")

    if OPT.sunsynk_id != SERIAL.value and not OPT.sunsynk_id.startswith("_"):
        log_bold("SUNSYNK_ID should be set to the serial number of your Inverter!")
        return

    powr = float(5000)
    try:
        powr = float(RATED_POWER.value)  # type:ignore pylint: disable=no-member
    except (ValueError, TypeError):
        pass

    await hass_discover_sensors(str(SERIAL.value), powr)

    # Read all & publish immediately
    await asyncio.sleep(0.01)
    await read_sensors([f.sensor for f in SENSORS], retry_single=True)
    await publish_sensors(SENSORS, force=True)

    async def write_sensors() -> None:
        """Flush any pending sensor writes"""

        while SENSOR_WRITE_QUEUE:
            _, (filt, value) = SENSOR_WRITE_QUEUE.popitem()
            sensor: RWSensor = filt.sensor
            old_reg_value = sensor.reg_value
            if not sensor.update_reg_value(value):
                continue
            await SUNSYNK.write_sensor(  # pylint: disable=no-value-for-parameter
                sensor, msg=f"[old {old_reg_value}]"
            )
            await read_sensors([sensor], msg=sensor.name)
            await publish_sensors([filt], force=True)

    async def poll_sensors() -> None:
        """Poll sensors."""
        fsensors = []
        # 1. collect sensors to read
        RROBIN.tick()
        for fil in SENSORS:
            if fil.should_update():
                fsensors.append(fil)
        if fsensors:
            # 2. read
            if await read_sensors([f.sensor for f in fsensors]):
                # 3. decode & publish
                await publish_sensors(fsensors)

    while True:
        await write_sensors()

        polltask = asyncio.create_task(poll_sensors())
        await asyncio.sleep(1)
        try:
            await polltask
        except asyncio.TimeoutError as exc:
            _LOGGER.error("TimeOut %s", exc)
            continue
        except AttributeError:
            # The read failed. Exit and let the watchdog restart
            return
        await hass_update_discovery_info()


if __name__ == "__main__":
    startup()
    LOOP = asyncio.get_event_loop()
    LOOP.run_until_complete(main(LOOP))
    LOOP.close()
