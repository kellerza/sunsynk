"""Addon options."""

import logging

import attrs
import cattrs
from mqtt_entity.options import CONVERTER, MQTTOptions, transform_error

from sunsynk.helpers import slug

from .timer_schedule import Schedule

_LOG = logging.getLogger(__name__)


def _convert_connectors(data: list) -> "list[ConnectorOptions]":
    """Convert list of dicts to list of ConnectorOptions."""
    if not isinstance(data, list):
        raise ValueError(f"Expected list, got {type(data)}")
    return [cattrs.structure(item, ConnectorOptions) for item in data]


def _convert_inverters(data: list) -> "list[InverterOptions]":
    """Convert list of dicts to list of InverterOptions."""
    if not isinstance(data, list):
        raise ValueError(f"Expected list, got {type(data)}")
    return [cattrs.structure(item, InverterOptions) for item in data]


def _convert_schedules(data: list) -> "list[Schedule]":
    """Convert list of dicts to list of Schedule."""
    if not isinstance(data, list):
        raise ValueError(f"Expected list, got {type(data)}")
    return [cattrs.structure(item, Schedule) for item in data]


@attrs.define()
class ConnectorOptions:
    """Options for a connector."""

    name: str
    type: str  # tcp, serial, solarman
    host: str = ""
    port: int = 502
    driver: str = "pymodbus"
    timeout: int = 10
    dongle_serial: int = 0
    baudrate: int = 9600

    def __attrs_post_init__(self) -> None:
        """Validate connector configuration."""
        if self.type not in ("tcp", "serial", "solarman"):
            raise ValueError(f"Invalid connector type: {self.type}")
        if self.driver not in ("pymodbus", "umodbus", "solarman"):
            raise ValueError(f"Invalid driver: {self.driver}")
        if self.type == "solarman" and not self.dongle_serial:
            raise ValueError("Solarman connector requires dongle_serial")


@attrs.define()
class InverterOptions:
    """Options for an inverter."""

    connector: str = ""  # Reference to connector name
    port: str = ""  # Legacy: direct port (backwards compatibility)
    modbus_id: int = 0
    ha_prefix: str = ""
    serial_nr: str = ""
    dongle_serial_number: int = 0

    def __attrs_post_init__(self) -> None:
        """Do some checks."""
        self.ha_prefix = self.ha_prefix.lower().strip()

        # Validate connector vs port usage
        if self.connector and self.port:
            _LOG.warning(
                "%s: Both connector and port specified. Using connector: %s",
                self.serial_nr,
                self.connector,
            )
        # Legacy port handling
        if not self.connector:
            if self.dongle_serial_number:
                if self.port:
                    _LOG.warning(
                        "%s: No port expected when you specify a serial number."
                    )
                return
            if self.port == "":
                _LOG.warning(
                    "%s: Using port from debug_device: %s",
                    self.serial_nr,
                    OPT.debug_device,
                )
                self.port = OPT.debug_device
            ddev = self.port == ""
            if ddev:
                _LOG.warning("Empty port, will use the debug device")
            if ddev or self.port.lower().startswith(("serial:", "/dev")):
                _LOG.warning(
                    "Use mbusd instead of connecting directly to a serial port"
                )

