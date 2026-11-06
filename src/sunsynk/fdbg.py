"""FDBG Modbus bridge support."""

from __future__ import annotations

import asyncio
import json
import re
import time
import socket
from dataclasses import dataclass

import requests
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
from urllib.error import URLError

from modbus_connection import (
    ModbusConnection as BaseModbusConnection,
    ModbusConnectionError,
    ModbusProtocolError,
)

from tmodbus.utils.crc import calculate_crc16, validate_crc16


@dataclass(frozen=True, kw_only=True)
class FdbgParams:
    """HTTP endpoint exposing a Modbus gateway at ``/fdbg.cgi``."""

    host: str
    path: str = "/fdbg.cgi"
    port: int = 80
    min_source_port: int = 0
    max_source_port: int = 0
    scheme: str = "http"

    def __post_init__(self) -> None:
        if not self.host:
            raise ValueError("host is required")
        if not self.path.startswith("/"):
            raise ValueError("path must start with '/'")
        if self.port <= 0:
            raise ValueError("port must be positive")
        if self.min_source_port < 0 or self.max_source_port < 0 or (self.min_source_port == 0 != self.max_source_port == 0):
            raise ValueError("source port range must be positive")
        if self.min_source_port > self.max_source_port:
            raise ValueError("min_source_port must be <= max_source_port")
    @property
    def url(self) -> str:
        return f"{self.scheme}://{self.host}:{self.port}{self.path}"

def _hex_bytes(payload: bytes) -> str:
    return " ".join(f"{byte:02X}" for byte in payload)


def _parse_fdbg_data(raw: bytes) -> bytes:
    text = raw.decode("utf-8", errors="replace")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r'"data"\s*:\s*"((?:[^"\\]|\\.)*)"', text)
        if match is None:
            raise ModbusProtocolError(f"unexpected FDBG response: {text!r}") from None
        payload = {"data": match.group(1).encode("utf-8").decode("unicode_escape")}
    data = payload.get("data")
    if not isinstance(data, str):
        raise ModbusProtocolError(f"FDBG response missing 'data': {text!r}")
    clean = "".join(data.split())
    if not clean:
        raise ModbusProtocolError("FDBG response had no payload data")
    try:
        return bytes.fromhex(clean)
    except ValueError as exc:
        raise ModbusProtocolError(f"FDBG response was not valid hex: {data!r}") from exc


