# Graph Report - sunsynk (2026-08-15)

## Corpus Check

- 109 files · ~231,763 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary

- 969 nodes · 1826 edges · 77 communities (65 shown, 12 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 92 edges (avg confidence: 0.54)
- Token cost: 0 input · 0 output

## Graph Freshness

- Built from commit: `6fcc39bb`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)

- SensorDefinitions
- package.json
- Sensor
- Adaptors & Wiring
- sensors.py
- driver.py
- compilerOptions
- test_a_inverter.py
- InverterState
- test_helpers.py
- percentile
- sensor_options.py
- a_inverter.py
- HoldingUnit
- RWSensor
- RegType
- .read_sensors
- SolarmanUnit
- ASensor
- test_connection.py
- Sunsynk
- AInverter
- .get
- Architecture: modbus-connection and sunsynk
- Groups of sensors
- ToggleLogCallback
- ModbusUnit underlay
- definitions.md
- .create_entity
- tests/conftest.py
- Run standalone using docker compose
- .from_url
- test_write_register_timeout
- Available addons
- Configuration
- Single-phase register backfill (proposal)
- Unreleased
- sunsynk.py
- test_options.py
- Inverter Automation
- Deye/Sunsynk Inverters
- .reg_value
- multi-options.md
- Schedules
- Issue related to
- Deye/Sunsynk Inverters
- build_prep.sh
- Sunsynk — align with Cursor rules
- Issue related to the Python sunsynk library
- Custom/My Sensors
- types.d.ts
- Sunsynk User Documentation
- Your environment
- test_versions.py
- Modbus TCP to Modbus RTU Gateway Add-on
- json_view.vue
- run.sh
- hass-addon-sunsynk-edge/DOCS.md
- hass-addon-sunsynk-edge/README.md
- hass-addon-sunsynk-multi/CHANGELOG.md
- hass-addon-sunsynk-multi/DOCS.md
- hass-addon-sunsynk-multi/README.md
- tests/README.md
- templates.md
- copy2local.sh

## God Nodes (most connected - your core abstractions)

1. `Sensor` - 89 edges
2. `InverterState` - 71 edges
3. `AInverter` - 41 edges
4. `RWSensor` - 34 edges
5. `ASensor` - 31 edges
6. `NumberRWSensor` - 29 edges
7. `Sunsynk` - 28 edges
8. `SensorDefinitions` - 23 edges
9. `slug()` - 20 edges
10. `SelectRWSensor` - 20 edges

## Surprising Connections (you probably didn't know these)

- `generate_all_sensors()` --calls--> `pretty_table()` [INFERRED] scripts/gen_sensors.py →
  src/sunsynk/utils/pretty_table.py
- `generate_all_sensors()` --calls--> `table_data()` [INFERRED] scripts/gen_sensors.py →
  src/sunsynk/utils/pretty_table.py
- `test_load_env()` --calls--> `Schedule` [INFERRED]
  src/tests/ha_addon_sunsynk_multi/test_options.py → src/ha_addon_sunsynk_multi/timer_schedule.py
