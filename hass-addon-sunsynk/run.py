#!/usr/bin/env python3
"""Run the addon."""
import asyncio
import logging

import sensors

_LOGGER = logging.getLogger(__name__)


async def main() -> None:
    """Main entry point."""
    logging.basicConfig(level=logging.DEBUG)

    await sensors.startup()
    LOOP = asyncio.get_event_loop()

    if sensors.OPTIONS.debug > 0:
        LOOP.set_debug(True)
    else:
        logging.basicConfig(level=logging.INFO, force=True)

    while True:
        try:
            await asyncio.sleep(sensors.OPTIONS.poll_interval)
        finally:
            pass


if __name__ == "__main__":
    # if os.name == "nt":
    #     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
