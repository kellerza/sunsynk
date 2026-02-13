"""Addon options."""

import logging

import attrs
from mqtt_entity.options import MQTTOptions

from sunsynk.helpers import slug

from .timer_schedule import Schedule

_LOG = logging.getLogger(__name__)


@attrs.define()
class InverterOptions:
    """Options for an inverter."""

    port: str = ""
    driver: str = ""
    """Optional driver override."""
    modbus_id: int = 0
    ha_prefix: str = ""
    serial_nr: str = ""
    dongle_serial_number: int = 0


@attrs.define()
class Options(MQTTOptions):
    """HASS Addon Options."""

    number_entity_mode: str = "auto"
    prog_time_interval: int = 15
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
        """Load options from dict."""
        super().load_dict(value, log_lvl, log_msg)

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
