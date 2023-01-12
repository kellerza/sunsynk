"""Helper functions."""
from math import modf
from typing import Any, Tuple, Union


def ensure_tuple(val: Any) -> Tuple[int]:
    """Return a tuple."""
    if isinstance(val, tuple):
        return val  # type: ignore
    if isinstance(val, int):
        return (val,)
    return tuple(val)  # type: ignore


def round(val: Union[int, float, str]) -> Union[int, float, str]:
    """Round if float."""
    if not isinstance(val, float):
        return val
    val = round(val, 2)
    if modf(val)[0] == 0:
        return int(val)
    return val


def signed(val: Union[int, float]) -> Union[int, float]:
    """Convert 16-bit value to signed int."""
    return val if val <= 0x7FFF else val - 0xFFFF


def slug(name: str) -> str:
    """Create a slug."""
    return name.lower().replace(" ", "_").replace("-", "_")


class SSTime:
    """Deals with inverter time format conversion complexities."""

    minutes: int

    def __init__(self, minutes: int = 0) -> None:
        """Init the time with minutes."""
        self.minutes = minutes

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
        (hours, _, minutes) = value.partition(":")
        self.minutes = int(hours) * 60 + int(minutes)
