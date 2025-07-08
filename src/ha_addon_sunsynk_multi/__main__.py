"""Main."""

import asyncio
import logging

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

_LOGGER = logging.getLogger(__name__)


async def main_loop() -> None:
    """Entry point."""
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
            _LOGGER.critical(
                "This Add-On will terminate in 30 seconds, use the Supervisor Watchdog to restart automatically."
            )
            await asyncio.sleep(30)
            return

    CALLBACKS.append(
        SyncCallback(name="log_errors", every=5 * 60, callback=print_errors)
    )

    await run_callbacks(CALLBACKS)


def main() -> None:
    """Entry point."""
    init_options()
    try:
        _LOGGER.info("sunsynk library version: %s", VERSION)
        init_driver(OPT)
    except (TypeError, ValueError) as err:
        _LOGGER.critical(str(err))
        return
    init_schedules(OPT.schedules)
    SOPT.init_sensors()
    for ist in STATE:
        ist.init_sensors()

    asyncio.run(main_loop())


if __name__ == "__main__":
    main()
