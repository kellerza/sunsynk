"""Timer class to run callbacks every x seconds."""

import asyncio
import logging
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field

from whenever import Time, ZonedDateTime

from sunsynk.helpers import slug

from .errors import log_error

_LOG = logging.getLogger(__name__)


@dataclass(slots=True)
class Callback:
    """A callback."""

    name: str

    next_run: int = 0
    """Next run in seconds."""

    keep_stats: bool = False
    """Whether to keep execution time stats."""
    stat_time: list[float] = field(default_factory=list)
    """Execution time history, if stat_time is a list."""
    stat_busy_count: int = 0
    """Number of times the callback was still executing, and could not be scheduled."""
    stat_error_count: int = 0
    """Number of times the callback raised an error."""

    def call(self, now: int) -> None:
        """Call the callback."""
        raise NotImplementedError

    def __post_init__(self) -> None:
        """Init."""
        self.name = slug(self.name)


@dataclass
class SyncCallback(Callback):
    """A sync callback."""

    every: int = 60
    """Run every <every> seconds."""
    callback: Callable[[int], None] = field(kw_only=True)

    def call(self, now: int) -> None:
        """Catch unhandled exceptions."""
        self.next_run = now + self.every
        try:
            t_0 = time.perf_counter()
            self.callback(now)
            t_1 = time.perf_counter()
            if self.keep_stats:
                self.stat_time.append(t_1 - t_0)
        except Exception as exc:
            log_error(f"{exc.__class__.__name__} in callback {self.name}: {exc}\n", exc)
            self.next_run = now  # re run!
            self.stat_error_count += 1


@dataclass
class ToggleLogCallback(Callback):
    """Toggle the log level to critical for a short time, to suppress expected errors."""

    duration: int = 60
    """Duration to keep the log level at critical, in seconds."""

    times: list[Time] = field(default_factory=list)
    next_runs: list[ZonedDateTime] = field(init=False)
    task: asyncio.Task = field(init=False)

    original_level: int = logging.INFO

    def calc_next_run(self) -> None:
        """Calculate the next run times."""
        now = ZonedDateTime.now_in_system_tz()
        self.next_runs = [
            n if n > now else n.add(days=1)
            for n in (now.replace_time(t) for t in self.times)
        ]
        self.next_runs.sort()
        self.next_run = self.next_run0

    @property
    def next_run0(self) -> int:
        """Return next run seconds of entry 0."""
        return self.next_runs[0].timestamp_millis() // 1000

    def __post_init__(self) -> None:
        """Init."""
        assert len(self.times) > 0
        self.next_runs = [ZonedDateTime.now_in_system_tz()]
        self.task = None  # type:ignore[assignment]
        self.calc_next_run()
        self.original_level = _LOG.level

    async def mute_log(self) -> None:
        """Set log level to critical, and reset after duration."""
        now, _, _ = ZonedDateTime.now_in_system_tz().format_iso().partition("T")
        _LOG.info(
            "[%s] Disabling the log for %s seconds",
            now,
            self.duration,
        )

        loggers = [logging.getLogger(n) for n in logging.root.manager.loggerDict]
        levels: dict[str, int] = {}
        for logr in loggers:
            levels[logr.name] = logr.level
            logr.setLevel(logging.CRITICAL + 1)

        _LOG.error("Log disabled")
        try:
            await asyncio.sleep(self.duration)
        finally:
            for name, level in levels.items():
                logging.getLogger(name).setLevel(level)

    def call(self, now: int) -> None:
        """Toggle the log level."""
        if self.task and not self.task.done():
            self.stat_busy_count += 1
            self.next_run = now + 1
            return
        should_mute = abs(now - self.next_run0) < 10
        if should_mute:
            self.task = asyncio.create_task(self.mute_log())
        self.calc_next_run()


@dataclass
class AsyncCallback(Callback):
    """An async callback."""

    every: int = 0
    """Run every <every> seconds."""
    task: asyncio.Task = field(init=False)
    callback: Callable[[int], Awaitable[None]] = field(kw_only=True)

    def __post_init__(self) -> None:
        """Init."""
        self.task = None  # type:ignore[assignment]

    async def wrap_callback(self, now: int) -> None:
        """Catch unhandled exceptions."""
        try:
            t_0 = time.perf_counter()
            await self.callback(now)
            t_1 = time.perf_counter()
            if self.keep_stats:
                self.stat_time.append(t_1 - t_0)
        except Exception as exc:
            log_error(f"{exc.__class__.__name__} in callback {self.name}: {exc}\n", exc)
            self.next_run = now  # re run!
            self.stat_error_count += 1

    def call(self, now: int) -> None:
        """Create the task."""
        if self.task and not self.task.done():
            self.stat_busy_count += 1
            return
        self.next_run = now + self.every
        self.task = asyncio.create_task(self.wrap_callback(now))


# async def run_callbacks_old(callbacks: Sequence[Callback]) -> None:
#     """Run the timer."""
#     sleep_task = asyncio.create_task(asyncio.sleep(0.5))
#     while callbacks:
#         await sleep_task
#         frac, nowf = modf(time.time())
#         sleep_task = asyncio.create_task(asyncio.sleep(1.05 - frac))
#         now = int(nowf)
#         for cb in callbacks:
#             slip_s = now - cb.next_run
#             if (now + cb.offset) % cb.every != 0 and slip_s < 0:
#                 continue
#             if cb.keep_stats and cb.next_run > 0:
#                 cb.stat_slip.append(abs(slip_s))
#             cb.call(now)

#     await sleep_task


async def run_callbacks(callbacks: list[Callback]) -> None:
    """Run the timer."""
    while True:
        now_s = ZonedDateTime.now_in_system_tz().timestamp_millis() // 1000
        for cb in callbacks:
            if cb.next_run > now_s:
                continue
            cb.call(now_s)

        end_s, ms = divmod(ZonedDateTime.now_in_system_tz().timestamp_millis(), 1000)
        if end_s <= now_s:  # sleep remainder of the second, plus 10ms
            await asyncio.sleep((1010 - ms) / 1000)
        else:
            await asyncio.sleep(0)  # yield to event loop


CALLBACKS: list[Callback] = []
