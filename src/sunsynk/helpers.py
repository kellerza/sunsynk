"""Helper functions."""

import logging
import math
import struct
from collections.abc import Iterable
from dataclasses import InitVar, dataclass

_LOG = logging.getLogger(__name__)

type ValType = float | int | str | bool | None
type RegType = tuple[int, ...]
"""Register addresses or values."""
type NumType = float | int


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
        fmt = "<h" if signed else "<H"
        return struct.unpack("<H", struct.pack(fmt, value))
    if bits == 32:
        fmt = "<i" if signed else "<I"
        return struct.unpack("<2H", struct.pack(fmt, value))
    raise ValueError(f"Unsupported number of bits: {bits}")


def unpack_value(regs: RegType, *, signed: bool = True, maybe16: bool = False) -> int:
    """Unpack register value(s) into an integer.

    Args:
        regs: Register values (1 or 2 registers)
        signed: Whether to treat as signed value
        maybe16: If 2 registers, treat as 16-bit if the second register is 0

    Returns:
        Unpacked integer value

    """
    # All inverters are little-endian <
    # h = short, H = unsigned short, i = int, I = unsigned int

    # If we always use maybe16, an incorrect result is expected between
    # the values of 32768 and 65535 (0x8000 and 0xffff), everything else is ok.
    # 32768 error      0x8000 0x0     -32768
    # 65535 error      0xffff 0x0     -1
    try:
        if len(regs) == 1 or (maybe16 and len(regs) == 2 and regs[1] == 0):
            fmt = "<h" if signed else "<H"
            return struct.unpack(fmt, struct.pack("<H", regs[0]))[0]
        if len(regs) == 2:
            fmt = "<i" if signed else "<I"
            return struct.unpack(fmt, struct.pack("<2H", regs[0], regs[1]))[0]
    except struct.error as err:
        _LOG.error(str(err))
        raise
    raise ValueError(f"Unsupported number of registers: {len(regs)}")


def ensure_tuple[T](val: T | tuple[T, ...]) -> tuple[T, ...]:
    """Return a tuple."""
    if isinstance(val, tuple):
        return val
    if val is None:
        return ()
    if isinstance(val, Iterable) and not isinstance(val, str):
        return tuple(val)
    return (val,)  # type: ignore[return-value]


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
    if isinstance(val, float | int):
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
        _LOG.error(str(err))
    return 0


def slug(name: str) -> str:
    """Create a slug."""
    return name.lower().replace(" ", "_").replace("-", "_")


def hex_str(regs: RegType, address: RegType | None = None) -> str:
    """Convert register values to hex strings."""
    res = (f"{r:04x}" for r in regs)
    if address:
        res = (f"{k}=0x{v}" for k, v in zip(address, res, strict=True))
    return f"{{{' '.join(res)}}}"


def patch_bitmask(value: int, patch: int, bitmask: int) -> int:
    """Combine bitmask values."""
    return (patch & bitmask) + (value & (0xFFFF - bitmask))


@dataclass
class SSTime:
    """Deals with inverter time format conversion complexities."""

    minutes: int = 0
    strv: InitVar[str] = ""
    regv: InitVar[int] = 0

    def __post_init__(self, strv: str, regv: int) -> None:
        """Initialize from string or register value."""
        if strv:
            self.str_value = strv
        elif regv:
            self.reg_value = regv

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
        hours = hours % 24
        return f"{hours}:{minutes:02}"

    @str_value.setter
    def str_value(self, value: str) -> None:
        """Parse a string in hh:mm format."""
        try:
            (hours, _, minutes) = value.partition(":")
            self.minutes = int(hours) * 60 + int(minutes)
        except ValueError:
            _LOG.warning("Invalid time string: %s (expected hh:mm)", value)