- `main()` --calls--> `import_all_defs()` [EXTRACTED] scripts/gen_sensors.py →
  src/sunsynk/definitions/**init**.py
- `generate_all_sensors()` --references--> `SensorDefinitions` [EXTRACTED] scripts/gen_sensors.py →
  src/sunsynk/sensors.py

## Import Cycles

- 3-file cycle:
  `src/sunsynk/sensors.py -> src/sunsynk/utils/pretty_table.py -> src/sunsynk/state.py -> src/sunsynk/sensors.py`
- 4-file cycle:
  `src/sunsynk/sensors.py -> src/sunsynk/utils/__init__.py -> src/sunsynk/utils/pretty_table.py -> src/sunsynk/state.py -> src/sunsynk/sensors.py`

## Communities (77 total, 12 thin omitted)

### Community 0 - "SensorDefinitions"

Cohesion: 0.06 Nodes (39): ModuleType, PrettyTable, generate_all_sensors(),
generate_group_sensors(), main(), Generate groups/all.html., Shorten the definition name., Generate
groups/{name}.yml. (+31 more)

### Community 1 - "package.json"

Cohesion: 0.04 Nodes (45): clipboard, @iconify-json/mdi, js-yaml, markdown-it-deflist,
markdown-it-imsize, sitemap-ts, @types/node, unplugin-icons (+37 more)

### Community 2 - "Sensor"

Cohesion: 0.08 Nodes (32): Constant, ProtocolVersionSensor, Sensor that always returns a constant
value., Sensor with a 16-bit/32-bit register registers., Decode the inverter serial number.,
Protocol version sensor., Return the source of the sensor., Sensor equality is based on the ID only.
(+24 more)

### Community 3 - "Adaptors & Wiring"

Cohesion: 0.06 Nodes (31): (A) Cabling & connection, (B) Configuration, (C) Reducing timeouts, Check
line voltage / termination resistor, Check the Modbus Server ID, Direct serial, Fault finding, Only
a single connection to the serial port (+23 more)

### Community 4 - "sensors.py"

Cohesion: 0.12 Nodes (25): Sunsynk / Deye 16kW hybrid inverter sensor definitions., Sunsynk 5kW&8kW
hybrid inverter sensor definitions., Sunsynk 5kW&8kW hybrid 3-phase inverter sensor definitions.,
Sunsynk/Deye hybrid 3-phase high voltage (HV) inverter sensor definitions., Sunsynk/Deye hybrid
3-phase LV inverter sensor definitions., BinarySensor, EnumSensor, FaultSensor (+17 more)

### Community 5 - "driver.py"

Cohesion: 0.11 Nodes (23): MQTTOptions, register_structure_hook, create_sunsynk(), init_driver(),
ModbusConnection, ValType, Init Sunsynk driver for each inverter., React to sensor updates. (+15
more)

### Community 6 - "compilerOptions"

Cohesion: 0.06 Nodes (30): docs/.vitepress/build_sitemap.ts,
docs/.vitepress/**/*.ts, docs/.vitepress/**/*.vue, dom, dom.iterable, esnext, node_modules,
./node_modules/@types (+22 more)

### Community 7 - "test_a_inverter.py"

Cohesion: 0.12 Nodes (26): ExceptionGroup, get_root(), import_mysensors(), Any, Path, Get the root
folder for data and mysensors., InverterOptions, Options for an inverter. (+18 more)

### Community 8 - "InverterState"

Cohesion: 0.09 Nodes (33): NumberRWSensor, Read & write time sensor., Numeric sensor which can be
read and written., Get a list of sensors upon which this sensor depends., SystemTimeRWSensor,
InverterState, Keep the state of the inverter., Add a sensor to be tracked. (+25 more)

### Community 9 - "test_helpers.py"

