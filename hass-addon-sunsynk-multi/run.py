#!/usr/bin/env python3
"""Run the addon."""
import asyncio
import logging
import sys
import traceback
from asyncio.events import AbstractEventLoop
from collections import defaultdict
from typing import Iterable, OrderedDict

from filter import RROBIN, Filter, getfilter, suggested_filter
from mqtt import MQTT, Device
from options import OPT, init_options
from state import SENSOR_PREFIX, SENSOR_WRITE_QUEUE, SS, SS_TOPIC, State, TimeoutState

from sunsynk.definitions import (
    ALL_SENSORS,
    DEPRECATED,
    RATED_POWER,
    SERIAL,
    WATT,
    MathSensor,
)
from sunsynk.helpers import ValType, slug
from sunsynk.rwsensors import RWSensor
from sunsynk.sunsynk import Sensor, Sunsynk

_LOGGER = logging.getLogger(":")


HASS_DISCOVERY_INFO_UPDATE_QUEUE: set[Sensor] = set()
STARTUP_SENSORS: set[Sensor] = {RATED_POWER, SERIAL}
STATES: dict[str, State] = {}


async def publish_sensors(states: Iterable[State], *, force: bool = False) -> None:
    """Publish state to HASS."""
    for state in states:
        if state.hidden or state.sensor is None:
            continue
        val = SS[0].state[state.sensor]
        if isinstance(state.filter, Filter):
            val = state.filter.update(val)
            if force and val is None:
                val = SS[0].state[state.sensor]
        await state.publish(val)

    # statistics
    await STATES["to"].publish(SS[0].timeouts)


async def hass_discover_sensors(
    *, mqtt_id: str, serial: str, rated_power: float
) -> None:
    """Discover all sensors."""
    dev = Device(
        identifiers=[mqtt_id],
        name=f"{OPT.manufacturer} Inverter {serial}",
        model=f"{int(rated_power/1000)}kW Inverter {serial}",
        manufacturer=OPT.manufacturer,
    )
    if mqtt_id != serial:
        dev.name += f" {mqtt_id}"
    SENSOR_PREFIX[mqtt_id] = OPT.sensor_prefix
    ents = [s.create_entity(dev) for s in STATES.values() if not s.hidden]
    await MQTT.connect(OPT)
    await MQTT.publish_discovery_info(entities=ents)


async def hass_update_discovery_info() -> None:
    """Update discovery info for existing sensors"""
    states = [STATES[n.id] for n in HASS_DISCOVERY_INFO_UPDATE_QUEUE]
    HASS_DISCOVERY_INFO_UPDATE_QUEUE.clear()
    ents = [s.create_entity(s.entity) for s in states if not s.hidden]
    await MQTT.connect(OPT)
    await MQTT.publish_discovery_info(entities=ents, remove_entities=False)


# def enqueue_hass_discovery_info_update(sen: Sensor, deps: list[Sensor]) -> None:
#     """Add a sensor's dependants to the HASS discovery info update queue."""
#     ids = sorted(s.id for s in deps)
#     _LOGGER.debug(
#         "%s changed: Enqueue discovery info updates for %s", sen.name, ", ".join(ids)
#     )
#     HASS_DISCOVERY_INFO_UPDATE_QUEUE.update(ids)


SENSOR_DEPENDANTS: dict[Sensor, list[Sensor]] = defaultdict(list)
"""Sensor dependencies. Changes in the sensor used as key, affects sensors in the list."""


def sensor_updates(sen: Sensor, _new: ValType, _old: ValType) -> None:
    """React to sensor updates."""
    if sen not in SENSOR_DEPENDANTS:
        return
    deps = SENSOR_DEPENDANTS[sen]
    _LOGGER.debug(
        "%s changed: Enqueue discovery info updates for %s",
        sen.name,
        ", ".join(s.id for s in deps),
    )
    HASS_DISCOVERY_INFO_UPDATE_QUEUE.update(deps)


