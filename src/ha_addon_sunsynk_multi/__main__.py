"""Main."""
import asyncio
import logging
from asyncio.events import AbstractEventLoop

from ha_addon_sunsynk_multi.a_inverter import STATE
from ha_addon_sunsynk_multi.a_sensor import MQTT, SS_TOPIC
from ha_addon_sunsynk_multi.driver import callback_discovery_info, init_driver
from ha_addon_sunsynk_multi.errors import print_errors
from ha_addon_sunsynk_multi.options import OPT, init_options
from ha_addon_sunsynk_multi.sensor_callback import build_callback_schedule
from ha_addon_sunsynk_multi.sensor_options import SOPT
from ha_addon_sunsynk_multi.timer_callback import (
    CALLBACKS,
    AsyncCallback,
    SyncCallback,
    run_callbacks,
)
from ha_addon_sunsynk_multi.timer_schedule import init_schedules

_LOGGER = logging.getLogger(__name__)


async def main_loop(loop: AbstractEventLoop) -> None:  # noqa
    """Main async loop."""
    loop.set_debug(OPT.debug > 0)

    # MQTT availability will always use first inverter's serial
    MQTT.availability_topic = f"{SS_TOPIC}/{OPT.inverters[0].serial_nr}/availability"

    CALLBACKS.append(
        AsyncCallback(name="discovery_info", every=5, callback=callback_discovery_info)
    )

    for idx, ist in enumerate(STATE):
        try:
            await ist.connect()
            await ist.hass_discover_sensors()
            ist.cb = build_callback_schedule(ist=ist, idx=idx)
            CALLBACKS.append(ist.cb)
        except (ConnectionError, ValueError) as err:
            ist.log_bold(str(err))
            _LOGGER.critical(
                "This Add-On will terminate in 30 seconds, "
                "use the Supervisor Watchdog to restart automatically."
            )
            await asyncio.sleep(30)
            return

    CALLBACKS.append(
        SyncCallback(name="log_errors", every=5 * 60, callback=print_errors)
    )

    await run_callbacks(CALLBACKS)


def main() -> None:
    """Main."""
    init_options()
    init_driver(OPT)
    init_schedules(OPT.schedules)
    SOPT.init_sensors()
    for ist in STATE:
        ist.init_sensors()

    loop = asyncio.get_event_loop_policy().get_event_loop()
    loop.run_until_complete(main_loop(loop))
    loop.close()


if __name__ == "__main__":
    main()
