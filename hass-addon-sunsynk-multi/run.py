#!/usr/bin/env python3
"""Run the addon."""
import asyncio
import logging
import sys
import traceback
from asyncio.events import AbstractEventLoop
from collections import defaultdict
from typing import Iterable

from filter import RROBIN, Filter, getfilter, suggested_filter
from helpers import import_mysensors
from mqtt_entity import Device
from options import OPT, InverterOptions, init_options
from state import (
    MQTT,
    SENSOR_PREFIX,
    SENSOR_WRITE_QUEUE,
    SS,
    SS_TOPIC,
    State,
    TimeoutState,
)

from sunsynk.definitions import SENSORS as DEFS1
from sunsynk.definitions3ph import SENSORS as DEFS3
from sunsynk.helpers import ValType, slug
from sunsynk.rwsensors import RWSensor
from sunsynk.sensors import SensorDefinitions
from sunsynk.sunsynk import Sensor, Sunsynk

_LOGGER = logging.getLogger(":")
DEFS: SensorDefinitions = SensorDefinitions()


HASS_DISCOVERY_INFO_UPDATE_QUEUE: set[Sensor] = set()
STARTUP_SENSORS: set[Sensor] = set()
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
    *, iopt: InverterOptions, ss: Sunsynk, rated_power: float
) -> bool:
    """Discover all sensors."""
    # Ensure the read serial is the same as the configured one
    if iopt.serial_nr != (sser := str(ss.state[DEFS.serial])):
        _LOGGER.error(
            "Serial number from device (%s) does not match configuration (%s). SKIP",
            sser,
            iopt.serial_nr,
        )
        return False

    dev = Device(
        identifiers=[iopt.mqtt_id],
        name=f"{OPT.manufacturer} Inverter {iopt.serial_nr}",
        model=f"{int(rated_power/1000)}kW Inverter {iopt.serial_nr}",
        manufacturer=OPT.manufacturer,
    )
    if iopt.mqtt_id != iopt.serial_nr:
        dev.name += f" {iopt.mqtt_id}"
    SENSOR_PREFIX[iopt.mqtt_id] = OPT.inverters[0].ha_prefix
    ents = [s.create_entity(dev) for s in STATES.values() if not s.hidden]
    await MQTT.connect(OPT)
    await MQTT.publish_discovery_info(entities=ents)
    return True


async def hass_update_discovery_info() -> None:
    """Update discovery info for existing sensors."""
    states = [STATES[n.id] for n in HASS_DISCOVERY_INFO_UPDATE_QUEUE]
    HASS_DISCOVERY_INFO_UPDATE_QUEUE.clear()
    ents = [s.create_entity(s.entity) for s in states if not s.hidden]
    await MQTT.connect(OPT)
    await MQTT.publish_discovery_info(entities=ents, remove_entities=False)


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

        factory = pySunsynk
    elif OPT.driver == "umodbus":
        from sunsynk.usunsynk import uSunsynk

        factory = uSunsynk
        port_prefix = "serial://"
    else:
        _LOGGER.critical("Invalid DRIVER: %s. Expected umodbus, pymodbus", OPT.driver)
        sys.exit(-1)

    for opt in OPT.inverters:
        kwargs = {
            "port": opt.port if opt.port else port_prefix + OPT.debug_device,
            "server_id": opt.modbus_id,
            "timeout": OPT.timeout,
            "read_sensors_batch_size": OPT.read_sensors_batch_size,
        }
        _LOGGER.debug("%s driver options: %s", OPT.driver, kwargs)
        suns = factory(**kwargs)
        suns.state.onchange = sensor_updates

        SS.append(suns)

    STATES["to"] = TimeoutState(entity=None, filter=None, sensor=None)


def setup_sensors() -> None:
    """Setup the sensors."""
    # pylint: disable=too-many-branches, too-many-statements

    if OPT.sensor_definitions == "three-phase":
        _LOGGER.info("Using three phase sensor definitions.")
        DEFS.all = DEFS3.all
        DEFS.deprecated = DEFS3.deprecated
    else:
        _LOGGER.info("Using Single phase sensor definitions.")
        DEFS.all = DEFS1.all
        DEFS.deprecated = DEFS1.deprecated

    sens: dict[str, Filter] = {}
    msg: dict[str, list[str]] = defaultdict(list)

    # Add custom sensors
    try:
        mysensors = import_mysensors()
    except ImportError:
        log_bold("Unable to import import mysensors.py")
        traceback.print_exc()
    if mysensors:
        DEFS.all.update(mysensors)

    for ssen in (DEFS.rated_power, DEFS.serial):
        STARTUP_SENSORS.add(ssen)
        SS[0].state.track(ssen)

    deprecated = [
        f"Replace {s} with {DEFS.deprecated[s].id}"
        for s in OPT.sensors
        if s in DEFS.deprecated
    ]
    if deprecated:
        _LOGGER.fatal(
            "Your config includes deprecated sensors. Please use the new names: %s",
            "\n".join(deprecated),
        )

    added_hidden = []

    for sensor_def in OPT.sensors:
        name, _, fstr = sensor_def.partition(":")
        name = slug(name)
        if name in sens:
            _LOGGER.warning("Sensor %s only allowed once", name)
            continue

        sen = DEFS.all.get(name)
        if not isinstance(sen, Sensor):
            log_bold(f"Unknown sensor in config: {sensor_def}")
            continue
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
            if dep in (DEFS.rated_power, DEFS.serial):  # These sensors never change
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
            if dep.id not in OPT.sensors:
                added_hidden.append(dep.id)
    if added_hidden:
        _LOGGER.info(
            "Added hidden sensors as other sensors depend on it: %s",
            ", ".join(added_hidden),
        )

    if OPT.debug > 0:
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
        _LOGGER.error("Read Error%s: %s: %s", msg, type(err), err)
        if OPT.debug > 2:
            traceback.print_exc()
        READ_ERRORS += 1
        await asyncio.sleep(0.02 * READ_ERRORS)
        if READ_ERRORS > 3:
            raise IOError(f"Multiple Modbus read errors: {err}") from err

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

    _LOGGER.info("Connecting to %s", SS[0].port)
    try:
        await SS[0].connect()
    except ConnectionError as exc:
        log_bold(f"Could not connect to {SS[0].port}: {exc}")
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

    log_bold(f"Inverter serial number '{SS[0].state[DEFS.serial]}'")

    if OPT.inverters[0].serial_nr != SS[0].state[DEFS.serial]:
        log_bold("SS[0].ID should be set to the serial number of your Inverter!")
        return

    powr = float(5000)
    try:
        powr = float(SS[0].state[DEFS.rated_power])  # type:ignore
    except (ValueError, TypeError):
        pass

    # Start MQTT - availability will always use
    mqtt_id = OPT.inverters[0].serial_nr
    MQTT.availability_topic = f"{SS_TOPIC}/{mqtt_id}/availability"
    for iopt, sus in zip(OPT.inverters, SS):
        await hass_discover_sensors(iopt=iopt, ss=sus, rated_power=powr)

    # Read all & publish immediately
    await asyncio.sleep(0.01)
    await read_sensors(
        SS[0], [s.sensor for s in STATES.values() if s.sensor], retry_single=True
    )
    await publish_sensors(STATES.values(), force=True)

    async def write_sensors() -> None:
        """Flush any pending sensor writes."""
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


if __name__ == "__main__":
    init_options()
    setup_driver()
    setup_sensors()
    LOOP = asyncio.get_event_loop_policy().get_event_loop()
    LOOP.run_until_complete(main(LOOP))
    LOOP.close()