def setup_driver() -> None:
    """Setup the correct driver."""
    # pylint: disable=import-outside-toplevel

    factory = Sunsynk
    port_prefix = ""

    if OPT.driver == "pymodbus":
        from sunsynk.pysunsynk import pySunsynk

        factory = pySunsynk  # type:ignore
    elif OPT.driver == "umodbus":
        from sunsynk.usunsynk import uSunsynk

        factory = uSunsynk  # type:ignore
        port_prefix = "serial://"
    else:
        _LOGGER.critical("Invalid DRIVER: %s. Expected umodbus, pymodbus", OPT.driver)
        sys.exit(-1)

    for opt in OPT.inverters:
        kwargs: OrderedDict = {  # type:ignore
            "port": opt.port if opt.port else port_prefix + opt.device,
            "server_id": opt.modbus_id,
            "timeout": OPT.timeout,
            "read_sensors_batch_size": OPT.read_sensors_batch_size,
        }
        suns = factory(**kwargs)
        suns.state.onchange = sensor_updates

        SS.append(suns)

    STATES["to"] = TimeoutState(entity=None, filter=None, sensor=None)


def setup_sensors() -> None:
    """Setup the sensors."""
    # pylint: disable=too-many-branches
    sens: dict[str, Filter] = {}
    msg: dict[str, list[str]] = defaultdict(list)

    # Add test sensors
    ALL_SENSORS.update((s.id, s) for s in TEST_SENSORS)

    for ssen in STARTUP_SENSORS:
        SS[0].state.track(ssen)

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
            log_bold(f"Sensor {sen.id} deprecated, rather use {DEPRECATED[sen.id].id}")
        if not fstr:
            fstr = suggested_filter(sen)
            msg[f"*{fstr}"].append(name)  # type: ignore
        else:
            msg[fstr].append(name)  # type: ignore

        filt = getfilter(fstr, sensor=sen)
        STATES[sen.id] = State(
            sensor=sen, filter=filt, retain=isinstance(sen, RWSensor)
        )
        SS[0].state.track(sen)
        sens[sen.id] = filt

        if not isinstance(sen, RWSensor):
            continue
        for dep in sen.dependencies:
            if dep in (RATED_POWER, SERIAL):  # These sensors never change
                continue
            if sen not in SENSOR_DEPENDANTS[dep]:
                SENSOR_DEPENDANTS[dep].append(sen)
            STARTUP_SENSORS.add(dep)
            SS[0].state.track(dep)
            if dep.id in STATES:
                continue
            fstr = suggested_filter(dep)
            msg[f"*{fstr}"].append(dep.id)  # type: ignore
            filt = getfilter(fstr, sensor=dep)
            STATES[dep.id] = State(sensor=dep, hidden=True, filter=filt)
            _LOGGER.info("Added hidden sensor %s as other sensors depend on it", dep.id)

    for nme, val in msg.items():
        _LOGGER.info("Filter %s used for %s", nme, ", ".join(sorted(val)))


def log_bold(msg: str) -> None:
    """Log a message."""
    _LOGGER.info("#" * 60)
    _LOGGER.info(f"{msg:^60}".rstrip())
    _LOGGER.info("#" * 60)


READ_ERRORS = 0


