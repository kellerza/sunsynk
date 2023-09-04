"""Helper functions."""
import logging
import math
from typing import Any, Optional, Tuple, Union

_LOGGER = logging.getLogger(__name__)

ValType = Union[float, int, str, bool, None]
RegType = tuple[int, ...]
"""Register addresses or values."""
NumType = Union[float, int]


def ensure_tuple(val: Any) -> Tuple[int]:
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


def as_num(val: ValType) -> Union[float, int]:
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


def signed(val: Union[int, float]) -> Union[int, float]:
    """Convert 16-bit value to signed int."""
    return val if val <= 0x7FFF else val - 0x10000


def slug(name: str) -> str:
    """Create a slug."""
    return name.lower().replace(" ", "_").replace("-", "_")


class SSTime:
    """Deals with inverter time format conversion complexities."""

    minutes: int = 0

    def __init__(
        self,
        *,
        minutes: Optional[int] = None,
        register: Optional[int] = None,
        string: Optional[str] = None,
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


def patch_bitmask(value: int, patch: int, bitmask: int) -> int:
    """Combine bitmask values."""
    return (patch & bitmask) + (value & (0xFFFF - bitmask))


def hex_str(regs: RegType, address: Optional[RegType] = None) -> str:
    """Convert register values to hex strings."""
    res = (f"0x{r:04x}" for r in regs)
    if address:
        res = (f"{k}={v}" for k, v in zip(address, res, strict=True))
    return f"{{{' '.join(res)}}}"
