"""Inverter wrapper for shared connections."""

import logging
from collections.abc import Iterable, Sequence

import attrs

from sunsynk.rwsensors import RWSensor
from sunsynk.sensors import Sensor
from sunsynk.sunsynk import Sunsynk, ValType

_LOG = logging.getLogger(__name__)


@attrs.define(slots=True, kw_only=True)
class InverterWrapper(Sunsynk):
    """Wrapper for inverter using shared connector."""

    connector: Sunsynk = attrs.field()
    """Shared connector instance."""

    server_id: int = attrs.field()
    """Modbus server ID for this inverter."""

    def __attrs_post_init__(self) -> None:
        """Initialize wrapper."""
        # Copy connector attributes
        self.port = self.connector.port
        self.timeout = self.connector.timeout
        self.read_sensors_batch_size = self.connector.read_sensors_batch_size
        self.allow_gap = self.connector.allow_gap
        self.state = self.connector.state
        self.timeouts = self.connector.timeouts

    async def connect(self) -> None:
        """Connect using shared connector."""
        await self.connector.connect()

    async def write_register(self, *, address: int, value: int) -> bool:
        """Write to a register using shared connector."""
        # Store original server_id and temporarily override
        original_server_id = self.connector.server_id
        self.connector.server_id = self.server_id
        try:
            return await self.connector.write_register(address=address, value=value)
        finally:
            self.connector.server_id = original_server_id

    async def read_holding_registers(self, start: int, length: int) -> Sequence[int]:
        """Read holding registers using shared connector."""
        # Store original server_id and temporarily override
        original_server_id = self.connector.server_id
        self.connector.server_id = self.server_id
        try:
            return await self.connector.read_holding_registers(
                start=start, length=length
            )
        finally:
            self.connector.server_id = original_server_id

    async def write_sensor(
        self, sensor: RWSensor, value: ValType, *, msg: str = ""
    ) -> None:
        """Write sensor value using shared connector."""
        await self.connector.write_sensor(sensor, value, msg=msg)

    async def read_sensors(self, sensors: Iterable[Sensor]) -> None:
        """Read sensors using shared connector."""
        await self.connector.read_sensors(sensors)
