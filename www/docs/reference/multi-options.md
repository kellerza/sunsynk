# Configuration

A typical Home Assistant OS setup needs three things: inverter type, which sensors to poll, and one
`INVERTERS` entry. MQTT is discovered from the Supervisor. Tune [Connection](#connection) and
[Stale inverter](#stale-inverter-global) only if the bus is flaky or you share RS485 between units.

1. Set `SENSOR_DEFINITIONS` and `SENSORS` (groups or names — see [Sensors](#sensors)).
2. Add one `INVERTERS` item: `SERIAL_NR`, `PORT`, `MODBUS_ID`, `HA_PREFIX`.
3. Leave MQTT blank on Home Assistant OS.
4. If reads fail or several inverters share a wire, lower the batch size, add spacing, or use the
   stale options.

```yaml
SENSOR_DEFINITIONS: single-phase
SENSORS:
  - energy_management
  - power_flow_card
  - pv1
SENSORS_FIRST_INVERTER:
  - settings
INVERTERS:
  - SERIAL_NR: "007"
    HA_PREFIX: SS
    MODBUS_ID: 1
    PORT: tcp://homeassistant.local:502
```

::: tip
Options with a <i-mdi-dev-to class="vp-edge-option-icon" /> icon appear only in the **edge** add-on
and are not in **sunsynk-multi** yet.
:::

## Sensors

Sensor ids, groups, and custom sensors are listed under [definitions](./definitions).

- `SENSOR_DEFINITIONS` – Inverter family: `single-phase`, `single-phase-16kw`, `three-phase`, or
  `three-phase-hv`.

- `SENSORS` – Groups or sensor ids to poll on **every** inverter (`energy_management`,
  `battery_soc`, `pv1`, …).

- `SENSORS_FIRST_INVERTER` – Extra sensors for the **first** inverter only (typically `settings`).

- `SENSOR_OVERRIDES` – List of `key=value` strings that override a sensor attribute.

  ```yaml
  SENSOR_OVERRIDES:
    - prog4_power.max=4990
    - battery_max_charge_current.max=350
    - battery_max_discharge_current.max=350
  ```

  ::: details The log will show if an override was applied.
  During startup, the log prints all overrides, directly after the line that shows which sensor
  definitions were loaded.

  ```log
  [08:19:42] INFO    Importing sensor definitions single-phase (view the source online: https://github.com/kellerza/sunsynk/tree/main/src/sunsynk/definitions/single_phase.py )
  [08:19:42] INFO    Applying sensor overrides from configuration
  +-------------+-----------+-------+----------+
  |    Sensor   | Attribute | Value | Message  |
  +-------------+-----------+-------+----------+
  |    Serial   |   trace   |   1   | ✓ 0 -> 1 |
  | Battery SOC |   trace   |   1   | ✓ 0 -> 1 |
  | Prog5 power |   trace   |   1   | ✓ 0 -> 1 |
  +-------------+-----------+-------+----------+
  ```

  :::
  ::: details Trace the value of any sensor.
  Set `.trace=1` on a sensor to log every change (old/new value and raw registers). Useful when
  debugging definitions; leave it off for normal use.

  ```yaml
  SENSOR_OVERRIDES:
    - prog4_power.trace=1
  ```

  :::

## Inverters

`INVERTERS` is a list. Each item needs:

- `SERIAL_NR` – Inverter serial. On startup the connected serial is printed in the log. The add-on
  will not run if this does not match.
  ::: tip
  This must be a string. Quote a numeric serial, especially if it starts with a zero: `'01000'`.
  :::

- `HA_PREFIX` – Unique per inverter. Used as the Home Assistant device name and as the prefix on
  entity ids (default `SS`). Must be unique when you have more than one inverter.

- `MODBUS_ID` – Modbus **server** id (the inverter answers requests). Typically `1`. Must match the
  inverter **Modbus SN**. Unique per inverter on a shared bus. See
  [Modbus](../guide/overview#modbus).

- `DONGLE_SERIAL_NUMBER` – Required for `solarman://`. A non-zero value also remaps `tcp://host` to
  Solarman.

- `PORT` – Transport URL or serial path. See [Port](#port).

### Port

| Scheme                   | When                                                | Extra                                                                                                           |
| ------------------------ | --------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| `tcp://host:502`         | Modbus TCP gateway or [mbusd](../guide/mbusd)       | —                                                                                                               |
| `serial-tcp://host:port` | Gateway that does **not** convert Modbus TCP to RTU | Sends RTU frames over TCP. `serial-udp://` is not supported                                                     |
| `udp://host:port`        | Modbus UDP                                          | —                                                                                                               |
| `solarman://host:8899`   | Solarman / Wi-Fi dongle                             | Set `DONGLE_SERIAL_NUMBER`. Prefer a fixed IP                                                                   |
| `/dev/ttyUSB0`           | Direct USB RS485                                    | tmodbus. If it fails, try [mbusd](../guide/mbusd) ([issue 131](https://github.com/kellerza/sunsynk/issues/131)) |
| `""`                     | First inverter only                                 | Uses `DEBUG_DEVICE` from the bottom of the config                                                               |

```yaml
INVERTERS:
  - PORT: tcp://homeassistant.local:502
```

List USB serial devices under _Supervisor_ → _System_ → _Host_ **&vellip;** → _Hardware_ (or copy
the path from `DEBUG_DEVICE`).

`DRIVER` is obsolete. The add-on will not start if it is still set.

::: details Solarman Wi-Fi dongle
Use `solarman://` with the dongle's local IP (typically port **8899**) and set
`DONGLE_SERIAL_NUMBER`. Find the IP on your router, or use a utility like
[netscan](https://www.portablefreeware.com/?id=730). Prefer a fixed IP.

```yaml
INVERTERS:
  - PORT: solarman://192.168.1.182:8899
    DONGLE_SERIAL_NUMBER: "1234567890"
```

Reduce how often you read — see [Schedules](./schedules#proposed-schedule-overrides-for-solarman).
:::

::: tip Shared RS485 bus (one connector, many inverters)
Repeat the **same** `PORT` on each `INVERTERS` entry. Each unit still needs its own `MODBUS_ID`,
`SERIAL_NR`, and `HA_PREFIX`. The add-on runs **one I/O request at a time** on that shared port so
several clients are not fighting the same link. This is the recommended layout when every inverter
is on one physical bus.
:::

## Connection

Global. Change these when a gateway or RS485 link is unreliable.

- `READ_SENSORS_BATCH_SIZE` – Max registers per Modbus read (default **20**). USR-style devices
  often need **8**. mbusd can go higher.

- `READ_ALLOW_GAP` – Unused registers allowed inside one sequential read block (default **2**). A
  slightly larger block is often cheaper than extra requests.

- `READ_MESSAGE_SPACING` – Seconds to wait after each successful Modbus reply before the next
  request on the same link (serial, `tcp://`, `serial-tcp://`, `udp://`). Default **0.05**. **0**
  disables the gap. Increase on flaky RS485 / USB-FTDI links. Not used for `solarman://`. Raising
  `TIMEOUT` does not add this pause.

- `TIMEOUT` – Modbus timeout in seconds for connect and register read/write (default **10**, max
  **15**). Increase on slow links. If timeouts persist, lower `READ_SENSORS_BATCH_SIZE` or increase
  `READ_MESSAGE_SPACING`.

## Schedules

`SCHEDULES` controls how often sensors are read and published. Defaults and Solarman-friendly
overrides: [Schedules](./schedules).

## Stale inverter (global)

If several inverters share one RS485 bus and one unit stops answering, pause polling **that** unit
so the others keep running.

- `STALE_INVERTER_AFTER_SECONDS` – After each **successful** read, if failures continue for this
  many seconds, polling that inverter pauses. Default `120`.

- `STALE_INVERTER_SKIP_SECONDS` – How long to stay paused before one serial probe and a possible
  resume. Default `600`.

See also [Fault finding](../guide/fault-finding).

## Home Assistant Discovery options

- `HA_PREFIX` – See [Inverters](#inverters). Device name and prefix on every entity id.

- `MANUFACTURER` – Name shown on the Home Assistant device. It does not have to be Sunsynk ;-)

- `NUMBER_ENTITY_MODE` – How read/write number entities display: `auto` (default), `box`, or
  `slider`.

- `PROG_TIME_INTERVAL` – Step in minutes for program-time select lists (`5`, `10`, `15`, `30`, `45`,
  `60`). **5** produces a very long list.

## MQTT Settings

On a standard Home Assistant OS install you do not need MQTT settings. The add-on asks the
Supervisor for the broker and credentials and ignores YAML when that succeeds.

The MQTT integration should publish birth (**online**) and last will (**offline**) to
`homeassistant/status` (_Re-configure MQTT_ in the UI).

::: details MQTT configuration options (optional)

Supervisor discovery is used unless `MQTT_CUSTOM: true` is set.

```yaml
MQTT_CUSTOM: true   # Force the add-on to use this MQTT configuration
MQTT_HOST: core-mosquitto
MQTT_PORT: 1883
MQTT_USERNAME: hass
MQTT_PASSWORD: my-secure-password
```

:::

::: details Availability topics (advanced)

Discovery uses two **retained** topics. Home Assistant availability mode **all** requires **both**
to be **online**:

- **`SS/availability_<joined>`** – MQTT session for the whole add-on. `<joined>` is every inverter’s
  slugged `HA_PREFIX`, sorted alphabetically, joined with `_`. Examples: one inverter `ss` →
  `SS/availability_ss`; two inverters `shed` and `house` → `SS/availability_house_shed`. **offline**
  when the MQTT client disconnects (broker last will) or crashes before the will is cleared.
- **`SS/availability_1_<HA_PREFIX>`** – Per-inverter poll loop. **offline** when that inverter is
  not polling (repeated read errors / stale skip, or reconnecting Modbus while the broker session is
  still up).

:::

## Debug options

- `DEBUG` – Log verbosity (`0`–`5`). `0` is normal.

  | Value | Description                  |
  | ----- | ---------------------------- |
  | `0`   | No extra debug messages.     |
  | `1`   | Messages for filter changes. |
  | `2`   | Debug level logging.         |

- `DEBUG_DEVICE` – USB serial picker in the UI. Used only when `PORT` is empty. Supervisor still
  requires a device to be selected.

- `MUTE_LOGS` – Local times (`hh:mm`) when logging is raised to critical for 60 seconds to hide
  noisy expected messages.
