"""MQTT helper."""
import asyncio
import logging
from typing import Any

from paho.mqtt.client import Client

_LOGGER = logging.getLogger(__name__)


class MQTTClient:
    """Basic MQTT Client."""

    def __init__(self) -> None:
        """Init MQTT Client."""
        self._client = Client()

        def on_connect(*, rc: int, **_kwargs) -> None:
            msg = {
                0: "successful",
                1: "refused - incorrect protocol version",
                2: "refused - invalid client identifier",
                3: "refused - server unavailable",
                4: "refused - bad username or password",
                5: "refused - not authorised",
            }.get(rc, f"refused - {rc}")
            _LOGGER.info("MQTT: Connection %s", msg)

        self._client.on_connect = on_connect

    async def connect(self, host: str, port: int, username: str, password: str) -> None:
        """Connect."""
        if not self._client.is_connected():
            _LOGGER.info("Connecting")
            self._client.username_pw_set(username=username, password=password)
            self._client.connect_async(host=host, port=port)
            self._client.loop_start()

        while not self._client.is_connected():
            await asyncio.sleep(1)

    async def disconnect(self) -> None:
        """Stop the MQTT client."""

        def _stop() -> None:
            # Do not disconnect, we want the broker to always publish will
            self._client.loop_stop()

        await asyncio.get_running_loop().run_in_executor(None, _stop)

    async def publish(
        self, topic: str, payload: Any, qos: int = 0, retain: bool = False
    ) -> None:
        """Publish a MQTT message."""
        # async with self._paho_lock:
        if not isinstance(qos, int):
            qos = 0
        await asyncio.get_running_loop().run_in_executor(
            None, self._client.publish, topic, payload, qos, retain is True
        )
