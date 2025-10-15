"""Connector management for shared connections."""

import logging

import attrs

from sunsynk.pysunsynk import PySunsynk
from sunsynk.solarmansunsynk import SolarmanSunsynk
from sunsynk.sunsynk import Sunsynk
from sunsynk.usunsynk import USunsynk

from .options import OPT, ConnectorOptions

_LOG = logging.getLogger(__name__)


@attrs.define(slots=True)
class ConnectorManager:
    """Manages shared connections for multiple inverters."""

    connectors: dict[str, Sunsynk] = attrs.field(factory=dict, init=False)
    """Active connector instances."""

    def get_connector(self, name: str) -> Sunsynk:
        """Get or create a connector instance."""
        if name not in self.connectors:
            self.connectors[name] = self._create_connector(name)
        return self.connectors[name]

    def _create_connector(self, name: str) -> Sunsynk:
        """Create a new connector instance."""
        # Find connector config
        conn_config = None
        for config in OPT.connectors:
            if config.name == name:
                conn_config = config
                break

        if not conn_config:
            raise ValueError(f"Connector '{name}' not found in configuration")

        _LOG.info("Creating connector: %s (%s)", name, conn_config.type)

        # Create appropriate driver instance
        factory = self._get_driver_factory(conn_config.driver)
        port = self._build_port_string(conn_config)

        suns = factory(
            port=port,
            server_id=1,  # Will be overridden by inverter-specific server_id
            timeout=conn_config.timeout,
            read_sensors_batch_size=OPT.read_sensors_batch_size,
            allow_gap=OPT.read_allow_gap,
        )

        # Set dongle serial for Solarman
        if hasattr(suns, "dongle_serial_number") and conn_config.dongle_serial:
            suns.dongle_serial_number = conn_config.dongle_serial

        return suns

    def _get_driver_factory(self, driver: str) -> type[Sunsynk]:
        """Get the appropriate driver factory."""
        if driver == "pymodbus":
            return PySunsynk
        elif driver == "umodbus":
            return USunsynk
        elif driver == "solarman":
            return SolarmanSunsynk
        else:
            raise ValueError(f"Invalid driver: {driver}")

    def _build_port_string(self, config: ConnectorOptions) -> str:
        """Build port string from connector config."""
        if config.type == "tcp":
            return f"tcp://{config.host}:{config.port}"
        elif config.type == "serial":
            if config.driver == "umodbus":
                return f"serial://{config.host}"
            return config.host
        elif config.type == "solarman":
            return f"tcp://{config.host}:{config.port}"
        else:
            raise ValueError(f"Unsupported connector type: {config.type}")

    async def close_all(self) -> None:
        """Close all connector connections."""
        for name, connector in self.connectors.items():
            try:
                if hasattr(connector, "disconnect"):
                    await connector.disconnect()
                _LOG.info("Closed connector: %s", name)
            except Exception as err:
                _LOG.error("Error closing connector %s: %s", name, err)
        self.connectors.clear()
