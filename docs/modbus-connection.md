# Architecture: modbus-connection and sunsynk

How [modbus-connection](https://home-assistant-libs.github.io/modbus-connection/) fits this library,
why the underlay is `ModbusUnit` rather than `Component`, and what stays in sunsynk.

The implementation cut is [modbus-connection-plan.md](modbus-connection-plan.md).

## Layers

```text
HA add-on          schedules, MQTT, history_average, discovery
        ↓
sunsynk            Sensor, RWSensor, definitions, InverterState, group_sensors
        ↓
HoldingUnit        read_holding_registers / write_registers (FC16)
        ↓
        ├── ModbusConnection.for_unit(server_id)   tmodbus (TCP, RTU-over-TCP, serial)
        └── SolarmanUnit                           PySolarmanV5Async tunnel
```

The public API stays `Sensor` + `Sunsynk.read_sensors(sensors)`. Internally, holding-register I/O
goes to a unit. The add-on stores one `ModbusConnection` per port and passes
`connection.for_unit(modbus_id)` into each inverter.

`for_unit(id)` is the Modbus **server id** (device id): today’s `Sunsynk.server_id` and add-on
`MODBUS_ID`. It is not a register address.

## What hurts today

Three drivers (`PySunsynk`, `RSunsynk`, `SolarmanSunsynk`) each own connect/reconnect, timeouts, and
unit id. Multi-inverter sharing is a lock plus mutating `server_id`:

```python
async with lock:
    inv.server_id = self.opt.modbus_id
    inv.state = self.state
    yield inv
```

That is the problem `ModbusConnection` / `ModbusUnit` were written for: one owner-held link,
serialized requests, `for_unit(id)` handles, reconnect on the next call, `message_spacing` /
`connect_delay` instead of ad-hoc sleeps.

`group_sensors` + `InverterState` are a different problem. They are not a bad Modbus client. They
are the Deye application cache.

## Why not a parallel v2 library

A v2 that models the inverter as `Component` subclasses would duplicate the thing people actually
depend on: four definition files, `mysensors.py`, `SENSOR_OVERRIDES`, RW sensors, schedules, MQTT
history.

The [library pattern](https://home-assistant-libs.github.io/modbus-connection/patterns/library/)
wants:

- consumer owns the connection, library takes a `ModbusUnit`
- one `Component` per sub-system
- `async_update()` reads **that whole sub-system**
- `restrict_fields` once at setup for firmware variants

The add-on does the opposite every second: user-selected sensors, mixed `read_every`,
significant-change / average reporting, RW min/max as *other* sensors. `restrict_fields` is “this
firmware omits register 2”; it is not a poll schedule.

Two libraries means two decode paths until v1 is deleted. The decode is the product.

## Modelling mismatch

|             | sunsynk `Sensor`                                                         | `modbus_connection.model` field                              |
| ----------- | ------------------------------------------------------------------------ | ------------------------------------------------------------ |
| Address     | tuple of **arbitrary** registers                                         | one start + **consecutive** `count`                          |
| Layout      | instances in a dict, subset chosen at runtime                            | class attributes, plan cached on first update                |
| 32-bit      | `Sensor16((633, 691), …)` — two far-apart regs, stateful 16/32 heuristic | `uint32(n)` = registers `n` and `n+1`, stateless codec       |
| Combine     | `MathSensor((175, 169, 166), factors=(1, 1, -1))`                        | `@property` over other fields                                |
| Packed bits | `bitmask=` + read-modify-write                                           | `bit` / `bits` / `flags` (this part is **better**)           |
| Word order  | always little (`<h` / `<2H`)                                             | default **big**; would need `word_order="little"` everywhere |
| Writes      | FC16 even for one register                                               | FC06 unless `force_fc16=True`                                |
| Cache       | raw regs + decoded values + history + `onchange`                         | last decoded value on the component                          |

`Sensor16` and `MathSensor` block a straight rewrite. A `Component` field cannot be “registers 633
and 691”. You would split them into two integers plus a stateful `@property` — and that state (last
10 high words) lives in `InverterState` today, not in the codec.

Packed settings (prog charge/mode, peak shaving on 280, weekday bits on 146) map cleanly onto `bit`
/ `bits`. That is the one place the new model is a strict upgrade.

`ManualComponent` is closer to `SensorDefinitions` (add by key at runtime) but still
consecutive-register fields, still no history, still not per-tick subset polling unless you
`add`/`remove` every cycle and throw away the cached plan.

`restrict_fields` reshapes a static layout for firmware holes. The add-on rebuilds the read set
every second from schedules.

## Class layout

Do **not** keep a driver subclass per backend, and do **not** wrap `ModbusConnection` with a
Solarman subclass.

- **`ModbusConnection`**: owner-held link. Only the add-on (or `from_url`) constructs and closes it.
- **`HoldingUnit`**: tiny protocol — `read_holding_registers(address, count)`,
  `write_registers(address, values)`, `connected`. Avoids the full `ModbusUnit` surface on Solarman.
- **`Sunsynk`**: concrete device class. Holds a unit, `InverterState`, and `group_sensors`. Owns the
  connection only when built via `from_url`.
- **`SolarmanUnit`**: `HoldingUnit` over `PySolarmanV5Async`. Not a `Sunsynk` subclass. Solarman is
  a proprietary V5 tunnel with the same holding-register ops; that is a stronger reason to adopt a
  unit protocol than to rewrite sensors.

tmodbus vs pymodbus is an import of `ModbusConnection`, not a Sunsynk type. `serial-udp`
(RTU-over-UDP) is unsupported by tmodbus.

```python
conn = ModbusConnection(ModbusTcpParams(host="192.168.1.50", port=502))
unit = conn.for_unit(1)  # server_id / MODBUS_ID

regs = await unit.read_holding_registers(175, 3)  # FC03, any start, any length
await unit.write_registers(430, [1])              # FC16

ss = Sunsynk(unit=unit)
# or: Sunsynk.from_url("tcp://192.168.1.50:502", server_id=1)
```

Two inverters on one adapter: one connection, two units — no swapping `server_id`.

## What stays in sunsynk

| Keep                                    | Why                                                                                      |
| --------------------------------------- | ---------------------------------------------------------------------------------------- |
| `Sensor` / definitions / `mysensors.py` | Public API and the Deye map                                                              |
| `group_sensors`                         | Same job as Component `max_gap` / `max_span`, but over a dynamic subset                  |
| `InverterState`                         | Raw regs for bitmask writes; history for MQTT; `onchange` for discovery; RW dependencies |
| Schedules / MQTT                        | Application layer; Component `_values` is only “last poll”                               |

## If Components come later

Same package, after the unit underlay is in. Group by Deye block (Battery, Grid, Load, Settings).
`repeating_group` fits Prog1–6. Then either wrap each `Sensor` around a field, or make Components
the source of truth and keep `Sensor` as the HA/mysensors view.

`MathSensor` / `Sensor16` / `FaultSensor` / `SystemTimeRWSensor` stay as properties or custom
converters. Do not migrate decode and transport at once.

Identity (regs 0–7: device type, protocol, serial) is already a `Component`
(`sunsynk.identity.Identity`); scheduled polls stay on `Sensor` + `group_sensors`.

## Sequence

1. `Sunsynk` holds a `HoldingUnit`; I/O delegates; FC16 stays.
2. `from_url` builds `ModbusConnection` (tmodbus) from the existing port schemes.
3. `SolarmanUnit` over `PySolarmanV5Async`.
4. Add-on: one connection per port, `for_unit` per inverter; delete `server_id` mutation and the
   extra lock.
5. Optional later: one sub-system as a `Component` (Battery is the smallest spike).