class FdbgModbusUnit:
    """Single-unit Modbus client talking to a FDBG HTTP endpoint."""

    def __init__(self, connection: FdbgModbusConnection, unit_id: int) -> None:
        self._connection = connection
        self.unit_id = unit_id

    @property
    def connected(self) -> bool:
        return self._connection.connected

    async def _request(
        self,
        function_code: int,
        address: int,
        *,
        count: int = 0,
        values: list[int] | None = None,
    ) -> bytes:
        payload = bytes([self.unit_id, function_code])
        if function_code in (0x03, 0x04):
            payload += bytes(
                [
                    (address >> 8) & 0xFF,
                    address & 0xFF,
                    (count >> 8) & 0xFF,
                    count & 0xFF,
                ]
            )
        elif function_code in (0x06, 0x10):
            if function_code == 0x06:
                values = [address, count]
                address = 0
            payload += bytes(
                [
                    (address >> 8) & 0xFF,
                    address & 0xFF,
                ]
            )
            if function_code == 0x06:
                payload += bytes(
                    [
                        (values[0] >> 8) & 0xFF,
                        values[0] & 0xFF,
                    ]
                )
            else:
                quantity = len(values)
                payload += bytes(
                    [
                        (quantity >> 8) & 0xFF,
                        quantity & 0xFF,
                        len(values) * 2,
                    ]
                )
                for value in values:
                    payload += bytes(
                        [
                            (value >> 8) & 0xFF,
                            value & 0xFF,
                        ]
                    )
        else:
            raise NotImplementedError(
                f"FDBG backend does not support function code {function_code:#04x}"
            )
        frame = payload + calculate_crc16(payload)
        return await self._connection._post(frame)

    async def read_holding_registers(self, address: int, count: int) -> list[int]:
        if count <= 0:
            return []
        response = await self._request(0x03, address, count=count)
        if len(response) < 5:
            raise ModbusProtocolError(f"FDBG FC03 response too short: {response!r}")
        if not validate_crc16(response):
            raise ModbusProtocolError(
                f"FDBG FC03 response has invalid CRC: {response!r}"
            )
        if response[0] != self.unit_id or response[1] != 0x03:
            raise ModbusProtocolError(
                f"FDBG FC03 response for unit {self.unit_id} was {response!r}"
            )
        byte_count = response[2]
        if count * 2 != byte_count:
            raise ModbusProtocolError(
                f"FDBG FC03 byte count mismatch: expected {count * 2}, got {byte_count}"
            )
        if len(response) != 5 + byte_count:
            raise ModbusProtocolError(
                f"FDBG FC03 response length mismatch: {len(response)} != {5 + byte_count}"
            )
        register_bytes = response[3:-2]
        values = [
            (register_bytes[i] << 8) | register_bytes[i + 1]
            for i in range(0, len(register_bytes), 2)
        ]
        return values

    async def read_input_registers(self, address: int, count: int) -> list[int]:
        response = await self._request(0x04, address, count=count)
        return _decode_register_response(self.unit_id, 0x04, response, count)

    async def write_register(self, address: int, value: int) -> None:
        await self.write_registers(address, [value])

    async def write_registers(self, address: int, values: list[int]) -> None:
        if not values:
            return
        response = await self._request(0x10, address, values=values)
        if not validate_crc16(response):
            raise ModbusProtocolError(
                f"FDBG FC16 response has invalid CRC: {response!r}"
            )
        if response[0] != self.unit_id or response[1] != 0x10:
            raise ModbusProtocolError(
                f"FDBG FC16 response for unit {self.unit_id} was {response!r}"
            )
        if response[2:4] != bytes(
            [
                (address >> 8) & 0xFF,
                address & 0xFF,
            ]
        ):
            raise ModbusProtocolError(
                f"FDBG FC16 address mismatch: expected {address:#06x}, got {response[2:4]!r}"
            )
        if response[4:6] != bytes(
            [
                (len(values) >> 8) & 0xFF,
                len(values) & 0xFF,
            ]
        ):
            raise ModbusProtocolError(
                f"FDBG FC16 quantity mismatch: expected {len(values)}, got {response[4:6]!r}"
            )

    async def read_coils(self, address: int, count: int) -> list[bool]:
        raise NotImplementedError("FDBG backend does not support coils")

    async def read_discrete_inputs(self, address: int, count: int) -> list[bool]:
        raise NotImplementedError("FDBG backend does not support discrete inputs")

    async def write_coil(self, address: int, value: bool) -> None:
        raise NotImplementedError("FDBG backend does not support coils")

    async def write_coils(self, address: int, values: list[bool]) -> None:
        raise NotImplementedError("FDBG backend does not support coils")

    async def read_exception_status(self) -> int:
        raise NotImplementedError("FDBG backend does not support exception status")

    async def report_server_id(self) -> bytes:
        raise NotImplementedError("FDBG backend does not support report_server_id")

    async def mask_write_register(
        self, address: int, and_mask: int, or_mask: int
    ) -> None:
        raise NotImplementedError("FDBG backend does not support mask_write_register")

    async def read_write_registers(
        self,
        read_address: int,
        read_count: int,
        write_address: int,
        write_values: list[int],
    ) -> list[int]:
        raise NotImplementedError("FDBG backend does not support read_write_registers")

    async def read_fifo_queue(self, address: int) -> list[int]:
        raise NotImplementedError("FDBG backend does not support FIFO queue")

    async def read_device_identification(self) -> dict[int, bytes]:
        raise NotImplementedError("FDBG backend does not support device identification")

    async def read_file_record(
        self, file: int, record: int, length: int
    ) -> list[int]:
        raise NotImplementedError("FDBG backend does not support file records")

    async def write_file_record(
        self, file: int, record: int, values: list[int]
    ) -> None:
        raise NotImplementedError("FDBG backend does not support file records")

    async def diagnostics(self, sub_function: int, data: int = 0) -> int:
        raise NotImplementedError("FDBG backend does not support diagnostics")

    async def get_comm_event_counter(self) -> tuple[bool, int]:
        raise NotImplementedError("FDBG backend does not support event counter")

    async def get_comm_event_log(self) -> bytes:
        raise NotImplementedError("FDBG backend does not support event log")

    def set_message_spacing(self, seconds: float) -> None:
        return None

    def require_timeout(self, seconds: float | None) -> None:
        return None

    def require_connect_delay(self, seconds: float | None) -> None:
        return None

    def on_connection_lost(self, callback):
        return lambda: None

    async def disconnect(self) -> None:
        await self._connection.disconnect()


