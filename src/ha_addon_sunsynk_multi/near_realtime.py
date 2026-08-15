"""Near-realtime MQTT publish mode for power sensors (#401)."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

_LOG = logging.getLogger(__name__)

NEAR_REALTIME_SECONDS = 600


@dataclass(slots=True)
class NearRealtime:
    """Mutable near-realtime flag and auto-off timer."""

    enabled: bool = False
    off_task: asyncio.Task[None] | None = None
    on_auto_off: Callable[[], Awaitable[None]] | None = None

    def set(self, enabled: bool) -> None:
        """Enable or disable near-realtime publish mode.

        When enabled, starts a timer that turns the mode off after
        ``NEAR_REALTIME_SECONDS``. Enabling again resets the timer; disabling
        cancels it.
        """
        if self.off_task is not None:
            self.off_task.cancel()
            self.off_task = None
        self.enabled = enabled
        _LOG.info("Near realtime %s", "enabled" if enabled else "disabled")
        if enabled:
            self.off_task = asyncio.create_task(self._auto_off())

    async def _auto_off(self) -> None:
        """Sleep then clear near-realtime and notify MQTT."""
        try:
            await asyncio.sleep(NEAR_REALTIME_SECONDS)
        except asyncio.CancelledError:
            return
        self.enabled = False
        self.off_task = None
        _LOG.info("Near realtime auto-off after %ss", NEAR_REALTIME_SECONDS)
        if self.on_auto_off is not None:
            await self.on_auto_off()


NEAR_REALTIME = NearRealtime()
