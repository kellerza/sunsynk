"""Timer class to run callbacks every x seconds."""
import asyncio
import logging
import time
from collections import defaultdict
from math import modf
from typing import Any, Awaitable, Callable, Optional

import attrs

from sunsynk.helpers import slug

_LOGGER = logging.getLogger(__name__)


@attrs.define(slots=True)
class Callback:
    """A callback."""

    # pylint: disable=too-few-public-methods
    name: str = attrs.field(converter=slug)
    every: int = attrs.field()
    """Run every <every> seconds."""
    callback: Callable[[int], Awaitable[None]] | Callable[[int], None] = attrs.field()

    task: Optional[asyncio.Task] = attrs.field(default=None, init=False)
    next_run: int = attrs.field(default=0, init=False)
    coroutinecb = attrs.field(init=False)
    """Next run in seconds."""

    def __attrs_post_init__(self) -> None:
        self.coroutinecb = asyncio.iscoroutinefunction(self.callback)

    async def wrap_callback(self, *args: Any) -> None:
        """Catch unhandled exceptions."""
        try:
            # _LOGGER.warning("Running %s", self.name)
            cb = self.callback(*args)
            if cb is not None:
                await cb
            # _LOGGER.warning("Done %s", self.name)
        except Exception as exc:  # pylint: disable=broad-except
            _LOGGER.error("Unhandled exception in %s: %s", self.name, exc)


async def run_callbacks(callbacks: list[Callback]) -> None:
    """Run the timer."""
    while callbacks:
        frac, _ = modf(time.time())
        await asyncio.sleep(1.1 - frac)  # Try to run at 50ms past the second
        now = int(time.time())
        for cb in callbacks:
            if cb.next_run > 0:
                nrdelta = now - cb.next_run
                if nrdelta > 0:
                    _LOGGER.debug(
                        "Callback %s was missed by %d seconds", cb.name, nrdelta
                    )
            elif now % cb.every != 0:
                continue

            if not cb.coroutinecb:
                cb.callback(now)
                continue

            # schedule a new run, if the previous is done
            if cb.task and not cb.task.done():
                SLIPS[cb.name] += 1
                # _LOGGER.warning("Callback %s still running (%d)", cb.name, now % 60)
                continue

            cb.next_run = now + cb.every
            cb.task = asyncio.create_task(cb.wrap_callback(now))
            EXECS[cb.name] += 1


SLIPS: dict[str, int] = defaultdict(int)
EXECS: dict[str, int] = defaultdict(int)


def print_stats(_: int) -> None:
    """Print callback stats."""
    if sum(SLIPS.values()) < EXECS["slip"]:
        return
    EXECS["slip"] = int(sum(SLIPS.values()) * 1.5)

    smis = sorted(SLIPS.items(), key=lambda x: x[1], reverse=True)
    mis = ", ".join(f"{n} {c}s delay over {EXECS[n]} runs" for n, c in smis if c > 0)
    _LOGGER.warning("Callback stats: %s", mis)


CALLBACKS: list[Callback] = [
    Callback(name="print_stats", every=10, callback=print_stats),
]