def _decode_register_response(
    unit_id: int,
    function_code: int,
    response: bytes,
    expected_count: int,
) -> list[int]:
    if len(response) < 5:
        raise ModbusProtocolError(
            f"FDBG FC{function_code:02x} response too short: {response!r}"
        )
    if not validate_crc16(response):
        raise ModbusProtocolError(
            f"FDBG FC{function_code:02x} response has invalid CRC: {response!r}"
        )
    if response[0] != unit_id or response[1] != function_code:
        raise ModbusProtocolError(
            f"FDBG FC{function_code:02x} response for unit {unit_id} was {response!r}"
        )
    byte_count = response[2]
    if expected_count * 2 != byte_count:
        raise ModbusProtocolError(
            f"FDBG FC{function_code:02x} byte count mismatch: expected {expected_count * 2}, got {byte_count}"
        )
    if len(response) != 5 + byte_count:
        raise ModbusProtocolError(
            f"FDBG FC{function_code:02x} response length mismatch: {len(response)} != {5 + byte_count}"
        )
    register_bytes = response[3:-2]
    return [
        (register_bytes[i] << 8) | register_bytes[i + 1]
        for i in range(0, len(register_bytes), 2)
    ]

class SourcePortAdapter(HTTPAdapter):
    def __init__(self, min_source_port, max_source_port, **kwargs):
        self.min_source_port = min_source_port
        self.max_source_port = max_source_port
        self.source_port = min_source_port
        super().__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        # Bind to all local interfaces ('0.0.0.0') and the chosen source port
        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            socket_options=[(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)],
            retries=False,
            **pool_kwargs
        )

    def get_connection_with_tls_context(self, request, verify, proxies = None, cert = None):
        # Ensure the source port is incremented for each new connection
        self.source_port += 1
        if self.source_port > self.max_source_port:
            self.source_port = self.min_source_port
        self.poolmanager.connection_pool_kw['source_address'] = ('0.0.0.0', self.source_port)
        return super().get_connection_with_tls_context(request, verify, proxies, cert)

class FdbgModbusConnection(BaseModbusConnection):
    """Modbus connection wrapper for a FDBG HTTP bridge."""

    def __init__(
        self,
        params: FdbgParams,
        *,
        timeout: float | None = None,
        message_spacing: float | None = None,
        connect_delay: float | None = None,
    ) -> None:
        super().__init__(
            params,
            timeout=timeout,
            message_spacing=message_spacing,
            connect_delay=connect_delay,
        )
        self._request_lock = asyncio.Lock()
        self._last_request_at = 0.0
        self._request_interval = max(
            0.0,
            float(
                getattr(getattr(self, "_pacer", None), "_message_spacing", 0.0)
                or 0.0
            ),
        )

    def for_unit(self, unit_id: int) -> FdbgModbusUnit:
        return FdbgModbusUnit(self, unit_id)

    async def _connect_client(self) -> object:
        if not isinstance(self._params, FdbgParams):
            raise ModbusConnectionError("FDBG connection requires FdbgParams")
        session = requests.Session()
        session.mount("http://", SourcePortAdapter(min_source_port=self._params.min_source_port, max_source_port=self._params.max_source_port))
        session.headers.update({
            "Content-Type": "application/octet-stream",
            "Connection": "close",
        })
        return session

    async def _close_client(self, client: object) -> None:
        if hasattr(client, "close"):
            client.close()

    async def _post(self, payload: bytes) -> bytes:
        if not isinstance(self._params, FdbgParams):
            raise ModbusConnectionError("FDBG connection requires FdbgParams")

        async with self._request_lock:
            now = time.monotonic()
            elapsed = now - self._last_request_at
            if elapsed < self._request_interval:
                await asyncio.sleep(self._request_interval - elapsed)
            self._last_request_at = time.monotonic()

            request_body = json.dumps(
                {"data": _hex_bytes(payload)}, separators=(",", ":")
            ).encode("ascii")
            session = self._client
            if session is None:
                await self.connect()
                session = self._client
            if not isinstance(session, requests.sessions.Session):
                raise ModbusConnectionError("FDBG HTTP session is not initialized")
            for attempt in range(3):
                try:
                    response = await asyncio.to_thread(
                        session.post,
                        self._params.url,
                        data=request_body,
                        timeout=self._timeout,
                        headers={
                            "Content-Type": "application/octet-stream",
                            "User-Agent": "hackney/1.20.1",
                            "Connection": "close",
                        },
                    )
                    raw = response.content
                    response.connection.close()
                    response.close()
                except (TimeoutError, URLError, requests.RequestException) as exc:
                    if attempt < 2:
                        print(f"FDBG request timed out, retrying... ({exc})")
                        await asyncio.sleep(self._request_interval)
                        continue
                    else:
                        raise ModbusConnectionError(
                            f"failed to contact {self._target}: {exc}"
                        ) from exc
                return _parse_fdbg_data(raw)
