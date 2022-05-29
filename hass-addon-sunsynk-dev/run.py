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
from typing import Dict, List, Sequence

import yaml
from filter import RROBIN, Filter, getfilter, suggested_filter
from mqtt import MQTT, Device, Entity, SensorEntity
from options import OPT, SS_TOPIC
from profiles import profile_add_entities, profile_poll

from sunsynk.definitions import ALL_SENSORS, DEPRECATED
from sunsynk.sunsynk import Sensor, Sunsynk

_LOGGER = logging.getLogger(__name__)


SENSORS: List[Filter] = []


SUNSYNK: Sunsynk = None  # type: ignore


async def publish_sensors(sensors: List[Filter], *, force: bool = False) -> None:
    """Publish sensors."""
    for fsen in sensors:
        res = fsen.sensor.value
        if not force:
            res = fsen.update(res)
            if res is None:
                continue
        if isinstance(res, float):
            if modf(res)[0] == 0:
                res = int(res)
            else:
                res = f"{res:.2f}".rstrip("0")

        await MQTT.connect(OPT)
        await MQTT.publish(
            topic=f"{SS_TOPIC}/{OPT.sunsynk_id}/{fsen.sensor.id}", payload=str(res)
        )


async def hass_discover_sensors(serial: str) -> None:
    """Discover all sensors."""
    ents: List[Entity] = []
    dev = Device(
        identifiers=[OPT.sunsynk_id],
        name=f"Sunsynk Inverter {serial}",
        model=f"Inverter {serial}",
        manufacturer="Sunsynk",
    )

    for filt in SENSORS:
        sensor = filt.sensor
        ents.append(
            SensorEntity(
                name=f"{OPT.sensor_prefix} {sensor.name}".strip(),
                state_topic=f"{SS_TOPIC}/{OPT.sunsynk_id}/{sensor.id}",
                unit_of_measurement=sensor.unit,
                unique_id=f"{OPT.sunsynk_id}_{sensor.id}",
                device=dev,
            )
        )

    profile_add_entities(entities=ents, device=dev)

    await MQTT.connect(OPT)
    await MQTT.publish_discovery_info(entities=ents)


SERIAL = ALL_SENSORS["serial"]


def setup_driver() -> None:
    """Setup the correct driver."""
    # pylint: disable=import-outside-toplevel
    global SUNSYNK  # pylint: disable=global-statement
    if OPT.driver == "pymodbus":
        from sunsynk.pysunsynk import pySunsynk

        SUNSYNK = pySunsynk()
    elif OPT.driver == "umodbus":
        from sunsynk.usunsynk import uSunsynk

        SUNSYNK = uSunsynk()
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

    MQTT.availability_topic = f"{SS_TOPIC}/{OPT.sunsynk_id}/availability"

    setup_driver()

    if OPT.debug < 2:
        logging.basicConfig(
            format="%(asctime)s %(levelname)-7s %(message)s",
            level=logging.INFO,
            force=True,
        )

    sens = {}

    msg: Dict[str, List[str]] = defaultdict(list)

    for sensor_def in OPT.sensors:
        name, _, fstr = sensor_def.partition(":")
        if name in sens:
            _LOGGER.warning("Sensor %s only allowed once", name)
            continue
        sens[name] = True

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

        SENSORS.append(getfilter(fstr, sensor=sen))

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
            raise Exception(f"Multiple Modbus read errors: {err}") from err

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
    loop.set_debug(OPT.debug > 0)

    try:
        await SUNSYNK.connect()
    except ConnectionError:
        log_bold(f"Could not connect to {SUNSYNK.port}")
        _LOGGER.critical(TERM)
        await asyncio.sleep(30)
        return

    if not await read_sensors([SERIAL]):
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

    await hass_discover_sensors(str(SERIAL.value))

    # Read all & publish immediately
    await asyncio.sleep(0.01)
    await read_sensors([f.sensor for f in SENSORS], retry_single=True)
    await publish_sensors(SENSORS, force=True)

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
        if OPT.profiles:
            await profile_poll(SUNSYNK)


if __name__ == "__main__":
    startup()
    LOOP = asyncio.get_event_loop()
    LOOP.run_until_complete(main(LOOP))
    LOOP.close()
