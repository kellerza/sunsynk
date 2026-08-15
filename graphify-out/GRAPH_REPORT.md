# Graph Report - sunsynk  (2026-08-15)

## Corpus Check
- 111 files · ~232,707 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 992 nodes · 1872 edges · 86 communities (74 shown, 12 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 92 edges (avg confidence: 0.54)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c548e67a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- utils/__init__.py
- package.json
- sunsynk.py
- Adaptors & Wiring
- sensors.py
- Sunsynk
- compilerOptions
- test_a_inverter.py
- BinarySensor
- RegType
- percentile
- a_inverter.py
- __main__.py
- HoldingUnit
- RWSensor
- RegType
- Sensor
- SolarmanUnit
- ASensor
- test_connection.py
- test_sunsynk.py
- AInverter
- .get
- test_helpers.py
- Groups of sensors
- InverterState
- .read_sensors
- definitions.md
- ensure_tuple
- tests/conftest.py
- Run standalone using docker compose
- Sensors
- .significant_change
- Available addons
- Configuration
- Single-phase register backfill (proposal)
- Unreleased
- NumberRWSensor
- test_options.py
- Inverter Automation
- Deye/Sunsynk Inverters
- .reg_value
- multi-options.md
- Schedules
- Issue related to
- Deye/Sunsynk Inverters
- _reset_near_realtime
- build_prep.sh
- Sunsynk — align with Cursor rules
- Issue related to the Python sunsynk library
- .value_to_reg
- types.d.ts
- Sunsynk User Documentation
- Your environment
- test_versions.py
- Modbus TCP to Modbus RTU Gateway Add-on
- ToggleLogCallback
- Time
- json_view.vue
- run.sh
- hass-addon-sunsynk-edge/DOCS.md
- hass-addon-sunsynk-edge/README.md
- hass-addon-sunsynk-multi/CHANGELOG.md
- hass-addon-sunsynk-multi/DOCS.md
- hass-addon-sunsynk-multi/README.md
- tests/README.md
- templates.md
- NearRealtime
- copy2local.sh
- .create_entity
- .reg_to_value
- .publish
- as_num
- three_phase_common.py

## God Nodes (most connected - your core abstractions)
1. `Sensor` - 91 edges
2. `InverterState` - 71 edges
3. `AInverter` - 43 edges
4. `RWSensor` - 34 edges
5. `ASensor` - 31 edges
6. `NumberRWSensor` - 29 edges
7. `Sunsynk` - 28 edges
8. `SensorDefinitions` - 23 edges
9. `Schedule` - 21 edges
10. `slug()` - 21 edges

## Surprising Connections (you probably didn't know these)
- `generate_all_sensors()` --references--> `SensorDefinitions`  [EXTRACTED]
  scripts/gen_sensors.py → src/sunsynk/sensors.py
- `generate_all_sensors()` --calls--> `pretty_table()`  [INFERRED]
  scripts/gen_sensors.py → src/sunsynk/utils/pretty_table.py
- `generate_all_sensors()` --calls--> `table_data()`  [INFERRED]
  scripts/gen_sensors.py → src/sunsynk/utils/pretty_table.py
- `generate_group_sensors()` --references--> `SensorDefinitions`  [EXTRACTED]
  scripts/gen_sensors.py → src/sunsynk/sensors.py
- `test_load_env()` --calls--> `Schedule`  [INFERRED]
  src/tests/ha_addon_sunsynk_multi/test_options.py → src/ha_addon_sunsynk_multi/timer_schedule.py

## Import Cycles
- 3-file cycle: `src/sunsynk/sensors.py -> src/sunsynk/utils/pretty_table.py -> src/sunsynk/state.py -> src/sunsynk/sensors.py`
- 4-file cycle: `src/sunsynk/sensors.py -> src/sunsynk/utils/__init__.py -> src/sunsynk/utils/pretty_table.py -> src/sunsynk/state.py -> src/sunsynk/sensors.py`

## Communities (86 total, 12 thin omitted)

### Community 0 - "utils/__init__.py"
Cohesion: 0.08
Nodes (34): ModuleType, PrettyTable, generate_all_sensors(), generate_group_sensors(), main(), Generate groups/all.html., Shorten the definition name., Generate groups/{name}.yml. (+26 more)

### Community 1 - "package.json"
Cohesion: 0.04
Nodes (45): clipboard, @iconify-json/mdi, js-yaml, markdown-it-deflist, markdown-it-imsize, sitemap-ts, @types/node, unplugin-icons (+37 more)

### Community 2 - "sunsynk.py"
Cohesion: 0.18
Nodes (11): group_sensors(), Group sensor registers into blocks for reading., Turn the registers into a dictionary or map., register_map(), Sunsync Modbus interface., Read a list of sensors - Sunsynk supports function code 0x03., Calculate amount of unused registers in this grouping., test_all_groups() (+3 more)

### Community 3 - "Adaptors & Wiring"
Cohesion: 0.06
Nodes (31): (A) Cabling & connection, (B) Configuration, (C) Reducing timeouts, Check line voltage / termination resistor, Check the Modbus Server ID, Direct serial, Fault finding, Only a single connection to the serial port (+23 more)

### Community 4 - "sensors.py"
Cohesion: 0.12
Nodes (28): Sunsynk 5kW&8kW hybrid inverter sensor definitions., ensure_slugs(), FaultSensor, HVFaultSensor, InverterStateSensor, MathSensor, Sensor classes represent modbus registers for an inverter., Sensor with a 16-bit/32-bit register registers. (+20 more)

### Community 5 - "Sunsynk"
Cohesion: 0.08
Nodes (28): MQTTOptions, create_sunsynk(), init_driver(), ModbusConnection, ValType, Init Sunsynk driver for each inverter., React to sensor updates., One ``ModbusConnection`` per port; reused across MODBUS_IDs. (+20 more)

### Community 6 - "compilerOptions"
Cohesion: 0.06
Nodes (30): docs/.vitepress/build_sitemap.ts, docs/.vitepress/**/*.ts, docs/.vitepress/**/*.vue, dom, dom.iterable, esnext, node_modules, ./node_modules/@types (+22 more)

### Community 7 - "test_a_inverter.py"
Cohesion: 0.14
Nodes (23): ExceptionGroup, compact_exception_group(), Compact exception group., InverterOptions, Options for an inverter., import_definitions(), Load definitions according to options., _ist() (+15 more)

### Community 8 - "BinarySensor"
Cohesion: 0.18
Nodes (11): BinarySensor, test_binary_sensor(), Sunsynk sensor state., Test history with numeric values., Test if we have a ValueError., Test history with non-numeric values., Test history with non-numeric values., test_history() (+3 more)

### Community 9 - "RegType"
Cohesion: 0.12
Nodes (14): RegType, ValType, Return the constant value., Return the value from the registers., Reg to value for binary., Decode the temperature (offset)., Decode the SD card status., Decode the inverter status. (+6 more)

### Community 10 - "percentile"
Cohesion: 0.10
Nodes (25): percentile(), Statistics utilities., Calculate the given percentile of the data., parametrize, Tests for sunsynk.utils.stats., Percentile must be 0..100 inclusive., 0 and 100 return min and max., One value: any valid percentile returns that value. (+17 more)

### Community 11 - "a_inverter.py"
Cohesion: 0.11
Nodes (19): MQTT switch: publish every W reading for 10 minutes (#401)., Near-realtime MQTT publish mode for power sensors (#401)., get_sensors(), Parse sensors from options., A dict of sensors from the configuration., Add a sensor. Keep dependencies for later., Parse options and get the various sensor lists., SensorOptions (+11 more)

### Community 12 - "__main__.py"
Cohesion: 0.11
Nodes (24): Exception, callback_discovery_info(), Update HASS discovery & write RWSensors., log_error(), print_errors(), Print an error message., main_loop(), build_callback_schedule() (+16 more)

### Community 13 - "HoldingUnit"
Cohesion: 0.22
Nodes (6): Protocol, HoldingUnit, Minimal unit surface used by ``Sunsynk`` (ModbusUnit or SolarmanUnit)., Whether the underlying link is up., Read ``count`` holding registers starting at ``address`` (FC03)., Write holding registers starting at ``address`` (FC16).

### Community 14 - "RWSensor"
Cohesion: 0.15
Nodes (18): Entity definition for the timeout sensor., TimeoutState, Sunsynk/Deye hybrid 3-phase LV inverter sensor definitions., Deals with inverter time format conversion complexities., Initialize from string or register value., SSTime, Sensor classes represent modbus registers for an inverter., Get the available values for this sensor. (+10 more)

### Community 15 - "RegType"
Cohesion: 0.15
Nodes (9): RegType, ValType, Ensure correct parameters., Ensure correct parameters., Reg to value for binary., Get the reg value from a display value, or the current reg value if out of…, Get the reg value from a display value., Decode the time from a register. (+1 more)

### Community 16 - "Sensor"
Cohesion: 0.10
Nodes (15): Self, Get the serial sensor., Get the rated power sensor., Copy the sensor definitions., Return the source of the sensor., Sensor equality is based on the ID only., Sensor, SensorDefinitions (+7 more)

### Community 17 - "SolarmanUnit"
Cohesion: 0.10
Nodes (17): PySolarmanV5Async, Solarman V5 tunnel as a holding-register unit., Write holding registers (FC16)., Holding-register I/O over a Solarman Wi-Fi dongle (not a ModbusConnection)., Validate the dongle serial number., Whether a Solarman client is open., Open the Solarman client if needed., Close the Solarman client. (+9 more)

### Community 18 - "ASensor"
Cohesion: 0.14
Nodes (17): Publish state to HASSH., Initialize the sensors., ASensor, State of a sensor & entity., Addon Sensor state & entity., Return the name of the sensor., Options for a sensor., SensorOption (+9 more)

### Community 19 - "test_connection.py"
Cohesion: 0.05
Nodes (38): ConnectionParams, Architecture: modbus-connection and sunsynk, Class layout, If Components come later, Layers, Modelling mismatch, Add-on, Class layout (+30 more)

### Community 20 - "test_sunsynk.py"
Cohesion: 0.29
Nodes (11): LogCaptureFixture, parametrize, patch, Test sunsynk library., A malformed response must not mix new words with cached registers., Sunsynk with a dummy unit., _ss(), test_ss_read_sensors() (+3 more)

### Community 21 - "AInverter"
Cohesion: 0.15
Nodes (8): AInverter, ValType, Write to the Modbus interface., Return the inverter power., Create discovery info for the inverter., Discover all sensors., Addon Inverter state (per inverter)., MQTT topic: ``online`` / ``offline`` reflect poll-loop lifecycle (retained).

### Community 22 - ".get"
Cohesion: 0.20
Nodes (6): NumType, ValType, Return the average of the history., Get the current value of a sensor., Get the current value of a sensor., Resolve a number helper.

### Community 23 - "test_helpers.py"
Cohesion: 0.12
Nodes (25): hex_str(), int_round(), pack_value(), NumType, RegType, Convert register values to hex strings., Pack a value into register format. Args: value: The value to pack bits: Number…, Unpack register value(s) into an integer. Args: regs: Register values (1 or 2… (+17 more)

### Community 24 - "Groups of sensors"
Cohesion: 0.18
Nodes (11): All sensors, Battery, Diagnostics, Energy management, Generator, Groups of sensors, My Sensors, Parallel (+3 more)

### Community 25 - "InverterState"
Cohesion: 0.13
Nodes (19): Get the available values for this sensor., Get a list of sensors upon which this sensor depends., TimeRWSensor, InverterState, Keep the state of the inverter., Add a sensor to be tracked., Get a generator of all sensors., LogCaptureFixture (+11 more)

### Community 26 - ".read_sensors"
Cohesion: 0.21
Nodes (7): AInverterLifecycle, Start or extend stale quiet: refresh deadline, set lifecycle, and log., Handle stale quiet or run a serial probe when quiet has elapsed., Return whether the last read left the serial register matching config., Read from the Modbus interface., Read sensors with a retry., Publish retained lifecycle availability (no-op if MQTT is not connected).

### Community 27 - "definitions.md"
Cohesion: 0.14
Nodes (9): Lovelace examples, Power Distribution card, Example #1, Example #2, System settings card, Sunsynk Power Flow Card, Energy Management, Home Assistant (+1 more)

### Community 28 - "ensure_tuple"
Cohesion: 0.20
Nodes (6): ensure_tuple(), T, Post-initialization processing., Ensure correct parameters., Ensure correct parameters., test_ensure_tuple()

### Community 29 - "tests/conftest.py"
Cohesion: 0.18
Nodes (11): Config, Item, Any, fixture, pytest_addoption(), pytest_collection_modifyitems(), pytest_configure(), Support command line marks. (+3 more)

### Community 30 - "Run standalone using docker compose"
Cohesion: 0.17
Nodes (12): amd64 / aarch64 / armv6 / armv7, CLI: amd64 / aarch64 / armv6 / armv7, Docker CLI examples, Docker-Compose examples, Example Configuration, Explanation of Environment Variables, Local Docker-Compose Builds, Mbusd (+4 more)

### Community 31 - "Sensors"
Cohesion: 0.50
Nodes (4): Adding sensors, Available sensors, Sensor definitions, Sensors

### Community 33 - "Available addons"
Cohesion: 0.20
Nodes (8): ESP add-on, Available addons, EskomSePush Add-on, Getting Started, Installation, Modbus TCP to Modbus RTU Gateway Add-on, Sunsynk/Deye Inverter Add-on (edge/dev), Sunsynk/Deye Inverter Add-on (multi)

### Community 34 - "Configuration"
Cohesion: 0.20
Nodes (10): Configuration, Connection, Debug options, Home Assistant Discovery options, Inverters, MQTT Settings, Port, Schedules (+2 more)

### Community 35 - "Single-phase register backfill (proposal)"
Cohesion: 0.22
Nodes (8): Background, Conflicts (verify before changing), Deye BMS block (large, separate effort), High value, Lower priority / per-phase & generator, Proposed additions, Single-phase register backfill (proposal), Suggested order of work

### Community 36 - "Unreleased"
Cohesion: 0.20
Nodes (9): Add-on behaviour, Changelog, Diagnostics and library, Docs and repo hygiene, GitHub issues (in progress), Internal / developer, Major changes, Sensor definitions (+1 more)

### Community 37 - "NumberRWSensor"
Cohesion: 0.17
Nodes (10): Sunsynk / Deye 16kW hybrid inverter sensor definitions., NumberRWSensor, Numeric sensor which can be read and written., Get a list of sensors upon which this sensor depends., Constant, Sensor that always returns a constant value., Test update and on_change., test_on_changed() (+2 more)

### Community 38 - "test_options.py"
Cohesion: 0.25
Nodes (5): patch, Legacy DRIVER / serial:// / tcp+dongle migrate via PORT schemes., test_legacy_port_migration(), test_load_env(), test_unique()

### Community 39 - "Inverter Automation"
Cohesion: 0.22
Nodes (7): Battery charging to optimise Time-of-Use tariffs, Charge the battery in case of low forecast, Detecting power failures / Load shedding, Inverter Automation, Load Limit, Config packages, Home Assistant Examples

### Community 40 - "Deye/Sunsynk Inverters"
Cohesion: 0.25
Nodes (6): [Overview](./overview), Alternatives, Credits, Deye/Sunsynk Inverters, Home Assistant Sunsynk Add-On, Sunsynk Python Library

### Community 41 - ".reg_value"
Cohesion: 0.29
Nodes (5): setter, Get the register value., Convert from a register value., Get the value in hh:mm format., Parse a string in hh:mm format.

### Community 42 - "multi-options.md"
Cohesion: 0.18
Nodes (7): Deployment options, mbusd, Creating your own sensor, Custom/My Sensors, Example: Simple division, Example: Time sensor, Using the sensor

### Community 43 - "Schedules"
Cohesion: 0.25
Nodes (6): Keys, Near realtime (power), Proposed schedule overrides for Solarman, Schedule entries, Schedules, Sensor modifiers

### Community 44 - "Issue related to"
Cohesion: 0.33
Nodes (5): Describe the issue/bug, Issue related to, Logs, Your configuration, Your environment

### Community 45 - "Deye/Sunsynk Inverters"
Cohesion: 0.33
Nodes (5): Deye/Sunsynk Inverters, Documentation, Home Assistant Sunsynk Add-On, Installation, Sunsynk Python Library

### Community 46 - "_reset_near_realtime"
Cohesion: 0.67
Nodes (3): fixture, Reset near-realtime flag and cancel any auto-off task., _reset_near_realtime()

### Community 47 - "build_prep.sh"
Cohesion: 0.40
Nodes (4): ADDON, PACKAGE, build_prep.sh script, VER

### Community 48 - "Sunsynk — align with Cursor rules"
Cohesion: 0.40
Nodes (4): Conflicts, Current rule files (index), Sunsynk — align with Cursor rules, What to do

### Community 49 - "Issue related to the Python sunsynk library"
Cohesion: 0.40
Nodes (4): Describe the issue/bug, Expected behavior, Issue related to the Python sunsynk library, Logs (if applicable)

### Community 50 - ".value_to_reg"
Cohesion: 0.29
Nodes (4): Get the reg value from a display value, or the current reg value if out of…, Get the reg value from a display value., Check the registers are within the bitmask., Get the reg value from a display value.

### Community 51 - "types.d.ts"
Cohesion: 0.40
Nodes (4): imsize_plugin, JsonViewer, markdown-it-imsize, vue3-json-viewer

### Community 52 - "Sunsynk User Documentation"
Cohesion: 0.40
Nodes (4): Contributions, Local testing, Overview, Sunsynk User Documentation

### Community 53 - "Your environment"
Cohesion: 0.50
Nodes (3): Describe the issue/bug and what you expect, Logs (if applicable), Your environment

### Community 55 - "test_versions.py"
Cohesion: 0.67
Nodes (3): _get_version(), Test versions. config.json - contains the HASS addon version setup.py - sunsynk…, test_versions()

### Community 57 - "ToggleLogCallback"
Cohesion: 0.24
Nodes (6): Set log level to critical, and reset after duration., Toggle the log level., Toggle the log level to critical for a short time, to suppress expected errors., Calculate the next run times., Return next run seconds of entry 0., ToggleLogCallback

### Community 58 - "Time"
Cohesion: 0.50
Nodes (4): register_structure_hook, Convert a string to a Time., time_structure_hook(), Time

### Community 70 - "NearRealtime"
Cohesion: 0.40
Nodes (4): NearRealtime, Mutable near-realtime flag and auto-off timer., Enable or disable near-realtime publish mode. When enabled, starts a timer that…, Sleep then clear near-realtime and notify MQTT.

### Community 79 - "copy2local.sh"
Cohesion: 0.67
Nodes (6): copy_addon(), copy_builder(), copy_sunsynk(), print(), rsync_excl(), copy2local.sh script

### Community 80 - ".create_entity"
Cohesion: 0.25
Nodes (4): MQTTEntity, Return True if the units are a measurement., Is entity visible on this inverter., MQTT entities for stats.

### Community 82 - ".publish"
Cohesion: 0.40
Nodes (3): ValType, Return the last value., Set the value through MQTT.

### Community 83 - "as_num"
Cohesion: 0.40
Nodes (5): as_num(), ValType, LogCaptureFixture, Test as_num function., test_as_num()

### Community 88 - "three_phase_common.py"
Cohesion: 0.21
Nodes (7): Sunsynk 5kW&8kW hybrid 3-phase inverter sensor definitions., Sunsynk/Deye hybrid 3-phase high voltage (HV) inverter sensor definitions., EnumSensor, ProtocolVersionSensor, Sensor with a set of enum values. Like a read-only SelectRWSensor., Get the available values for this sensor., Protocol version sensor.

## Knowledge Gaps
- **200 isolated node(s):** `build_prep.sh script`, `ADDON`, `VER`, `PACKAGE`, `run.sh script` (+195 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Sensor` connect `Sensor` to `utils/__init__.py`, `sunsynk.py`, `sensors.py`, `Sunsynk`, `BinarySensor`, `RegType`, `a_inverter.py`, `__main__.py`, `HoldingUnit`, `RWSensor`, `ASensor`, `test_sunsynk.py`, `.get`, `test_helpers.py`, `InverterState`, `.read_sensors`, `ensure_tuple`, `NumberRWSensor`, `three_phase_common.py`?**
  _High betweenness centrality (0.110) - this node is a cross-community bridge._
- **Why does `InverterState` connect `InverterState` to `utils/__init__.py`, `sunsynk.py`, `sensors.py`, `NumberRWSensor`, `Sunsynk`, `test_a_inverter.py`, `BinarySensor`, `a_inverter.py`, `HoldingUnit`, `RWSensor`, `RegType`, `Sensor`, `.value_to_reg`, `test_connection.py`, `test_sunsynk.py`, `AInverter`, `.get`, `tests/conftest.py`?**
  _High betweenness centrality (0.076) - this node is a cross-community bridge._
- **Why does `AInverter` connect `AInverter` to `Sunsynk`, `test_a_inverter.py`, `percentile`, `a_inverter.py`, `__main__.py`, `RWSensor`, `ASensor`, `InverterState`, `.read_sensors`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Are the 15 inferred relationships involving `Sensor` (e.g. with `SensorOption` and `SensorOptions`) actually correct?**
  _`Sensor` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `InverterState` (e.g. with `AInverter` and `NumberRWSensor`) actually correct?**
  _`InverterState` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `AInverter` (e.g. with `ASensor` and `InverterOptions`) actually correct?**
  _`AInverter` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `RWSensor` (e.g. with `AInverter` and `ASensor`) actually correct?**
  _`RWSensor` has 11 INFERRED edges - model-reasoned connections that need verification._