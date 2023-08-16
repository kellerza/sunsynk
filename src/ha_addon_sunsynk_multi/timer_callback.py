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
    coroutinecb = attrs.field(init=False)
    """Next run in seconds."""

    cbstat_time: Optional[list[float]] = attrs.field(default=None)
    """Execution time history."""
    cbstat_slip: Optional[list[int]] = attrs.field(default=None)
    """Seconds that execution slipped."""
    cbstat_busy: int = attrs.field(default=0)
    """Number of times the callback was still busy."""

    def __attrs_post_init__(self) -> None:
        self.coroutinecb = asyncio.iscoroutinefunction(self.callback)

    async def wrap_callback(self, cb_call: Awaitable[None]) -> None:
        """Catch unhandled exceptions."""
        try:
            t_0 = time.perf_counter()
            await cb_call
            if self.cbstat_time is not None:
                t_1 = time.perf_counter()
                self.cbstat_time.append(t_1 - t_0)
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

            if cb.cbstat_slip:
                cb.cbstat_slip.append(slip_s)

            if not cb.coroutinecb:
                cb.callback(now)
                cb.next_run = now + cb.every
                continue

            # schedule a new run, if the previous is done
            if cb.task and not cb.task.done():
                cb.cbstat_busy += 1
                continue

            cb.next_run = now + cb.every
            cb.task = asyncio.create_task(cb.wrap_callback(cb.callback(now)))


CALLBACKS: list[Callback] = []
