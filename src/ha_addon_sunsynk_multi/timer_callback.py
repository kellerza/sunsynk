"""Timer class to run callbacks every x seconds."""

import asyncio
import logging
import time
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass, field
from math import modf

from sunsynk.helpers import slug

from .errors import log_error

_LOG = logging.getLogger(__name__)


@dataclass(slots=True)
class Callback:
    """A callback."""

    name: str
    every: int = field()
    """Run every <every> seconds."""
    offset: int = 0
    """Offset in seconds."""
    next_run: int = 0
    """Next run in seconds."""

    keep_stats: bool = False
    stat_time: list[float] = field(default_factory=list)
    """Execution time history."""
    stat_slip: list[int] = field(default_factory=list)
    """Seconds that execution slipped."""
    stat_busy: int = 0
    """Number of times the callback was still busy."""

    def call(self, now: int) -> None:
        """Call the callback."""
        raise NotImplementedError

    def __post_init__(self) -> None:
        """Init."""
        self.name = slug(self.name)
        if self.every - self.offset < 1:
            raise ValueError(
                f"every ({self.every}) must be larger than offset ({self.offset})"
            )


@dataclass
class SyncCallback(Callback):
    """A sync callback."""

    callback: Callable[[int], None] = field(kw_only=True)

    def call(self, now: int) -> None:
        """Catch unhandled exceptions."""
        self.next_run = now + self.every
        try:
            t_0 = time.perf_counter()
            self.callback(now)
            if self.keep_stats:
                t_1 = time.perf_counter()
                self.stat_time.append(t_1 - t_0)
        except Exception as exc:
            log_error(f"{exc.__class__.__name__} in callback {self.name}: {exc}\n", exc)
            self.next_run = now  # re run!


@dataclass
class AsyncCallback(Callback):
    """An async callback."""

    task: asyncio.Task = field(default=None, init=False)  # type:ignore[arg-type]
    callback: Callable[[int], Awaitable[None]] = field(kw_only=True)

    async def wrap_callback(self, cb_call: Awaitable[None]) -> None:
        """Catch unhandled exceptions."""
        try:
            t_0 = time.perf_counter()
            await cb_call
            if self.keep_stats:
                t_1 = time.perf_counter()
                self.stat_time.append(t_1 - t_0)
        except Exception as exc:
            log_error(f"{exc.__class__.__name__} in callback {self.name}: {exc}\n", exc)
            self.next_run = int(time.time())  # re run!

    def call(self, now: int) -> None:
        """Create the task."""
        if self.task and not self.task.done():
            self.stat_busy += 1
            return
        self.next_run = now + self.every
        self.task = asyncio.create_task(self.wrap_callback(self.callback(now)))


async def run_callbacks(callbacks: Sequence[Callback]) -> None:
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
