"""Build a ``ModbusConnection`` from the add-on / library port URL schemes."""

from __future__ import annotations

from urllib.parse import urlparse

from modbus_connection import ModbusSerialParams, ModbusTcpParams, ModbusUdpParams
from modbus_connection.tmodbus import ModbusConnection

type ConnectionParams = ModbusTcpParams | ModbusUdpParams | ModbusSerialParams

# ponytail: Deye + USB-FTDI need a pause after each reply. tmodbus's RTU 3.5-char
# gap is counted from *send*, so it is already elapsed when the response arrives
# and the next poll goes out immediately. Ceiling: a noisy bus still times out;
# then retry/flush on timeout belongs in tmodbus (buffer is not cleared today).
DEFAULT_MESSAGE_SPACING = 0.05


def url_to_params(port: str, baudrate: int = 9600) -> ConnectionParams:
    """Map a port URL (or serial device path) to connection params."""
    url = urlparse(port)
    if url.hostname:
        host, tcp_port = url.hostname, url.port or 502
        match url.scheme:
            case "tcp":
                return ModbusTcpParams(host=host, port=tcp_port)
            case "serial-tcp":
                return ModbusTcpParams(host=host, port=tcp_port, framer="rtu")
            case "udp":
                return ModbusUdpParams(host=host, port=tcp_port)
            case "serial-udp":
                raise NotImplementedError(
                    "serial-udp (RTU-over-UDP) is not supported by the tmodbus "
                    "backend; use serial-tcp:// or a serial device path"
                )
            case _:
                raise NotImplementedError(
                    f"Unknown scheme {url.scheme!r}: expected tcp, serial-tcp, "
                    "udp, or a serial device path"
                )
    return ModbusSerialParams(device=port, baudrate=baudrate)


def open_connection(
    port: str,
    *,
    baudrate: int = 9600,
    timeout: float = 10,
    message_spacing: float | None = None,
    connect_delay: float = 0.0,
) -> ModbusConnection:
    """Create a tmodbus ``ModbusConnection`` for ``port`` (does not connect yet).

    ``message_spacing`` defaults to ``DEFAULT_MESSAGE_SPACING`` (50ms) so serial
    and RS485 gateways get a turnaround gap. Pass ``0`` to disable.
    """
    if message_spacing is None:
        message_spacing = DEFAULT_MESSAGE_SPACING
    return ModbusConnection(
        url_to_params(port, baudrate),
        timeout=timeout,
        message_spacing=message_spacing,
        connect_delay=connect_delay,
    )
