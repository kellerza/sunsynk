#!/usr/bin/env python3
"""Run the addon."""
import asyncio
import logging
import sys
import traceback
from asyncio.events import AbstractEventLoop
from typing import Iterable

from filter import RROBIN, Filter, getfilter
from mqtt_entity import Device
from options import OPT, init_options
from sensors import SOPT
from state import (
    MQTT,
    SENSOR_PREFIX,
    SENSOR_WRITE_QUEUE,
    SS_TOPIC,
    STATE,
    AllStates,
    State,
    TimeoutState,
)

from sunsynk.helpers import ValType
from sunsynk.rwsensors import RWSensor
from sunsynk.sunsynk import Sensor, Sunsynk

_LOGGER = logging.getLogger(":")


HASS_DISCOVERY_INFO_UPDATE_QUEUE: set[Sensor] = set()


async def publish_sensors(
    *, ast: AllStates, states: Iterable[State], force: bool = False
) -> None:
    """Publish state to HASS."""
    for state in states:
        if state.hidden or state.sensor is None:
            continue
        val = ast.inv.state[state.sensor]
        if isinstance(state.filter, Filter):
            val = state.filter.update(val)
            if force and val is None:
                val = ast.inv.state[state.sensor]
        await state.publish(val)

    # statistics
    await ast.state["to"].publish(ast.inv.timeouts)


async def hass_discover_sensors(*, ast: AllStates, rated_power: float) -> bool:
    """Discover all sensors."""
    # Ensure the read serial is the same as the configured one
    serial_nr = ast.opt.serial_nr
    # if serial_nr.replace("*", "") != (sser := str(ast.inv.state[SOPT.defs.serial])):
    #     _LOGGER.error(
    #         "Serial number from device (%s) does not match configuration (%s). SKIP",
    #         sser,
    #         serial_nr,
    #     )
    #     return False

    dev = Device(
        identifiers=[serial_nr],
        name=f"{OPT.manufacturer} Inverter {serial_nr}",
        model=f"{int(rated_power/1000)}kW Inverter {serial_nr}",
        manufacturer=OPT.manufacturer,
    )
    SENSOR_PREFIX[serial_nr] = ast.opt.ha_prefix
    ents = [s.create_entity(dev) for s in ast.state.values() if not s.hidden]
    await MQTT.connect(OPT)
    await MQTT.publish_discovery_info(entities=ents)
    return True


async def hass_update_discovery_info() -> None:
    """Update discovery info for existing sensors."""
    for ssi in range(len(STATE)):
        states = [STATE[ssi].state[n.id] for n in HASS_DISCOVERY_INFO_UPDATE_QUEUE]
    HASS_DISCOVERY_INFO_UPDATE_QUEUE.clear()
    ents = [s.create_entity(s.entity) for s in states if not s.hidden]
    await MQTT.connect(OPT)
    await MQTT.publish_discovery_info(entities=ents, remove_entities=False)


def sensor_updates(sen: Sensor, _new: ValType, _old: ValType) -> None:
    """React to sensor updates."""
    if sen not in SOPT.deps:
        return
    deps = SOPT.deps[sen]
    _LOGGER.debug(
        "%s changed: Enqueue discovery info updates for %s",
        sen.name,
        ", ".join(s.id for s in deps),
    )
    HASS_DISCOVERY_INFO_UPDATE_QUEUE.update(deps)


def setup_driver() -> None:
    """Setup the correct driver, inits STATE."""
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
    elif OPT.driver == "solarman":
        from sunsynk.solarmansunsynk import SolarmanSunsynk

        factory = SolarmanSunsynk
        port_prefix = "tcp://"
    else:
        _LOGGER.critical("Invalid DRIVER: %s. Expected umodbus, pymodbus", OPT.driver)
        sys.exit(-1)

    STATE.clear()

    for opt in OPT.inverters:
        kwargs = {
            "port": opt.port if opt.port else port_prefix + OPT.debug_device,
            "server_id": opt.modbus_id,
            "timeout": OPT.timeout,
            "read_sensors_batch_size": OPT.read_sensors_batch_size,
            "serial_nr": opt.serial_nr,
        }
        _LOGGER.debug("%s driver options: %s", OPT.driver, kwargs)
        suns = factory(**kwargs)
        suns.state.onchange = sensor_updates

        STATE.append(AllStates(inv=suns, state={}, opt=opt))


