"""Timer class to run callbacks every x seconds."""
import asyncio
import logging
import time
from math import modf
from typing import Any, Awaitable, Callable, Optional

import attrs

_LOGGER = logging.getLogger(__name__)


@attrs.define(slots=True)
class Callback:
    """A callback."""

    # pylint: disable=too-few-public-methods
    name: str = attrs.field()
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


CALLBACKS: list[Callback] = []


async def run_callbacks(callbacks: list[Callback]) -> None:
    """Run the timer."""
    while callbacks:
        frac, _ = modf(time.time())
        await asyncio.sleep(1.1 - frac)  # Try to run at 50ms past the second
        now = int(time.time())
        for cb in callbacks:  # pylint: disable=invalid-name
            if cb.next_run > 0:
                nrdelta = now - cb.next_run
                if nrdelta > 0:
                    _LOGGER.warning(
                        "Callback %s was missed by %d seconds", cb.name, nrdelta
                    )
            elif now % cb.every != 0:
                continue

            if not cb.coroutinecb:
                cb.callback(now)
                continue

            # schedule a new run, if the previous is done
            if cb.task and not cb.task.done():
                # _LOGGER.warning("Callback %s still running (%d)", cb.name, now % 60)
                continue

            cb.next_run = now + cb.every
            cb.task = asyncio.create_task(cb.wrap_callback(now))