Cohesion: 0.05 Nodes (44): ensure_tuple(), int_round(), pack_value(), NumType, RegType, T, Pack a
value into register format. Args: value: The value to pack bits: Number…, Unpack register value(s)
into an integer. Args: regs: Register values (1 or 2… (+36 more)

### Community 10 - "percentile"

Cohesion: 0.10 Nodes (25): percentile(), Statistics utilities., Calculate the given percentile of
the data., parametrize, Tests for sunsynk.utils.stats., Percentile must be 0..100 inclusive., 0 and
100 return min and max., One value: any valid percentile returns that value. (+17 more)

### Community 11 - "sensor_options.py"

Cohesion: 0.13 Nodes (15): get_sensors(), Parse sensors from options., A dict of sensors from the
configuration., Add a sensor. Keep dependencies for later., Parse options and get the various sensor
lists., SensorOptions, get_schedule(), init_schedules() (+7 more)

### Community 12 - "a_inverter.py"

Cohesion: 0.14 Nodes (20): Exception, callback_discovery_info(), Update HASS discovery & write
RWSensors., log_error(), print_errors(), Print an error message., main_loop(),
build_callback_schedule() (+12 more)

### Community 13 - "HoldingUnit"

Cohesion: 0.18 Nodes (7): Protocol, HoldingUnit, Minimal unit surface used by ``Sunsynk``
(ModbusUnit or SolarmanUnit)., Whether the underlying link is up., Read ``count`` holding registers
starting at ``address`` (FC03)., Write holding registers starting at ``address`` (FC16)., Write to a
register - Sunsynk support function code 0x10.

### Community 14 - "RWSensor"

Cohesion: 0.15 Nodes (19): State of a sensor & entity., Entity definition for the timeout sensor.,
TimeoutState, Deals with inverter time format conversion complexities., Initialize from string or
register value., SSTime, Sensor classes represent modbus registers for an inverter., Get the
available values for this sensor. (+11 more)

### Community 15 - "RegType"

Cohesion: 0.12 Nodes (13): RegType, ValType, Get the reg value from a display value, or the current
reg value if out of…, Ensure correct parameters., Ensure correct parameters., Reg to value for
binary., Get the reg value from a display value, or the current reg value if out of…, Get the reg
value from a display value. (+5 more)

### Community 16 - ".read_sensors"

Cohesion: 0.17 Nodes (9): AInverterLifecycle, compact_exception_group(), Start or extend stale
quiet: refresh deadline, set lifecycle, and log., Handle stale quiet or run a serial probe when
quiet has elapsed., Return whether the last read left the serial register matching config., Read
from the Modbus interface., Read sensors with a retry., Compact exception group. (+1 more)

### Community 17 - "SolarmanUnit"

Cohesion: 0.10 Nodes (17): PySolarmanV5Async, Solarman V5 tunnel as a holding-register unit., Write
holding registers (FC16)., Holding-register I/O over a Solarman Wi-Fi dongle (not a
ModbusConnection)., Validate the dongle serial number., Whether a Solarman client is open., Open the
Solarman client if needed., Close the Solarman client. (+9 more)

### Community 18 - "ASensor"

Cohesion: 0.13 Nodes (18): Initialize the sensors., ASensor, ValType, Addon Sensor state & entity.,
Return the last value., Set the value through MQTT., Return the name of the sensor., SensorRun (+10
more)

### Community 19 - "test_connection.py"

Cohesion: 0.17 Nodes (14): ConnectionParams, open_connection(), ModbusConnection, Build a
``ModbusConnection`` from the add-on / library port URL schemes., Map a port URL (or serial device
path) to connection params., Create a tmodbus ``ModbusConnection`` for ``port`` (does not connect
yet)., url_to_params(), Connection URL helpers and Sunsynk.from_url. (+6 more)

### Community 20 - "Sunsynk"

Cohesion: 0.20 Nodes (14): Sunsync inverter reached through a holding-register unit., Connect the
owned link, or a unit that implements ``connect`` (Solarman)., Sunsynk, LogCaptureFixture,
parametrize, patch, Test sunsynk library., A malformed response must not mix new words with cached
registers. (+6 more)

### Community 21 - "AInverter"

Cohesion: 0.14 Nodes (9): AInverter, ValType, Write to the Modbus interface., Publish state to
HASSH., Return the inverter power., Create discovery info for the inverter., Discover all sensors.,
Addon Inverter state (per inverter). (+1 more)

### Community 22 - ".get"

Cohesion: 0.14 Nodes (11): as_num(), ValType, NumType, ValType, Return the average of the history.,
Get the current value of a sensor., Get the current value of a sensor., Resolve a number helper. (+3
more)

### Community 23 - "Architecture: modbus-connection and sunsynk"

Cohesion: 0.18 Nodes (9): Architecture: modbus-connection and sunsynk, Class layout, If Components
come later, Layers, Modelling mismatch, Sequence, What hurts today, What stays in sunsynk (+1 more)

### Community 24 - "Groups of sensors"

Cohesion: 0.13 Nodes (15): Adding sensors, All sensors, Available sensors, Battery, Diagnostics,
Energy management, Generator, Groups of sensors (+7 more)

### Community 25 - "ToggleLogCallback"

Cohesion: 0.24 Nodes (6): Set log level to critical, and reset after duration., Toggle the log
level., Toggle the log level to critical for a short time, to suppress expected errors., Calculate
the next run times., Return next run seconds of entry 0., ToggleLogCallback

### Community 26 - "ModbusUnit underlay"

Cohesion: 0.20 Nodes (10): Add-on, Class layout, Construction, `for_unit` is the server id, Library
files, ModbusUnit underlay, Out of scope, Reading an arbitrary holding-register block (+2 more)

### Community 27 - "definitions.md"

Cohesion: 0.14 Nodes (9): Lovelace examples, Power Distribution card, Example #1, Example #2, System
settings card, Sunsynk Power Flow Card, Energy Management, Home Assistant (+1 more)

### Community 28 - ".create_entity"

Cohesion: 0.25 Nodes (4): MQTTEntity, Return True if the units are a measurement., Is entity visible
on this inverter., MQTT entities for stats.

### Community 29 - "tests/conftest.py"

Cohesion: 0.18 Nodes (11): Config, fixture, Item, Any, pytest_addoption(),
pytest_collection_modifyitems(), pytest_configure(), Support command line marks. (+3 more)

### Community 30 - "Run standalone using docker compose"

Cohesion: 0.17 Nodes (12): amd64 / aarch64 / armv6 / armv7, CLI: amd64 / aarch64 / armv6 / armv7,
Docker CLI examples, Docker-Compose examples, Example Configuration, Explanation of Environment
Variables, Local Docker-Compose Builds, Mbusd (+4 more)

### Community 31 - ".from_url"

Cohesion: 0.50 Nodes (3): Create a ``Sunsynk`` that owns a tmodbus connection for ``port``.,
Sunsynk.from_url owns a connection; I/O goes through the unit., test_from_url_mock_unit()

### Community 33 - "Available addons"

Cohesion: 0.20 Nodes (8): ESP add-on, Available addons, EskomSePush Add-on, Getting Started,
Installation, Modbus TCP to Modbus RTU Gateway Add-on, Sunsynk/Deye Inverter Add-on (edge/dev),
Sunsynk/Deye Inverter Add-on (multi)

### Community 34 - "Configuration"

Cohesion: 0.20 Nodes (10): Configuration, Connection, Debug options, Home Assistant Discovery
options, Inverters, MQTT Settings, Port, Schedules (+2 more)

### Community 35 - "Single-phase register backfill (proposal)"

Cohesion: 0.22 Nodes (8): Background, Conflicts (verify before changing), Deye BMS block (large,
separate effort), High value, Lower priority / per-phase & generator, Proposed additions,
Single-phase register backfill (proposal), Suggested order of work

### Community 36 - "Unreleased"

Cohesion: 0.22 Nodes (8): Add-on behaviour, Changelog, Diagnostics and library, Docs and repo
hygiene, GitHub issues (in progress), Internal / developer, Sensor definitions, Unreleased

### Community 37 - "sunsynk.py"

Cohesion: 0.20 Nodes (9): hex_str(), patch_bitmask(), Convert register values to hex strings.,
Combine bitmask values., Turn the registers into a dictionary or map., register_map(), ValType,
Sunsync Modbus interface. (+1 more)

### Community 38 - "test_options.py"

Cohesion: 0.25 Nodes (5): patch, Legacy DRIVER / serial:// / tcp+dongle migrate via PORT schemes.,
test_legacy_port_migration(), test_load_env(), test_unique()

### Community 39 - "Inverter Automation"

Cohesion: 0.22 Nodes (7): Battery charging to optimise Time-of-Use tariffs, Charge the battery in
case of low forecast, Detecting power failures / Load shedding, Inverter Automation, Load Limit,
Config packages, Home Assistant Examples

### Community 40 - "Deye/Sunsynk Inverters"

Cohesion: 0.25 Nodes (6): [Overview](./overview), Alternatives, Credits, Deye/Sunsynk Inverters,
Home Assistant Sunsynk Add-On, Sunsynk Python Library

### Community 41 - ".reg_value"

Cohesion: 0.29 Nodes (5): setter, Get the register value., Convert from a register value., Get the
value in hh:mm format., Parse a string in hh:mm format.

### Community 43 - "Schedules"

Cohesion: 0.29 Nodes (5): Keys, Proposed schedule overrides for Solarman, Schedule entries,
Schedules, Sensor modifiers

### Community 44 - "Issue related to"

Cohesion: 0.33 Nodes (5): Describe the issue/bug, Issue related to, Logs, Your configuration, Your
environment

### Community 45 - "Deye/Sunsynk Inverters"

Cohesion: 0.33 Nodes (5): Deye/Sunsynk Inverters, Documentation, Home Assistant Sunsynk Add-On,
Installation, Sunsynk Python Library

### Community 47 - "build_prep.sh"

Cohesion: 0.40 Nodes (4): ADDON, PACKAGE, build_prep.sh script, VER

### Community 48 - "Sunsynk — align with Cursor rules"

Cohesion: 0.40 Nodes (4): Conflicts, Current rule files (index), Sunsynk — align with Cursor rules,
What to do

### Community 49 - "Issue related to the Python sunsynk library"

Cohesion: 0.40 Nodes (4): Describe the issue/bug, Expected behavior, Issue related to the Python
sunsynk library, Logs (if applicable)

### Community 50 - "Custom/My Sensors"

Cohesion: 0.40 Nodes (5): Creating your own sensor, Custom/My Sensors, Example: Simple division,
Example: Time sensor, Using the sensor

### Community 51 - "types.d.ts"

Cohesion: 0.40 Nodes (4): imsize_plugin, JsonViewer, markdown-it-imsize, vue3-json-viewer

### Community 52 - "Sunsynk User Documentation"

Cohesion: 0.40 Nodes (4): Contributions, Local testing, Overview, Sunsynk User Documentation

### Community 53 - "Your environment"

Cohesion: 0.50 Nodes (3): Describe the issue/bug and what you expect, Logs (if applicable), Your
environment

### Community 55 - "test_versions.py"

Cohesion: 0.67 Nodes (3): _get_version(), Test versions. config.json - contains the HASS addon
version setup.py - sunsynk…, test_versions()

### Community 79 - "copy2local.sh"

Cohesion: 0.67 Nodes (6): copy_addon(), copy_builder(), copy_sunsynk(), print(), rsync_excl(),
copy2local.sh script

## Knowledge Gaps

- **198 isolated node(s):** `build_prep.sh script`, `ADDON`, `VER`, `PACKAGE`, `run.sh script` (+193
  more) These have ≤1 connection - possible missing edges or undocumented components.
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated
  nodes.

## Suggested Questions

_Questions this graph is uniquely positioned to answer:_

- **Why does `Sensor` connect `Sensor` to `SensorDefinitions`, `sensors.py`, `driver.py`,
  `sunsynk.py`, `InverterState`, `test_helpers.py`, `sensor_options.py`, `a_inverter.py`,
  `HoldingUnit`, `RWSensor`, `.read_sensors`, `ASensor`, `Sunsynk`, `.get`?**
  _High betweenness centrality (0.107) - this node is a cross-community bridge._
- **Why does `InverterState` connect `InverterState` to `SensorDefinitions`,
  `test_write_register_timeout`, `Sensor`, `sensors.py`, `sunsynk.py`, `test_a_inverter.py`,
  `a_inverter.py`, `HoldingUnit`, `RWSensor`, `RegType`, `test_connection.py`, `Sunsynk`,
  `AInverter`, `.get`, `tests/conftest.py`, `.from_url`?**
  _High betweenness centrality (0.077) - this node is a cross-community bridge._
- **Why does `AInverter` connect `AInverter` to `driver.py`, `test_a_inverter.py`, `InverterState`,
  `percentile`, `sensor_options.py`, `a_inverter.py`, `RWSensor`, `.read_sensors`, `ASensor`,
  `Sunsynk`?** _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Are the 15 inferred relationships involving `Sensor` (e.g. with `SensorOption` and
  `SensorOptions`) actually correct?**
  _`Sensor` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `InverterState` (e.g. with `AInverter` and
  `NumberRWSensor`) actually correct?**
  _`InverterState` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `AInverter` (e.g. with `ASensor` and
  `InverterOptions`) actually correct?**
  _`AInverter` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `RWSensor` (e.g. with `AInverter` and `ASensor`)
  actually correct?**
  _`RWSensor` has 11 INFERRED edges - model-reasoned connections that need verification._