def setup_sensors() -> None:
    """Setup the sensors, extends STATE."""
    SOPT.from_options()

    for istate, ast in enumerate(STATE):
        for sen in SOPT.startup.values():
            ast.inv.state.track(sen)

        # create state entry
        for name, sen in SOPT.sensors.items():
            ast.inv.state.track(sen)

            fil = getfilter(SOPT.filter_str[name], sensor=sen)
            ast.state[sen.id] = State(
                sensor=sen,
                filter=fil,
                retain=isinstance(sen, RWSensor),
                hidden=not SOPT.visible.get(name),
                istate=istate,
            )

        ast.state["to"] = TimeoutState(
            entity=None, filter=None, sensor=None, istate=istate
        )


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
        if OPT.debug > 1:
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


async def connect(inv: Sunsynk) -> bool:
    """Connect."""
    _LOGGER.info("Connecting to %s", inv.port)
    try:
        await inv.connect()
    except ConnectionError as exc:
        raise ConnectionError(f"Could not connect to {inv.port}: {exc}") from exc

    _LOGGER.info("Reading startup sensors %s", ", ".join(list(SOPT.startup)))

    if not await read_sensors(inv, SOPT.startup.values()):
        raise ConnectionError(
            f"No response on the Modbus interface {inv.port}, try checking the "
            "wiring to the Inverter, the USB-to-RS485 converter, etc"
        )

    log_bold(f"Inverter serial number '{inv.state[SOPT.defs.serial]}'")


async def main(loop: AbstractEventLoop) -> None:  # noqa
    """Main async loop."""
    # pylint: disable=too-many-statements
    loop.set_debug(OPT.debug > 0)

    power = []
    for ast in STATE:
        try:
            await connect(ast.inv)
        except ConnectionError as err:
            log_bold(str(err))
            _LOGGER.critical(TERM)
            await asyncio.sleep(30)
            return

        expected_ser = ast.opt.serial_nr.replace("_", "")
        if expected_ser != ast.inv.state[SOPT.defs.serial]:
            log_bold(f"Error. Expected SERIAL_NR={expected_ser}")
            return

        try:
            powr = float(ast.inv.state[SOPT.defs.rated_power])  # type:ignore
            power.append(powr)
        except (ValueError, TypeError):
            power.append(0)

    # Start MQTT - availability will always use first inverter's serial
    MQTT.availability_topic = f"{SS_TOPIC}/{OPT.inverters[0].serial_nr}/availability"
    for ast in STATE:
        await hass_discover_sensors(ast=ast, rated_power=powr)

    # Read all & publish immediately
    for ast in STATE:
        await asyncio.sleep(0.01)
        await read_sensors(
            ast.inv,
            [s.sensor for s in ast.state.values() if s.sensor],
            retry_single=True,
        )
        await publish_sensors(ast=ast, states=ast.state.values(), force=True)

    async def write_sensors() -> None:
        """Flush any pending sensor writes."""
        while SENSOR_WRITE_QUEUE:
            (ssi, sensor), value = SENSOR_WRITE_QUEUE.popitem()
            if not isinstance(sensor, RWSensor):
                continue
            await STATE[ssi].inv.write_sensor(
                sensor, value
            )  # , msg=f"[old {old_reg_value}]")
            await read_sensors(STATE[ssi].inv, [sensor], msg=sensor.name)
            await publish_sensors(
                ast=ast, states=[STATE[ssi].state[sensor.id]], force=True
            )

    async def poll_sensors() -> None:
        """Poll sensors."""
        RROBIN.tick()
        for ast in STATE:
            states: list[State] = []
            # 1. collect sensors to read
            for state in ast.state.values():
                if state.filter and state.filter.should_update():
                    states.append(state)
            if states:
                # 2. read
                if await read_sensors(ast.inv, [s.sensor for s in states if s.sensor]):
                    # 3. decode & publish
                    await publish_sensors(ast=ast, states=states)

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
