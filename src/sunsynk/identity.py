"""Inverter identity from holding registers 0-7 (modbus_connection Component)."""

from __future__ import annotations

from typing import Final

from modbus_connection.model import Component, NumberField, integer, string

# Register 0 → (SENSOR_DEFINITIONS profile, label). Unknown codes → single-phase.
DEVICE_TYPES: Final[dict[int, tuple[str, str]]] = {
    0x002: ("single-phase", "String Inverter"),
    0x003: ("single-phase", "Single-phase hybrid"),
    0x004: ("single-phase", "Micro-inverter"),
    0x005: ("three-phase", "Low-voltage three-phase hybrid"),
    0x006: ("three-phase-hv", "High-voltage three-phase hybrid"),
    0x103: ("single-phase", "Single-phase hybrid"),
    0x200: ("single-phase-16kw", "Single-phase LV hybrid (3x MTTP)"),
    0x500: ("three-phase", "Low-voltage three-phase hybrid 10kW"),
    0x601: ("three-phase-hv", "High-voltage three-phase hybrid 6-15kW"),
    0x602: ("three-phase-hv", "High-voltage three-phase hybrid 20-50kW"),
}


def _device_type_label(raw: int) -> str:
    if hit := DEVICE_TYPES.get(raw):
        return hit[1]
    return f"Unknown ({hex(raw)})"


def _protocol_version(raw: int) -> str:
    return f"{raw >> 8}.{raw & 0xFF}"


class Identity(Component):
    """Device type, protocol, and serial — shared by all Deye/Sunsynk families."""

    device_type_code: int = integer(0, signed=False)  # type: ignore[assignment]
    device_type: str = NumberField(0, signed=False, convert=_device_type_label)  # type: ignore[assignment]
    protocol: str = NumberField(2, signed=False, convert=_protocol_version)  # type: ignore[assignment]
    serial: str = string(3, length=5)  # type: ignore[assignment]

    def __str__(self) -> str:
        """Return a string representation of the identity."""
        return (
            f"Identity: device_type={self.device_type} ({hex(self.device_type_code)}) "
            f"protocol={self.protocol} serial=****{str(self.serial)[-5:]}"
        )


def suggested_sensor_definitions(device_type_code: int) -> str:
    """Return the SENSOR_DEFINITIONS profile for ``device_type_code`` (default single-phase)."""
    if hit := DEVICE_TYPES.get(device_type_code):
        return hit[0]
    return "single-phase"