@attrs.define()
class Options(MQTTOptions):
    """HASS Addon Options."""

    number_entity_mode: str = "auto"
    prog_time_interval: int = 15
    connectors: list[ConnectorOptions] = attrs.field(factory=list)
    inverters: list[InverterOptions] = attrs.field(factory=list)
    sensor_definitions: str = "single-phase"
    sensor_overrides: list[str] | None = None
    overrides: dict[str, int | float] | None = None
    sensors: list[str] = attrs.field(factory=list)
    sensors_first_inverter: list[str] = attrs.field(factory=list)
    read_allow_gap: int = 2
    read_sensors_batch_size: int = 20
    schedules: list[Schedule] = attrs.field(factory=list)
    timeout: int = 10
    debug: int = 0
    driver: str = "pymodbus"
    manufacturer: str = "Sunsynk"
    debug_device: str = ""

    async def init_addon(self) -> None:
        """Init Add-On."""
        await super().init_addon()

        if self.driver == "umodbus":
            _LOG.warning("Try *pymodbus* if your encounter any issues with *umodbus*")

        for inv in self.inverters:
            inv.ha_prefix = slug(inv.ha_prefix.strip())

            if inv.dongle_serial_number:
                if inv.port:
                    _LOG.warning(
                        "%s: No port expected when you specify a serial number."
                    )
                continue

            if not inv.port or inv.port.lower().startswith(("serial:", "/dev")):
                _LOG.warning(
                    "Use mbusd instead of connecting directly to a serial port"
                )

            if not inv.port:
                _LOG.warning(
                    "%s: Using port from debug_device: %s",
                    inv.serial_nr,
                    self.debug_device,
                )
                inv.port = self.debug_device

        # Check all ha_prefixes are unique
        ha_prefs = [i.ha_prefix for i in self.inverters]
        if "" in ha_prefs or len(set(ha_prefs)) != len(ha_prefs):
            raise ValueError(
                f"Inverters need a unique HA_PREFIX: {', '.join(ha_prefs)}"
            )

    def load_dict(
        self, value: dict, log_lvl: int = logging.DEBUG, log_msg: str = ""
    ) -> None:
        """Load configuration with custom handling for complex types."""
        _LOG.log(log_lvl, "%s: %s", log_msg or "Loading config", value)

        # Create a copy to avoid modifying the original
        config = value.copy()

        # Handle connectors conversion
        if "connectors" in config:
            config["connectors"] = _convert_connectors(config["connectors"])

        # Handle inverters conversion
        if "inverters" in config:
            config["inverters"] = _convert_inverters(config["inverters"])

        # Handle schedules conversion
        if "schedules" in config:
            config["schedules"] = _convert_schedules(config["schedules"])

        # Use cattrs to structure the configuration, but exclude already-converted fields
        try:
            # Create a copy without the complex types for cattrs processing
            simple_config = {
                k: v
                for k, v in config.items()
                if k not in ("connectors", "inverters", "schedules")
            }
            val = CONVERTER.structure(simple_config, self.__class__)
        except Exception as exc:
            msg = "Error loading config: " + "\n".join(transform_error(exc))
            _LOG.error(msg)
            raise ValueError(msg) from None

        # Set attributes from the structured object
        for key in config:
            if key in ("connectors", "inverters", "schedules"):
                # Use our pre-converted values
                setattr(self, key.lower(), config[key])
            else:
                # Use cattrs-converted values
                setattr(self, key.lower(), getattr(val, key.lower()))

        # Handle sensor overrides
        if isinstance(self.sensor_overrides, list):
            self.overrides = {}
            errs = {}
            for item in self.sensor_overrides:
                key, _, val = str(item).partition("=")
                try:
                    self.overrides[key.strip()] = float(val) if "." in val else int(val)
                except ValueError:
                    errs[key] = val
            if errs:
                _LOG.warning("Invalid sensor overrides found: %s", errs)


OPT = Options()


async def init_options() -> None:
    """Load the options & setup the logger."""
    await OPT.init_addon()

    # check ha_prefix is unique
    all_prefix = set()
    for inv in OPT.inverters:
        if inv.ha_prefix in all_prefix:
            raise ValueError("HA_PREFIX should be unique")
        all_prefix.add(inv.ha_prefix)

    # check connector names are unique
    connector_names = set()
    for conn in OPT.connectors:
        if conn.name in connector_names:
            raise ValueError(f"Connector name '{conn.name}' should be unique")
        connector_names.add(conn.name)

    # validate inverter connector references
    for inv in OPT.inverters:
        if inv.connector and inv.connector not in connector_names:
            raise ValueError(
                f"Inverter '{inv.serial_nr}' references unknown connector "
                f"'{inv.connector}'"
            )
