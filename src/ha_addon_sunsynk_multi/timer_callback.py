"""Timer class to run callbacks every x seconds."""
import asyncio
import logging
import time
from math import modf
from typing import Awaitable, Callable, Optional

import attrs

from sunsynk.helpers import slug

_LOGGER = logging.getLogger(__name__)


@attrs.define(slots=True)
class Callback:
    """A callback."""

    # pylint: disable=too-few-public-methods, too-many-instance-attributes
    name: str = attrs.field(converter=slug)
    every: int = attrs.field()
    """Run every <every> seconds."""
    callback: Callable[[int], Awaitable[None]] | Callable[[int], None] = attrs.field()

    task: Optional[asyncio.Task] = attrs.field(default=None, init=False)
    next_run: int = attrs.field(default=0, init=False)
    """Next run in seconds."""

    keep_stats: bool = attrs.field(default=False)
    stat_time: list[float] = attrs.field(factory=list)
    """Execution time history."""
    stat_slip: list[int] = attrs.field(factory=list)
    """Seconds that execution slipped."""
    stat_busy: int = attrs.field(default=0)
    """Number of times the callback was still busy."""

    async def wrap_callback(self, cb_call: Awaitable[None]) -> None:
        """Catch unhandled exceptions."""
        try:
            t_0 = time.perf_counter()
            await cb_call
            if self.keep_stats:
                t_1 = time.perf_counter()
                self.stat_time.append(t_1 - t_0)
        except Exception as exc:  # pylint: disable=broad-except
            _LOGGER.error("Exception in %s: %s", self.name, exc)


async def run_callbacks(callbacks: list[Callback]) -> None:
    """Run the timer."""
    while callbacks:
        frac, _ = modf(time.time())
        await asyncio.sleep(1.1 - frac)  # Try to run at 50ms past the second
        now = int(time.time())
        for cb in callbacks:
            should = now % cb.every == 0
            slip_s = now - cb.next_run if cb.next_run > 0 else 0
            if not (should or slip_s):
                continue

            if cb.keep_stats:
                cb.stat_slip.append(slip_s)

            if not asyncio.iscoroutinefunction(cb.callback):
                cb.callback(now)
                cb.next_run = now + cb.every
                continue

            # schedule a new run, if the previous is done
            if cb.task and not cb.task.done():
                cb.stat_busy += 1
                continue

            cb.next_run = now + cb.every
            cb.task = asyncio.create_task(cb.wrap_callback(cb.callback(now)))


CALLBACKS: list[Callback] = []
