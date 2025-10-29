"""Main."""

import asyncio
import logging
import sys
from pathlib import Path

from sunsynk import VERSION

from .a_inverter import STATE
from .a_sensor import MQTT, SS_TOPIC
from .driver import callback_discovery_info, init_driver
from .errors import print_errors
from .options import OPT, init_options
from .sensor_callback import build_callback_schedule
from .sensor_options import SOPT
from .timer_callback import (
    CALLBACKS,
    AsyncCallback,
    SyncCallback,
    run_callbacks,
)
from .timer_schedule import init_schedules

_LOG = logging.getLogger(__name__)


async def main_loop() -> int:
    """Entry point."""
    # Print version added during build & pyproject version
    vfile = Path(__file__) / "../../../../VERSION"
    ver = vfile.read_text().strip() if vfile.exists() else ""
    _LOG.info("sunsynk library version: %s (%s)", VERSION, ver)

    await init_options()
    try:
        init_driver(OPT)
    except (TypeError, ValueError) as err:
        _LOG.critical(str(err))
        return 1
    init_schedules(OPT.schedules)
    SOPT.init_sensors()
    for ist in STATE:
        ist.init_sensors()

    asyncio.get_event_loop().set_debug(OPT.debug > 0)

    # MQTT client availability will use the first inverter's prefix
    MQTT.availability_topic = f"{SS_TOPIC}/availability_{OPT.inverters[0].ha_prefix}"

    CALLBACKS.append(
        AsyncCallback(name="discovery_info", every=5, callback=callback_discovery_info)
    )

    for ist in STATE:
        try:
            await ist.connect()
            await ist.hass_discover_sensors()
            ist.cb = build_callback_schedule(ist)
            CALLBACKS.append(ist.cb)
        except (ConnectionError, ValueError) as err:
            ist.log_bold(str(err))
            _LOG.critical(
                "This Add-On will terminate in 30 seconds, use the Supervisor Watchdog to restart automatically."
            )
            return 2

    CALLBACKS.append(
        SyncCallback(name="log_errors", every=5 * 60, callback=print_errors)
    )

    await run_callbacks(CALLBACKS)
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main_loop()))
