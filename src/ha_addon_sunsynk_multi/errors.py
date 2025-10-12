"""Error messages."""

import logging
from collections import defaultdict
from traceback import format_exception

ERRLIST: dict[str, int] = defaultdict(int)
_LOG = logging.getLogger(__name__)


def log_error(msg: str, exc: Exception | None = None) -> None:
    """Print an error message."""
    ERRLIST[msg] += 1
    if ERRLIST[msg] > 1:
        return
    if exc:
        _LOG.error("%s\n%s", msg, "\n".join(format_exception(exc)))
    else:
        _LOG.error(msg)


def print_errors(_: int) -> None:
    """Print errors."""
    if not ERRLIST:
        return
    errs = [(c, m) for m, c in ERRLIST.items() if c > 1]
    errs.sort(reverse=True)
    for count, msg in errs:
        _LOG.error("(%s in 5 min) %s", count - 1, msg)

    for key in ERRLIST:
        ERRLIST[key] = 1
