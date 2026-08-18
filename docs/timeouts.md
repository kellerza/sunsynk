# Modbus timeouts

How register I/O deadlines, pacing, and retries work in sunsynk and the Home Assistant add-on.
Background on the v1.0.0 stack change is [modbus-connection.md](modbus-connection.md). User-facing
tuning tips are in [fault-finding](../www/docs/guide/fault-finding.md#c-reducing-timeouts) and
[multi-options](../www/docs/reference/multi-options.md).

Reported regressions after the v1.0.0 move from pymodbus to tmodbus / modbus-connection are tracked
in [#672](https://github.com/kellerza/sunsynk/issues/672).

## Shared behaviour (all transports)

### Add-on `TIMEOUT`

The **`TIMEOUT`** option (default **10** seconds) is the deadline for:

- opening the link (connect), and
- each individual register read or write attempt.

It is **not** a cap on an entire sensor batch or poll cycle. `Sunsynk.read_sensors()` may issue many
FC03 groups in one call; each group gets its own deadline.

Before v1.0.0 edge fixes, the library also wrapped batches in `asyncio.timeout(2 × TIMEOUT)`. That
double layer is **removed** — only the modbus-connection / Solarman client deadline applies now.

Raising `TIMEOUT` makes the client wait **longer for a missing reply**. It does **not** insert a
pause **between** successful requests. For that, see [message spacing](#message-spacing) below.

### Add-on retries and stale inverters

Above the driver, `AInverter` adds:

| Layer                  | Behaviour                                                                                                                                  |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `read_sensors_retry()` | Up to **3** attempts per scheduled read, **0.2s** apart; then retries **one sensor at a time** if the batch failed                         |
| Stale quiet            | After **`STALE_INVERTER_AFTER_SECONDS`** without a successful read, skip Modbus for **`STALE_INVERTER_SKIP_SECONDS`**, then probe identity |
| Timeout counter        | `Sunsynk.timeouts` increments on timeout; exposed as the **RS485 timeout** MQTT sensor                                                     |

These apply to Modbus (serial / TCP) and Solarman alike.

### Message spacing

For Modbus connections opened via [`open_connection()`](../src/sunsynk/connection.py), the library
sets **`message_spacing = 0.05`** (50ms) by default. modbus-connection waits that long after the
**previous request finished** before starting the next one on the same link (shared across all
`for_unit()` handles on that port).

Pass `message_spacing=0` to `open_connection()` to disable. There is no add-on option for this yet;
the default is fixed in code (`DEFAULT_MESSAGE_SPACING`).

---

## Serial

**PORT examples:** `/dev/ttyUSB0`, `/dev/serial/by-id/usb-FTDI_…`

Direct RS485 through a USB adapter uses **tmodbus** RTU via
[modbus-connection](https://home-assistant-libs.github.io/modbus-connection/) (`ModbusConnection`

- `ModbusSerialParams`).

### Why v1.0.0 regressed on serial

Pre-1.0.0 **pymodbus** (`PySunsynk`) was relatively forgiving on direct serial: extra asyncio
overhead, per-group `asyncio.timeout`, and behaviour that often masked bus timing issues.

v1.0.0 **tmodbus** is stricter:

1. **No turnaround gap by default** — Modbus RTU requires a silent interval (3.5 character times)
   before a new frame. tmodbus enforces that gap from the **send** time (`_last_frame_ended_at` is
   updated when the request is written). By the time the inverter replies, that interval has already
   elapsed, so the **next poll can go out immediately** after the response is parsed.
2. **Slow slaves** — Deye inverters and USB-FTDI adapters often need tens of milliseconds after a
   reply before they accept another master request. Polling back-to-back produces intermittent
   timeouts (~every 10s with default `TIMEOUT`, matching field reports in #672).
3. **FTDI latency** — FT232R and similar chips buffer serial data (default latency timer ~16ms).
   tmodbus documents that true inter-frame silence detection is unreliable on USB serial; it sizes
   frames by content instead. Late bytes can still land in the buffer after a timeout.
4. **No retry on timeout** — modbus-connection configures tmodbus with `response_retry_strategy`
   that does **not** retry bare `TimeoutError`. One missed frame surfaces as an error immediately.
5. **Buffer not flushed on timeout** — on RTU timeout, tmodbus leaves unread bytes in the protocol
   buffer. The next request can then see garbage (`Received data with no pending requests`,
   `Cannot frame response with unsupported function code 0x79`) until the link recovers or the
   add-on is restarted.

Increasing **`TIMEOUT`** alone does not fix (1)–(3); it only waits longer before declaring failure.

### Fix: 50ms message spacing

`sunsynk.connection.open_connection()` now defaults to **50ms** `message_spacing` for all Modbus
ports (including serial). That gap is enforced **after each completed request** by
modbus-connection’s `Pacer`, giving the inverter and adapter time to turn the bus around.

This matches common RS485 guidance (roughly **50–100ms** between commands on slow devices) and is
the main code-side mitigation for #672 on direct serial.

### What still helps on serial

- Lower **`READ_SENSORS_BATCH_SIZE`** (e.g. 8) — smaller FC03 reads, less time on the wire per
  request.
- **`READ_ALLOW_GAP`** — batch nearby registers; fewer total requests.
- **mbusd** — run mbusd on the serial port and point the add-on at `tcp://host:502` (see
  [fault-finding](../www/docs/guide/fault-finding.md#direct-serial)).
- **One client per port** — do not share the serial device with mbusd, Node-RED, or a second add-on
  instance.
- **Cabling / termination** — see fault-finding; unrelated to the v1.0.0 stack but often confused
  with it.

### Code path

```text
AInverter.read_sensors()
  → Sunsynk.read_sensors()     # groups sensors, one FC03 per group
    → unit.read_holding_registers()
      → modbus-connection TmodbusUnit  # connect + Pacer (50ms) + tmodbus RTU
```

Implementation: [`connection.py`](../src/sunsynk/connection.py),
[`sunsynk.py`](../src/sunsynk/sunsynk.py),
[`driver.py`](../src/ha_addon_sunsynk_multi/driver.py) (`_shared_modbus_connection`).

---

## TCP

**PORT examples:** `tcp://192.168.1.50:502`, `serial-tcp://gateway:502`, `udp://host:502`

Modbus TCP, RTU-over-TCP, and UDP use the same **tmodbus** / modbus-connection stack as serial. The
add-on passes **`TIMEOUT`** and the default **50ms** `message_spacing` into `open_connection()`.

### `tcp://` (Modbus TCP / MBAP)

Typical setups:

- **mbusd** or another gateway exposing Modbus TCP on the LAN.
- **RS485→Ethernet** devices (Waveshare, USR, etc.) speaking Modbus TCP toward the host.

Requests are serialized on **one `ModbusConnection` per PORT** string. Multiple inverters on the
same gateway share that connection; modbus-connection’s lock and pacer ensure only one transaction
is in flight at a time.

Timeouts here are usually **gateway or multi-master** issues rather than RTU turnaround:

- **`Received unexpected response with Transaction ID`** — another client is talking to the same
  gateway, or the gateway returned a late MBAP frame for an earlier request (#672, multi-inverter
  setups).
- **`Inverter … stale`** — no successful read within `STALE_INVERTER_AFTER_SECONDS`; often follows
  repeated timeouts, not necessarily total loss of connectivity (external Modbus tools may still
  work).

Raising `TIMEOUT` can help on **slow gateways** or long RTU legs behind TCP. The **50ms spacing**
still applies between requests on the shared connection (including when two `MODBUS_ID`s share one
`tcp://` PORT).

### `serial-tcp://` (RTU-over-TCP)

Same as TCP for the socket side, but the framer is **RTU**. The gateway translates RTU frames on the
RS485 side. Spacing and turnaround constraints from [Serial](#serial) apply
**on the bus behind the gateway**; the 50ms default helps gateways that forward requests immediately
without pacing.

If the gateway buffers poorly under rapid polling, prefer **`tcp://`** (native Modbus TCP) when the
device supports it, or reduce batch size / read frequency.

### `udp://`

Modbus UDP (socket framing) via tmodbus. Same timeout and message-spacing defaults. RTU-over-UDP
(`serial-udp://`) is **not** supported by the tmodbus backend.

### Code path

Same as serial; only `url_to_params()` differs ([`connection.py`](../src/sunsynk/connection.py)).

---

## Solarman

**PORT example:** `solarman://192.168.1.182:8899` plus **`DONGLE_SERIAL_NUMBER`**

Solarman does **not** use modbus-connection or tmodbus. It uses
[`SolarmanUnit`](../src/sunsynk/solarman.py) over **PySolarmanV5Async** (proprietary V5 tunnel).

### Timeouts

- **`TIMEOUT`** maps to **`socket_timeout`** on the Solarman client (connect and reads).
- **`TimeoutError`** on read: log, **disconnect**, re-raise — **no** retry inside `SolarmanUnit`
  (unlike other exceptions).
- Other read errors: up to **`RETRY_ATTEMPTS` (5)** with **2s** sleep and disconnect between tries.

There is **no** `message_spacing` knob on Solarman; pacing is whatever the dongle and
PySolarmanV5Async implement, plus the add-on’s normal poll schedules.

### Tuning

- Use **`solarman://`** explicitly (not `tcp://` with a dongle serial — that remaps at startup).
- Reduce read frequency in **Schedules**; Solarman links are slower than wired RS485.
- Do not point a serial `PORT` at a Solarman dongle IP; that is a different transport (#672 reports
  conflating the two).

### Code path

```text
create_sunsynk() → SolarmanUnit → PySolarmanV5Async.read_holding_registers()
```

No shared `ModbusConnection`; one Solarman client per inverter port entry.

---

## Quick reference

| Topic                          | Serial / TCP                          | Solarman                             |
| ------------------------------ | ------------------------------------- | ------------------------------------ |
| Library                        | modbus-connection + tmodbus           | PySolarmanV5Async                    |
| Add-on `TIMEOUT`               | Per connect / FC03 / FC16 attempt     | `socket_timeout`                     |
| Default gap after each reply   | **50ms** (`message_spacing`)          | —                                    |
| Driver retry on `TimeoutError` | No (immediate error)                  | No (disconnect)                      |
| Add-on batch retry             | Yes (`read_sensors_retry`)            | Yes (same)                           |
| Multi-inverter same PORT       | One connection, `for_unit(MODBUS_ID)` | Not supported (one dongle per entry) |

### Add-on options that affect this

User-facing keys from [multi-options](../www/docs/reference/multi-options.md) (and
[schedules](../www/docs/reference/schedules.md)). There is **no** add-on option for
`message_spacing`; it is fixed at 50ms in `open_connection()`.

| Option                          | Role                                                                                          |
| ------------------------------- | --------------------------------------------------------------------------------------------- |
| `TIMEOUT`                       | Deadline in **seconds** for connect and each register read/write (default **10**)             |
| `READ_SENSORS_BATCH_SIZE`       | Max registers per FC03 group (smaller → more requests, less time per request)                 |
| `READ_ALLOW_GAP`                | Extra registers allowed between addresses so groups merge (fewer requests)                    |
| `STALE_INVERTER_AFTER_SECONDS`  | Grace after last good read before the inverter is marked stale                                |
| `STALE_INVERTER_SKIP_SECONDS`   | Quiet period with no polling while stale, then an identity probe                              |

`DRIVER` is obsolete and ignored (startup fails if it is still set). mbusd has its own `TIMEOUT` if
you use that add-on as a serial-to-TCP gateway. The mbusd timeout should always be lower than the
addon timeout.

## Related changes (edge, post-1.0.0)

- [modbus-connection#213](https://github.com/home-assistant-libs/modbus-connection/pull/213) —
  serial `timeout` passed through to tmodbus (fixes `TIMEOUT` being ignored on RTU; does not add
  spacing).
- **50ms `message_spacing`** in `open_connection()` — addresses back-to-back polling on serial /
  RTU-backed links ([#672](https://github.com/kellerza/sunsynk/issues/672)).
- Removal of nested **`asyncio.timeout`** wrappers — avoids double cancellation; see edge CHANGELOG.
