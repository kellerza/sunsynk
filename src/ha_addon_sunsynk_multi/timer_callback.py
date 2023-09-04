"""Timer class to run callbacks every x seconds."""
import asyncio
import logging
import time
from math import modf
from typing import Awaitable, Callable

import attrs

from ha_addon_sunsynk_multi.errors import log_error
from sunsynk.helpers import slug

_LOGGER = logging.getLogger(__name__)


@attrs.define(slots=True)
class Callback:
    """A callback."""

    # pylint: disable=too-few-public-methods, too-many-instance-attributes
    name: str = attrs.field(converter=slug)
    every: int = attrs.field()
    """Run every <every> seconds."""
    offset: int = attrs.field(default=0)
    """Offset in seconds."""
    next_run: int = attrs.field(default=0, init=False)
    """Next run in seconds."""

    keep_stats: bool = attrs.field(default=False)
    stat_time: list[float] = attrs.field(factory=list)
    """Execution time history."""
    stat_slip: list[int] = attrs.field(factory=list)
    """Seconds that execution slipped."""
    stat_busy: int = attrs.field(default=0)
    """Number of times the callback was still busy."""

    def call(self, now: int) -> None:
        """Call the callback."""
        raise NotImplementedError()

    def __attrs_post_init__(self) -> None:
        """Init."""
        if self.every - self.offset < 1:
            raise ValueError(
                f"every ({self.every}) must be larger than offset ({self.offset})"
            )


@attrs.define(slots=True)
class SyncCallback(Callback):
    """A sync callback."""

    callback: Callable[[int], None] = attrs.field(kw_only=True)

    def call(self, now: int) -> None:
        """Catch unhandled exceptions."""
        self.next_run = now + self.every
        try:
            t_0 = time.perf_counter()
            self.callback(now)
            if self.keep_stats:
                t_1 = time.perf_counter()
                self.stat_time.append(t_1 - t_0)
        except Exception as exc:  # pylint: disable=broad-except
            log_error(f"{exc.__class__.__name__} in {self.name}: {exc}")
            self.next_run = now  # re run!


@attrs.define(slots=True)
class AsyncCallback(Callback):
    """An async callback."""

    task: asyncio.Task = attrs.field(default=None, init=False)
    callback: Callable[[int], Awaitable[None]] = attrs.field(kw_only=True)

    async def wrap_callback(self, cb_call: Awaitable[None]) -> None:
        """Catch unhandled exceptions."""
        try:
            t_0 = time.perf_counter()
            await cb_call
            if self.keep_stats:
                t_1 = time.perf_counter()
                self.stat_time.append(t_1 - t_0)
        except Exception as exc:  # pylint: disable=broad-except
            log_error(f"{exc.__class__.__name__} in {self.name}: {exc}")
            self.next_run = int(time.time())  # re run!

    def call(self, now: int) -> None:
        """Create the task."""
        if self.task and not self.task.done():
            self.stat_busy += 1
            return
        self.next_run = now + self.every
        self.task = asyncio.create_task(self.wrap_callback(self.callback(now)))


async def run_callbacks(callbacks: list[Callback]) -> None:
    """Run the timer."""
    sleep_task = asyncio.create_task(asyncio.sleep(0.5))
    while callbacks:
        await sleep_task
        frac, nowf = modf(time.time())
        sleep_task = asyncio.create_task(asyncio.sleep(1.05 - frac))
        now = int(nowf)
        for cb in callbacks:
            slip_s = now - cb.next_run
            if (now + cb.offset) % cb.every != 0 and slip_s < 0:
                continue
            if cb.keep_stats and cb.next_run > 0:
                cb.stat_slip.append(abs(slip_s))
            cb.call(now)

    await sleep_task


CALLBACKS: list[Callback] = []
