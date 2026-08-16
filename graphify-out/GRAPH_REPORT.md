# Graph Report - sunsynk  (2026-08-16)

## Corpus Check
- 114 files · ~233,291 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1018 nodes · 1909 edges · 92 communities (78 shown, 14 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 94 edges (avg confidence: 0.54)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5bc30ad0`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- src/sunsynk/definitions/__init__.py
- package.json
- Sunsynk
- Adaptors & Wiring
- Sensor
- driver.py
- compilerOptions
- test_a_inverter.py
- test_sensors.py
- RegType
- percentile
- utils/__init__.py
- timer_callback.py
- HoldingUnit
- RegType
- RWSensor
- options.py
- SolarmanUnit
- ASensor
- test_connection.py
- NumberRWSensor
- SensorDefinitions
- .get
- test_helpers.py
- Groups of sensors
- InverterState
- AInverter
- definitions.md
- .__post_init__
- tests/conftest.py
- test_state.py
- Sensors
- .significant_change
- Available addons
- Configuration
- Single-phase register backfill (proposal)
- Release 1.0.0
- int_round
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
- a_inverter.py
- types.d.ts
- Sunsynk User Documentation
- Your environment
- test_versions.py
- Modbus TCP to Modbus RTU Gateway Add-on
- .publish
- ensure_str
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
- import_module
- gen_sensors.py
- patch_bitmask
- .value_to_reg
- Run standalone using Docker
- Release
- ensure_slugs
- .available_values
- .source
- .__eq__

## God Nodes (most connected - your core abstractions)
1. `Sensor` - 88 edges
2. `InverterState` - 71 edges
3. `AInverter` - 46 edges
4. `RWSensor` - 34 edges
5. `ASensor` - 31 edges
6. `NumberRWSensor` - 29 edges
7. `Sunsynk` - 28 edges
8. `Schedule` - 21 edges
9. `slug()` - 21 edges
10. `SelectRWSensor` - 20 edges

## Surprising Connections (you probably didn't know these)
- `generate_all_sensors()` --calls--> `pretty_table()`  [INFERRED]
  scripts/gen_sensors.py → src/sunsynk/utils/pretty_table.py
- `generate_all_sensors()` --calls--> `table_data()`  [INFERRED]
  scripts/gen_sensors.py → src/sunsynk/utils/pretty_table.py
- `main()` --calls--> `import_all_defs()`  [EXTRACTED]
  scripts/gen_sensors.py → src/sunsynk/definitions/__init__.py
- `generate_all_sensors()` --references--> `SensorDefinitions`  [EXTRACTED]
  scripts/gen_sensors.py → src/sunsynk/sensors.py
- `generate_group_sensors()` --references--> `SensorDefinitions`  [EXTRACTED]
  scripts/gen_sensors.py → src/sunsynk/sensors.py

## Import Cycles
- 3-file cycle: `src/sunsynk/sensors.py -> src/sunsynk/utils/pretty_table.py -> src/sunsynk/state.py -> src/sunsynk/sensors.py`
- 4-file cycle: `src/sunsynk/sensors.py -> src/sunsynk/utils/__init__.py -> src/sunsynk/utils/pretty_table.py -> src/sunsynk/state.py -> src/sunsynk/sensors.py`

## Communities (92 total, 14 thin omitted)

### Community 0 - "src/sunsynk/definitions/__init__.py"
Cohesion: 0.31
Nodes (8): import_all_defs(), import_defs(), Get all sensor definitions., Test sensor definitions., Test all sensor definitions., Test importing sensors., test_all_defs(), test_import_defs()

### Community 1 - "package.json"
Cohesion: 0.04
Nodes (45): clipboard, @iconify-json/mdi, js-yaml, markdown-it-deflist, markdown-it-imsize, sitemap-ts, @types/node, unplugin-icons (+37 more)

### Community 2 - "Sunsynk"
Cohesion: 0.16
Nodes (10): Exception, Turn the registers into a dictionary or map., register_map(), ValType, Read holding registers (FC03)., Read a list of sensors - Sunsynk supports function code 0x03., Sunsync inverter reached through a holding-register unit., Connect the owned link, or a unit that implements ``connect`` (Solarman). (+2 more)

### Community 3 - "Adaptors & Wiring"
Cohesion: 0.06
Nodes (31): (A) Cabling & connection, (B) Configuration, (C) Reducing timeouts, Check line voltage / termination resistor, Check the Modbus Server ID, Direct serial, Fault finding, Only a single connection to the serial port (+23 more)

### Community 4 - "Sensor"
Cohesion: 0.14
Nodes (27): Sunsynk / Deye 16kW hybrid inverter sensor definitions., Sunsynk 5kW&8kW hybrid inverter sensor definitions., Sunsynk 5kW&8kW hybrid 3-phase inverter sensor definitions., Sunsynk/Deye hybrid 3-phase high voltage (HV) inverter sensor definitions., Sunsynk/Deye hybrid 3-phase LV inverter sensor definitions., Sensor classes represent modbus registers for an inverter., Switch. Similar to BinarySensor, but writeable., SwitchRWSensor (+19 more)

### Community 5 - "driver.py"
Cohesion: 0.18
Nodes (14): MQTTOptions, create_sunsynk(), init_driver(), ModbusConnection, ValType, Init Sunsynk driver for each inverter., React to sensor updates., One ``ModbusConnection`` per port; reused across MODBUS_IDs. (+6 more)

### Community 6 - "compilerOptions"
Cohesion: 0.06
Nodes (30): docs/.vitepress/build_sitemap.ts, docs/.vitepress/**/*.ts, docs/.vitepress/**/*.vue, dom, dom.iterable, esnext, node_modules, ./node_modules/@types (+22 more)

### Community 7 - "test_a_inverter.py"
Cohesion: 0.16
Nodes (21): ExceptionGroup, InverterOptions, Options for an inverter., import_definitions(), Load definitions according to options., _ist(), LogCaptureFixture, Tests for ha_addon_sunsynk_multi.a_inverter. (+13 more)

### Community 8 - "test_sensors.py"
Cohesion: 0.11
Nodes (24): FaultSensor, MathSensor, Sensor with a 16-bit/32-bit register registers., Math sensor, add multiple registers., Decode the inverter serial number., Decode Inverter faults., Sensor16, SerialSensor (+16 more)

### Community 9 - "RegType"
Cohesion: 0.13
Nodes (13): RegType, ValType, Return the constant value., Return the value from the registers., Reg to value for binary., Decode the SD card status., Decode the inverter status., Decode the inverter serial number. (+5 more)

### Community 10 - "percentile"
Cohesion: 0.10
Nodes (25): percentile(), Statistics utilities., Calculate the given percentile of the data., parametrize, Tests for sunsynk.utils.stats., Percentile must be 0..100 inclusive., 0 and 100 return min and max., One value: any valid percentile returns that value. (+17 more)

### Community 11 - "utils/__init__.py"
Cohesion: 0.33
Nodes (8): PrettyTable, Override existing sensors with new definitions., pretty_table(), pretty_table_sensors(), T, Convert a list of dictionaries to a table data format., Generate a pretty table for the given sensors., table_data()

### Community 12 - "timer_callback.py"
Cohesion: 0.09
Nodes (22): callback_discovery_info(), Update HASS discovery & write RWSensors., log_error(), print_errors(), Print an error message., main_loop(), AsyncCallback, Callback (+14 more)

### Community 13 - "HoldingUnit"
Cohesion: 0.22
Nodes (6): Protocol, HoldingUnit, Minimal unit surface used by ``Sunsynk`` (ModbusUnit or SolarmanUnit)., Whether the underlying link is up., Read ``count`` holding registers starting at ``address`` (FC03)., Write holding registers starting at ``address`` (FC16).

### Community 14 - "RegType"
Cohesion: 0.14
Nodes (11): RegType, ValType, Ensure correct parameters., Ensure correct parameters., Reg to value for binary., Get the reg value from a display value, or the current reg value if out of…, Read & write time sensor., Get the reg value from a display value. (+3 more)

### Community 15 - "RWSensor"
Cohesion: 0.14
Nodes (16): State of a sensor & entity., Entity definition for the timeout sensor., TimeoutState, Deals with inverter time format conversion complexities., Initialize from string or register value., SSTime, Get the available values for this sensor., Switch Sensor. The original implementation. (+8 more)

### Community 16 - "options.py"
Cohesion: 0.21
Nodes (10): register_structure_hook, as_solarman_port(), is_solarman_port(), _normalize_legacy_port(), Convert a string to a Time., Check if the port selects the Solarman dongle transport., Strip legacy umodbus ``serial://`` prefix., Rewrite a host URL (or bare host) to ``solarman://host:port``. (+2 more)

### Community 17 - "SolarmanUnit"
Cohesion: 0.10
Nodes (17): PySolarmanV5Async, Solarman V5 tunnel as a holding-register unit., Write holding registers (FC16)., Holding-register I/O over a Solarman Wi-Fi dongle (not a ModbusConnection)., Validate the dongle serial number., Whether a Solarman client is open., Open the Solarman client if needed., Close the Solarman client. (+9 more)

### Community 18 - "ASensor"
Cohesion: 0.17
Nodes (15): Initialize the sensors., ASensor, Addon Sensor state & entity., Return the name of the sensor., Options for a sensor., SensorOption, ist_factory(), Return an inverter test instance. (+7 more)

### Community 19 - "test_connection.py"
Cohesion: 0.05
Nodes (38): ConnectionParams, Architecture: modbus-connection and sunsynk, Class layout, If Components come later, Layers, Modelling mismatch, Add-on, Class layout (+30 more)

### Community 20 - "NumberRWSensor"
Cohesion: 0.18
Nodes (16): NumberRWSensor, Numeric sensor which can be read and written., Get a list of sensors upon which this sensor depends., Test update and on_change., test_on_changed(), LogCaptureFixture, parametrize, patch (+8 more)

### Community 21 - "SensorDefinitions"
Cohesion: 0.17
Nodes (10): Get the rated power sensor., Copy the sensor definitions., SensorDefinitions, String ``alias`` is one alternate name; registry keys match ``slug()`` (config…, Multiple alternate names from a tuple each get a slug key., test_override(), test_override_const(), test_override_many() (+2 more)

### Community 22 - ".get"
Cohesion: 0.14
Nodes (11): as_num(), ValType, NumType, ValType, Return the average of the history., Get the current value of a sensor., Get the current value of a sensor., Resolve a number helper. (+3 more)

### Community 23 - "test_helpers.py"
Cohesion: 0.12
Nodes (23): ensure_tuple(), hex_str(), pack_value(), RegType, T, Convert register values to hex strings., Pack a value into register format. Args: value: The value to pack bits: Number…, Unpack register value(s) into an integer. Args: regs: Register values (1 or 2… (+15 more)

### Community 24 - "Groups of sensors"
Cohesion: 0.18
Nodes (11): All sensors, Battery, Diagnostics, Energy management, Generator, Groups of sensors, My Sensors, Parallel (+3 more)

### Community 25 - "InverterState"
Cohesion: 0.16
Nodes (16): InverterState, Keep the state of the inverter., Add a sensor to be tracked., Get a generator of all sensors., LogCaptureFixture, Sunsynk sensor tests., A time sensor whose window wraps past midnight offers the wrapped slots., test_bad_sensor() (+8 more)

### Community 26 - "AInverter"
Cohesion: 0.05
Nodes (36): AInverterLifecycle, Component, AInverter, compact_exception_group(), ValType, Start or extend stale quiet: refresh deadline, set lifecycle, and log., Handle stale quiet or run a serial probe when quiet has elapsed., Read device type, protocol, and serial via the Identity Component. (+28 more)

### Community 27 - "definitions.md"
Cohesion: 0.14
Nodes (9): Lovelace examples, Power Distribution card, Example #1, Example #2, System settings card, Sunsynk Power Flow Card, Energy Management, Home Assistant (+1 more)

### Community 28 - ".__post_init__"
Cohesion: 0.33
Nodes (3): Post-initialization processing., Ensure correct parameters., Ensure correct parameters.

### Community 29 - "tests/conftest.py"
Cohesion: 0.18
Nodes (11): Config, Item, Any, fixture, pytest_addoption(), pytest_collection_modifyitems(), pytest_configure(), Support command line marks. (+3 more)

### Community 30 - "test_state.py"
Cohesion: 0.20
Nodes (9): Sunsynk sensor state., Test history with numeric values., Test if we have a ValueError., Test history with non-numeric values., Test history with non-numeric values., test_history(), test_history_nn(), test_history_nn_binary() (+1 more)

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

### Community 36 - "Release 1.0.0"
Cohesion: 0.18
Nodes (10): Add-on behaviour, Changelog, Diagnostics and library, Docs and repo hygiene, GitHub issues (in progress), Internal / developer, Major changes, Release 1.0.0 (+2 more)

### Community 37 - "int_round"
Cohesion: 0.29
Nodes (5): int_round(), NumType, Calculate the math value., Decode the temperature (offset)., test_int_round()

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
Cohesion: 0.29
Nodes (6): Deye/Sunsynk Inverters, Documentation, Home Assistant Sunsynk Add-On, Installation, Running outside Home Assistant OS, Sunsynk Python Library

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

### Community 50 - "a_inverter.py"
Cohesion: 0.10
Nodes (25): Near-realtime MQTT publish mode for power sensors (#401)., build_callback_schedule(), Self, Print the sensor schedule., Build the callback schedule., SensorRun, SensorSchedule, get_sensors() (+17 more)

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

### Community 57 - ".publish"
Cohesion: 0.40
Nodes (3): ValType, Return the last value., Set the value through MQTT.

### Community 58 - "ensure_str"
Cohesion: 0.67
Nodes (3): ensure_str(), Any, Ensure a value is a string.

### Community 70 - "NearRealtime"
Cohesion: 0.40
Nodes (4): NearRealtime, Mutable near-realtime flag and auto-off timer., Enable or disable near-realtime publish mode. When enabled, starts a timer that…, Sleep then clear near-realtime and notify MQTT.

### Community 79 - "copy2local.sh"
Cohesion: 0.67
Nodes (6): copy_addon(), copy_builder(), copy_sunsynk(), print(), rsync_excl(), copy2local.sh script

### Community 80 - ".create_entity"
Cohesion: 0.25
Nodes (4): MQTTEntity, Return True if the units are a measurement., Is entity visible on this inverter., MQTT entities for stats.

### Community 81 - "import_module"
Cohesion: 0.28
Nodes (8): ModuleType, get_root(), import_mysensors(), Any, Path, Get the root folder for data and mysensors., import_module(), Path

### Community 82 - "gen_sensors.py"
Cohesion: 0.39
Nodes (7): generate_all_sensors(), generate_group_sensors(), main(), Generate groups/all.html., Shorten the definition name., Generate groups/{name}.yml., simple_def_name()

### Community 83 - "patch_bitmask"
Cohesion: 0.50
Nodes (4): patch_bitmask(), Combine bitmask values., Test patch_bitmask function., test_patch_bitmask()

### Community 85 - ".value_to_reg"
Cohesion: 0.29
Nodes (4): Get the reg value from a display value, or the current reg value if out of…, Get the reg value from a display value., Check the registers are within the bitmask., Get the reg value from a display value.

### Community 86 - "Run standalone using Docker"
Cohesion: 0.25
Nodes (8): Addon configuration — environment variables, Addon configuration — options.yaml, Docker CLI, Environment variable notes, Example docker-compose.yaml, Mbusd configuration — mbusd.conf, Run standalone using Docker, Start the stack

### Community 87 - "Release"
Cohesion: 0.29
Nodes (6): Done message, Implementation notes, Parameter, Preconditions (abort if unmet), Release, Steps

### Community 88 - "ensure_slugs"
Cohesion: 0.40
Nodes (4): ensure_slugs(), Self, Ensure a list of slugs., test_ids()

## Knowledge Gaps
- **207 isolated node(s):** `build_prep.sh script`, `ADDON`, `VER`, `PACKAGE`, `run.sh script` (+202 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Sensor` connect `Sensor` to `Sunsynk`, `driver.py`, `test_sensors.py`, `RegType`, `utils/__init__.py`, `HoldingUnit`, `RegType`, `RWSensor`, `ASensor`, `NumberRWSensor`, `SensorDefinitions`, `.get`, `test_helpers.py`, `InverterState`, `AInverter`, `test_state.py`, `a_inverter.py`, `ensure_slugs`, `.source`, `.__eq__`?**
  _High betweenness centrality (0.090) - this node is a cross-community bridge._
- **Why does `InverterState` connect `InverterState` to `Sunsynk`, `Sensor`, `test_a_inverter.py`, `test_sensors.py`, `utils/__init__.py`, `HoldingUnit`, `RegType`, `RWSensor`, `a_inverter.py`, `test_connection.py`, `NumberRWSensor`, `.value_to_reg`, `.get`, `SensorDefinitions`, `AInverter`, `tests/conftest.py`, `test_state.py`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **Why does `AInverter` connect `AInverter` to `Sunsynk`, `driver.py`, `test_a_inverter.py`, `percentile`, `timer_callback.py`, `RWSensor`, `a_inverter.py`, `ASensor`, `InverterState`?**
  _High betweenness centrality (0.063) - this node is a cross-community bridge._
- **Are the 15 inferred relationships involving `Sensor` (e.g. with `SensorOption` and `SensorOptions`) actually correct?**
  _`Sensor` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `InverterState` (e.g. with `AInverter` and `NumberRWSensor`) actually correct?**
  _`InverterState` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `AInverter` (e.g. with `ASensor` and `InverterOptions`) actually correct?**
  _`AInverter` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `RWSensor` (e.g. with `AInverter` and `ASensor`) actually correct?**
  _`RWSensor` has 11 INFERRED edges - model-reasoned connections that need verification._