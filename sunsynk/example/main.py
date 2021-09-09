"""Example."""
import asyncio
import logging

import sunsynk.definitions as sens
from sunsynk.sunsynk import Sunsynk

logging.basicConfig()
_LOGGER = logging.getLogger()
_LOGGER.setLevel(logging.DEBUG)


async def main() -> None:
    """Main."""
    # ----------------------------------------------------------------------- #
    # For testing on linux based systems you can use socat to create serial
    # ports
    # ----------------------------------------------------------------------- #
    # socat -d -d PTY,link=/tmp/ptyp0,raw,echo=0,ispeed=9600 PTY,
    # link=/tmp/ttyp0,raw,echo=0,ospeed=9600
    ssk = Sunsynk(port="/tmp/ptyp0")
    ssk.read([sens.grid_frequency])
    _LOGGER.info("%s - %s", sens.grid_frequency.name, sens.grid_frequency.value)


if __name__ == "__main__":
    asyncio.run(main())