async def read_sensors(
    inv: Sunsynk, sensors: Iterable[Sensor], msg: str = "", retry_single: bool = False
) -> bool:
    """Read from the Modbus interface."""
    global READ_ERRORS  # pylint:disable=global-statement
    try:
        await inv.read_sensors(sensors)
        READ_ERRORS = 0
        return True
    except asyncio.TimeoutError:
        pass
    except Exception as err:  # pylint:disable=broad-except
        _LOGGER.error("Read Error%s: %s", msg, err)
        if OPT.debug > 2:
            traceback.print_exc()
        READ_ERRORS += 1
        await asyncio.sleep(0.02 * READ_ERRORS)
        if READ_ERRORS > 3:
            raise Exception(f"Multiple Modbus read errors: {err}") from err

    if retry_single:
        _LOGGER.info("Retrying individual sensors: %s", [s.id for s in sensors])
        for sen in sensors:
            await asyncio.sleep(0.02)
            await read_sensors(inv, [sen], msg=sen.name, retry_single=False)

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
        await SS[0].connect()
    except ConnectionError:
        log_bold(f"Could not connect to {SS[0].port}")
        _LOGGER.critical(TERM)
        await asyncio.sleep(30)
        return

    _LOGGER.info(
        "Reading startup sensors %s", ", ".join([s.id for s in STARTUP_SENSORS])
    )

    if not await read_sensors(SS[0], STARTUP_SENSORS):
        log_bold(
            f"No response on the Modbus interface {SS[0].port}, try checking the "
            "wiring to the Inverter, the USB-to-RS485 converter, etc"
        )
        _LOGGER.critical(TERM)
        await asyncio.sleep(30)
        return

    log_bold(f"Inverter serial number '{SS[0].state[SERIAL]}'")

    if OPT.inverters[0].get_serial() != SS[0].state[SERIAL]:
        log_bold("SS[0].ID should be set to the serial number of your Inverter!")
        return

    powr = float(5000)
    try:
        powr = float(SS[0].state[RATED_POWER])  # type:ignore
    except (ValueError, TypeError):
        pass

    # Start MQTT
    mqtt_id = OPT.inverters[0].get_mqttid()
    MQTT.availability_topic = f"{SS_TOPIC}/{mqtt_id}/availability"
    await hass_discover_sensors(
        mqtt_id=mqtt_id,
        serial=str(SS[0].state[SERIAL]),
        rated_power=powr,
    )

    # Read all & publish immediately
    await asyncio.sleep(0.01)
    await read_sensors(
        SS[0], [s.sensor for s in STATES.values() if s.sensor], retry_single=True
    )
    await publish_sensors(STATES.values(), force=True)

    async def write_sensors() -> None:
        """Flush any pending sensor writes"""

        while SENSOR_WRITE_QUEUE:
            sensor, value = SENSOR_WRITE_QUEUE.popitem()
            if not isinstance(sensor, RWSensor):
                continue
            await SS[0].write_sensor(sensor, value)  # , msg=f"[old {old_reg_value}]")
            await read_sensors(SS[0], [sensor], msg=sensor.name)
            await publish_sensors([STATES[sensor.id]], force=True)

    async def poll_sensors() -> None:
        """Poll sensors."""
        states: list[State] = []
        # 1. collect sensors to read
        RROBIN.tick()
        for state in STATES.values():
            if state.filter and state.filter.should_update():
                states.append(state)
        if states:
            # 2. read
            if await read_sensors(SS[0], [s.sensor for s in states if s.sensor]):
                # 3. decode & publish
                await publish_sensors(states)

    while True:
        await write_sensors()

        polltask = asyncio.create_task(poll_sensors())
        await asyncio.sleep(1)
        try:
            await polltask
        except asyncio.TimeoutError as exc:
            _LOGGER.error("TimeOut %s", exc)
            continue
        except AttributeError as exc:
            _LOGGER.error("Attr err %s", exc)
            # The read failed. Exit and let the watchdog restart
            return
        if HASS_DISCOVERY_INFO_UPDATE_QUEUE:
            await hass_update_discovery_info()


TEST_SENSORS = (
    MathSensor(
        (175, 167, 166), "Essential abs power", WATT, factors=(1, 1, -1), absolute=True
    ),
    # https://powerforum.co.za/topic/8646-my-sunsynk-8kw-data-collection-setup/?do=findComment&comment=147591
    MathSensor(
        (175, 169, 166), "Essential l2 power", WATT, factors=(1, 1, -1), absolute=True
    ),
)


if __name__ == "__main__":
    init_options()
    setup_driver()
    setup_sensors()
    LOOP = asyncio.get_event_loop_policy().get_event_loop()
    LOOP.run_until_complete(main(LOOP))
    LOOP.close()
