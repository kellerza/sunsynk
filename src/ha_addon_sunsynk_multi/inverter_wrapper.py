"""Inverter wrapper for shared connections."""

import logging
from collections.abc import Iterable, Sequence

import attrs

from sunsynk.rwsensors import RWSensor
from sunsynk.sensors import Sensor
from sunsynk.state import InverterState
from sunsynk.sunsynk import Sunsynk, ValType

from .connector_manager import ConnectorManager

_LOG = logging.getLogger(__name__)

# Global connector manager instance (set by driver.init_driver)
CONNECTOR_MANAGER: ConnectorManager | None = None


@attrs.define(slots=True, kw_only=True)
class InverterWrapper(Sunsynk):
    """Wrapper for inverter using shared connector."""

    connector: Sunsynk = attrs.field()
    """Shared connector instance."""

    connector_name: str = attrs.field()
    """Name of the connector (for lock access)."""

    server_id: int = attrs.field()
    """Modbus server ID for this inverter."""

    def __attrs_post_init__(self) -> None:
        """Initialize wrapper."""
        # Copy connector attributes
        self.port = self.connector.port
        self.timeout = self.connector.timeout
        self.read_sensors_batch_size = self.connector.read_sensors_batch_size
        self.allow_gap = self.connector.allow_gap
        # Create separate state instance for this inverter
        self.state = InverterState()
        self.timeouts = 0

    async def connect(self) -> None:
        """Connect using shared connector."""
        await self.connector.connect()

    async def write_register(self, *, address: int, value: int) -> bool:
        """Write to a register using shared connector."""
        if CONNECTOR_MANAGER is None:
            raise RuntimeError("ConnectorManager not initialized")
        lock = CONNECTOR_MANAGER.get_lock(self.connector_name)
        async with lock:
            # Store original server_id and temporarily override
            original_server_id = self.connector.server_id
            self.connector.server_id = self.server_id
            try:
                return await self.connector.write_register(address=address, value=value)
            finally:
                self.connector.server_id = original_server_id

    async def read_holding_registers(self, start: int, length: int) -> Sequence[int]:
        """Read holding registers using shared connector."""
        if CONNECTOR_MANAGER is None:
            raise RuntimeError("ConnectorManager not initialized")
        lock = CONNECTOR_MANAGER.get_lock(self.connector_name)
        async with lock:
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
        """Write sensor value using shared connector, updating this inverter's state."""
        if CONNECTOR_MANAGER is None:
            raise RuntimeError("ConnectorManager not initialized")
        lock = CONNECTOR_MANAGER.get_lock(self.connector_name)
        async with lock:
            # Store original server_id and state, temporarily override
            original_server_id = self.connector.server_id
            original_state = self.connector.state
            self.connector.server_id = self.server_id
            # Temporarily replace connector's state with our own so updates go to this inverter
            self.connector.state = self.state
            try:
                await self.connector.write_sensor(sensor, value, msg=msg)
            finally:
                self.connector.server_id = original_server_id
                self.connector.state = original_state

    async def read_sensors(self, sensors: Iterable[Sensor]) -> None:
        """Read sensors using shared connector, updating this inverter's state."""
        if CONNECTOR_MANAGER is None:
            raise RuntimeError("ConnectorManager not initialized")
        lock = CONNECTOR_MANAGER.get_lock(self.connector_name)
        async with lock:
            # Store original server_id and state, temporarily override
            original_server_id = self.connector.server_id
            original_state = self.connector.state
            self.connector.server_id = self.server_id
            # Temporarily replace connector's state with our own so updates go to this inverter
            self.connector.state = self.state
            try:
                await self.connector.read_sensors(sensors)
                # Also sync timeouts
                self.timeouts = self.connector.timeouts
            finally:
                self.connector.server_id = original_server_id
                self.connector.state = original_state
