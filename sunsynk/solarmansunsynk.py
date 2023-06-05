import attrs
import logging
import asyncio

from sunsynk.sunsynk import Sunsynk
from pysolarmanv5 import PySolarmanV5Async, V5FrameError
from typing import Sequence
from urllib.parse import urlparse


_LOGGER = logging.getLogger(__name__)


retry_attempts = 5

@attrs.define
class SolarmanSunsynk(Sunsynk):  # pylint: disable=invalid-name
    """Sunsynk class using PySolarmanV5."""

    client: PySolarmanV5Async = None

    async def connect(self) -> None:
        """Connect."""
        url = urlparse(f"{self.port}")
        self.client = PySolarmanV5Async(
            address=url.hostname
            ,serial=int(self.serial_nr)
            ,port=url.port
            ,mb_slave_id=self.server_id
            ,auto_reconnect=True
            ,verbose=False
            ,socket_timeout=60)
        await self.client.connect()

    async def write_register(self, *, address: int, value: int) -> bool:
        """Write to a register - Sunsynk supports modbus function 0x10."""
        try:
            #await self.client.connect()
            await self.client.write_holding_register(address=address, value=value)
            return True            
        except asyncio.TimeoutError:
            _LOGGER.error("timeout writing register %s=%s", address, value)
        #finally:
        #    await self.client.disconnect()

        self.timeouts += 1
        return False

    async def read_holding_registers(self, start: int, length: int) -> Sequence[int]:        
        """Read a holding register."""        
        try:
            #await self.client.connect()
            return await self.client.read_holding_registers(start, length)
        except asyncio.TimeoutError:
            raise IOError(f"failed to read register {start}")
        except V5FrameError:
            _LOGGER.error("frame error reading registers starting at: %s", start)
            for attempt in range(retry_attempts):
                try:                    
                    return await self.client.read_holding_registers(start, length)
                    #break
                except Exception as e:                    
                    _LOGGER.error("Caught error: %s", e)
                    await asyncio.sleep(10)
                    continue               
            else:
                raise IOError(f"failed to read register {start}")
        #finally:
        #   await self.client.disconnect()        