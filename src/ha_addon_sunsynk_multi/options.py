"""Addon options."""

import logging
from dataclasses import dataclass, field
from urllib.parse import urlparse

from mqtt_entity.options import CONVERTER, MQTTOptions
from whenever import Time

from sunsynk.helpers import slug
from sunsynk.sensors import LOG_TRACE

from .timer_schedule import Schedule

_LOG = logging.getLogger(__name__)


def is_solarman_port(port: str) -> bool:
    """Check if the port selects the Solarman dongle transport."""
    return urlparse(port).scheme == "solarman"


def _normalize_legacy_port(port: str) -> str:
    """Strip legacy umodbus ``serial://`` prefix."""
    parsed = urlparse(port)
    if parsed.scheme == "serial" and parsed.path:
        return parsed.path
    return port


def as_solarman_port(port: str) -> str:
    """Rewrite a host URL (or bare host) to ``solarman://host:port``."""
    if is_solarman_port(port):
        return port
    url = urlparse(port)
    if url.hostname:
        return f"solarman://{url.hostname}:{url.port or 8899}"
    if port and "://" not in port and not port.startswith("/"):
        host, _, p = port.partition(":")
        return f"solarman://{host}:{p or 8899}"
    raise ValueError(
        f"Cannot use Solarman with PORT {port!r}; expected solarman://host:8899"
    )


@dataclass
class InverterOptions:
    """Options for an inverter."""

    port: str = ""
    driver: str = ""
    """Obsolete; kept so legacy configs still load. Prefer ``solarman://`` PORT."""
    modbus_id: int = 0
    ha_prefix: str = ""
    serial_nr: str = ""
    dongle_serial_number: int = 0


@dataclass
class Options(MQTTOptions):
    """HASS Addon Options."""

    number_entity_mode: str = "auto"
    prog_time_interval: int = 15
    inverters: list[InverterOptions] = field(default_factory=list)
    sensor_definitions: str = "single-phase"
    sensor_overrides: list[str] | None = None
    overrides: dict[str, int | float] | None = None
    sensors: list[str] = field(default_factory=list)
    sensors_first_inverter: list[str] = field(default_factory=list)
    read_allow_gap: int = 2
    read_sensors_batch_size: int = 20
    schedules: list[Schedule] = field(default_factory=list)
    timeout: int = 10

    stale_inverter_after_seconds: int = 60
    """Grace window (seconds) after each successful read: if failures continue past this deadline, enter stale quiet."""
    stale_inverter_skip_seconds: int = 600
    """Quiet period (seconds) with no normal polling before a serial-only probe and possible recovery."""

    debug: int = 0
    driver: str = ""
    """Obsolete; kept so legacy configs still load. Prefer ``solarman://`` PORT."""
    manufacturer: str = "Sunsynk"
    debug_device: str = ""
    mute_logs: list[Time] = field(default_factory=list)

    async def init_addon(self) -> None:
        """Init Add-On."""
        await super().init_addon()
        logging.addLevelName(LOG_TRACE, "TRACE")

        global_solarman = self.driver == "solarman"
        if self.driver:
            _LOG.warning(
                "DRIVER is obsolete and ignored; use PORT schemes "
                "(tcp://, serial-tcp://, udp://, /dev/..., or solarman://). "
                "Got DRIVER=%r",
                self.driver,
            )
        self.driver = ""

        for inv in self.inverters:
            inv.ha_prefix = slug(inv.ha_prefix.strip())

            inv_solarman = inv.driver == "solarman"
            if inv.driver:
                _LOG.warning(
                    "%s: per-inverter DRIVER is obsolete and ignored "
                    "(got %r); use PORT: solarman://... for Solarman",
                    inv.ha_prefix or inv.serial_nr,
                    inv.driver,
                )
            inv.driver = ""

            if inv.port:
                normalized = _normalize_legacy_port(inv.port)
                if normalized != inv.port:
                    _LOG.warning(
                        "%s: Normalized legacy port %r to %r",
                        inv.ha_prefix or inv.serial_nr,
                        inv.port,
                        normalized,
                    )
                    inv.port = normalized

            want_solarman = (
                is_solarman_port(inv.port)
                or inv_solarman
                or global_solarman
                or bool(inv.dongle_serial_number)
            )
            if want_solarman and inv.port and not is_solarman_port(inv.port):
                try:
                    rewritten = as_solarman_port(inv.port)
                except ValueError as err:
                    _LOG.warning("%s: %s", inv.ha_prefix or inv.serial_nr, err)
                else:
                    _LOG.warning(
                        "%s: Remapped PORT %r to %r "
                        "(use solarman:// and DONGLE_SERIAL_NUMBER; DRIVER is obsolete)",
                        inv.ha_prefix or inv.serial_nr,
                        inv.port,
                        rewritten,
                    )
                    inv.port = rewritten

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
                key, _, val = item.partition("=")
                try:
                    self.overrides[key.strip()] = float(val) if "." in val else int(val)
                except ValueError:
                    errs[key] = val
            if errs:
                _LOG.warning("Invalid sensor overrides found: %s", errs)


@CONVERTER.register_structure_hook  # type:ignore[call-overload]
def time_structure_hook(value: str, _: type | None = None) -> Time:
    """Convert a string to a Time."""
    try:
        vals = [int(v) for v in value.split(":")]
        if len(vals) != 2:
            raise ValueError()
        return Time(hour=vals[0], minute=vals[1])
    except ValueError as exc:
        _LOG.error("Invalid time: %s (expected hh:mm)", value)
        raise ValueError(f"Invalid time: {value} (expected hh:mm)") from exc


OPT = Options()
