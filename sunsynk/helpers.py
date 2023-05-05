"""Helper functions."""
import logging
import math
import re
import sys
from typing import Any, Optional, Tuple, Union

_LOGGER = logging.getLogger(__name__)

ValType = Union[float, int, str, None]
RegType = tuple[int, ...]
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
    return val if val <= 0x7FFF else val - 0xFFFF


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
        (hours, _, minutes) = value.partition(":")
        self.minutes = int(hours) * 60 + int(minutes)


def patch_bitmask(value: int, patch: int, bitmask: int) -> int:
    """Combine bitmask values."""
    return (patch & bitmask) + (value & (0xFFFF - bitmask))


# Kept outside simple_eval() just for performance
_RE_SIMPLE_EVAL = re.compile(rb"d([\x00-\xFF]+)S\x00")


def _simple_eval(expr: str) -> Union[float, int]:
    """Simple eval function allowing only constant results."""
    # pylint: disable=raise-missing-from
    try:
        cde = compile(expr, "userinput", "eval")
    except SyntaxError:
        raise ValueError("Malformed expression")
    mch = _RE_SIMPLE_EVAL.fullmatch(cde.co_code)
    if not mch:
        raise ValueError(f"Not a simple algebraic expression: {cde.co_code!r}")
    try:
        if mch:
            return cde.co_consts[int.from_bytes(mch.group(1), sys.byteorder)]
        return cde.co_consts[int.from_bytes(cde.co_code, sys.byteorder)]
    except IndexError:
        raise ValueError(
            "Not a simple algebraic expression, result needs to be constant"
        )


def simple_eval(expr: str, allow: Optional[list[str]] = None) -> Union[float, int]:
    """Evaluate a simple algebraic expression."""
    # pylint: disable=raise-missing-from
    exp2 = expr
    for alw in allow or ["abs", "pow"]:
        exp2 = exp2.replace(alw, "")
    # ensure it is a fairly simple expression
    try:
        _simple_eval(exp2)
    except ValueError as err:
        raise ValueError(f"{err}: {expr}") from err

    try:
        return eval(expr)  # pylint: disable=eval-used
    except SyntaxError:
        raise ValueError(f"Malformed expression: {expr}")
