"""Addon options."""

import logging

import attrs
from mqtt_entity.options import MQTTOptions

from .timer_schedule import Schedule

_LOG = logging.getLogger(__name__)


@attrs.define()
class InverterOptions:
    """Options for an inverter."""

    port: str = ""
    modbus_id: int = 0
    ha_prefix: str = ""
    serial_nr: str = ""
    dongle_serial_number: int = 0

    def __attrs_post_init__(self) -> None:
        """Do some checks."""
        self.ha_prefix = self.ha_prefix.lower().strip()
        if self.dongle_serial_number:
            if self.port:
                _LOG.warning("%s: No port expected when you specify a serial number.")
            return
        if self.port == "":
            _LOG.warning(
                "%s: Using port from debug_device: %s", self.serial_nr, OPT.debug_device
            )
            self.port = OPT.debug_device
        ddev = self.port == ""
        if ddev:
            _LOG.warning("Empty port, will use the debug device")
        if ddev or self.port.lower().startswith(("serial:", "/dev")):
            _LOG.warning("Use mbusd instead of connecting directly to a serial port")


@attrs.define()
class Options(MQTTOptions):
    """HASS Addon Options."""

    number_entity_mode: str = "auto"
    prog_time_interval: int = 15
    inverters: list[InverterOptions] = attrs.field(factory=list)
    sensor_definitions: str = "single-phase"
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
