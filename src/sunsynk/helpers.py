"""Helper functions."""

import logging
import math
import struct
from typing import Any

_LOGGER = logging.getLogger(__name__)

ValType = float | int | str | bool | None
RegType = tuple[int, ...]
"""Register addresses or values."""
NumType = float | int


def pack_value(value: int, bits: int = 16, signed: bool = True) -> RegType:
    """Pack a value into register format.

    Args:
        value: The value to pack
        bits: Number of bits (16 or 32)
        signed: Whether the value should be treated as signed

    Returns:
        For 16-bit: single register value
        For 32-bit: tuple of (low, high) register values
    """
    if bits == 16:
        fmt = "h" if signed else "H"
        return struct.unpack("H", struct.pack(fmt, value))
    if bits == 32:
        fmt = "i" if signed else "I"
        return struct.unpack("2H", struct.pack(fmt, value))
    raise ValueError(f"Unsupported number of bits: {bits}")


def unpack_value(regs: RegType, signed: bool = True) -> int:
    """Unpack register value(s) into an integer.

    Args:
        regs: Register values (1 or 2 registers)
        signed: Whether to treat as signed value

    Returns:
        Unpacked integer value
    """
    if len(regs) == 1:
        fmt = "h" if signed else "H"
        return struct.unpack(fmt, struct.pack("H", regs[0]))[0]
    if len(regs) == 2:
        fmt = "i" if signed else "I"
        return struct.unpack(fmt, struct.pack("2H", regs[0], regs[1]))[0]
    raise ValueError(f"Unsupported number of registers: {len(regs)}")


def ensure_tuple(val: Any) -> tuple[int, ...]:
    """Return a tuple."""
    if isinstance(val, tuple):
        return val  # type: ignore
    if isinstance(val, int):
        return (val,)
    return tuple(val)  # type: ignore


def int_round(val: NumType) -> NumType:
    """Round if float."""
    if not isinstance(val, float):
        return val
    val = round(val, 2)
    if math.modf(val)[0] == 0:
        return int(val)
    return val


def as_num(val: ValType) -> float | int:
    """Convert to float."""
    if isinstance(val, (float, int)):
        return val
    if val is None:
        return 0
    try:
        return int(val)
    except ValueError:
        pass
    try:
        return float(val)
    except ValueError as err:
        _LOGGER.error(str(err))
    return 0


def slug(name: str) -> str:
    """Create a slug."""
    return name.lower().replace(" ", "_").replace("-", "_")


def hex_str(regs: RegType, address: RegType | None = None) -> str:
    """Convert register values to hex strings."""
    res = (f"0x{r:04x}" for r in regs)
    if address:
        res = (f"{k}={v}" for k, v in zip(address, res, strict=True))
    return f"{{{' '.join(res)}}}"


def patch_bitmask(value: int, patch: int, bitmask: int) -> int:
    """Combine bitmask values."""
    return (patch & bitmask) + (value & (0xFFFF - bitmask))


class SSTime:
    """Deals with inverter time format conversion complexities."""

    minutes: int = 0

    def __init__(
        self,
        *,
        minutes: int | None = None,
        register: int | None = None,
        string: str | None = None,
    ) -> None:
        """Init the time. All mutually exclusive."""
        if minutes is not None:
            assert register is None
            assert string is None
            self.minutes = minutes
        elif register is not None:
            assert string is None
            self.reg_value = register
        elif string is not None:
            self.str_value = string

    @property
    def reg_value(self) -> int:
        """Get the register value."""
        hours, minutes = divmod(self.minutes, 60)
        return hours * 100 + minutes

    @reg_value.setter
    def reg_value(self, reg_value: int) -> None:
        """Convert from a register value."""
        hours, minutes = divmod(reg_value, 100)
        self.minutes = hours * 60 + minutes

    @property
    def str_value(self) -> str:
        """Get the value in hh:mm format."""
        hours, minutes = divmod(self.minutes, 60)
        return f"{hours}:{minutes:02}"

    @str_value.setter
    def str_value(self, value: str) -> None:
        """Parse a string in hh:mm format."""
        try:
            (hours, _, minutes) = value.partition(":")
            self.minutes = int(hours) * 60 + int(minutes)
        except ValueError:
            _LOGGER.warning("Invalid time string: %s (expected hh:mm)", value)
