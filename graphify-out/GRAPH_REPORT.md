# Graph Report - sunsynk  (2026-08-15)

## Corpus Check
- 110 files · ~232,385 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 969 nodes · 1839 edges · 79 communities (67 shown, 12 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 92 edges (avg confidence: 0.54)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8c76da0b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- SensorDefinitions
- package.json
- Sensor
- Adaptors & Wiring
- sensors.py
- a_inverter.py
- compilerOptions
- test_a_inverter.py
- InverterState
- RegType
- percentile
- ASensor
- __main__.py
- AInverter
- RWSensor
- RegType
- PySunsynk
- SolarmanSunsynk
- sensor_options.py
- ModbusUnit underlay
- sunsynk/helpers.py
- .read_sensors
- .connected_client
- BinarySensor
- Groups of sensors
- unpack_value
- Sunsynk
- definitions.md
- utils/__init__.py
- tests/conftest.py
- Run standalone using docker compose
- ToggleLogCallback
- .get
- Available addons
- Configuration
- Single-phase register backfill (proposal)
- Unreleased
- hex_str
- test_options.py
- Inverter Automation
- Deye/Sunsynk Inverters
- .reg_value
- multi-options.md
- Schedules
- Issue related to
- Deye/Sunsynk Inverters
- .__post_init__
- build_prep.sh
- Sunsynk — align with Cursor rules
- Issue related to the Python sunsynk library
- Custom/My Sensors
- types.d.ts
- Sunsynk User Documentation
- Your environment
- test_versions.py
- Modbus TCP to Modbus RTU Gateway Add-on
- .significant_change
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

## God Nodes (most connected - your core abstractions)
1. `Sensor` - 88 edges
2. `InverterState` - 70 edges
3. `AInverter` - 49 edges
4. `RWSensor` - 33 edges
5. `ASensor` - 31 edges
6. `NumberRWSensor` - 29 edges
7. `Sunsynk` - 28 edges
8. `SensorDefinitions` - 23 edges
9. `slug()` - 20 edges
10. `SelectRWSensor` - 20 edges

## Surprising Connections (you probably didn't know these)
- `generate_all_sensors()` --calls--> `pretty_table()`  [INFERRED]
  scripts/gen_sensors.py → src/sunsynk/utils/pretty_table.py
- `generate_all_sensors()` --calls--> `table_data()`  [INFERRED]
  scripts/gen_sensors.py → src/sunsynk/utils/pretty_table.py
- `test_load_env()` --calls--> `Schedule`  [INFERRED]
  src/tests/ha_addon_sunsynk_multi/test_options.py → src/ha_addon_sunsynk_multi/timer_schedule.py
- `main()` --calls--> `import_all_defs()`  [EXTRACTED]
  scripts/gen_sensors.py → src/sunsynk/definitions/__init__.py
- `generate_all_sensors()` --references--> `SensorDefinitions`  [EXTRACTED]
  scripts/gen_sensors.py → src/sunsynk/sensors.py

## Import Cycles
- 3-file cycle: `src/sunsynk/sensors.py -> src/sunsynk/utils/pretty_table.py -> src/sunsynk/state.py -> src/sunsynk/sensors.py`
- 4-file cycle: `src/sunsynk/sensors.py -> src/sunsynk/utils/__init__.py -> src/sunsynk/utils/pretty_table.py -> src/sunsynk/state.py -> src/sunsynk/sensors.py`

## Communities (79 total, 12 thin omitted)

### Community 0 - "SensorDefinitions"
Cohesion: 0.06
Nodes (37): ModuleType, generate_all_sensors(), generate_group_sensors(), main(), Generate groups/all.html., Shorten the definition name., Generate groups/{name}.yml., simple_def_name() (+29 more)

### Community 1 - "package.json"
Cohesion: 0.04
Nodes (45): clipboard, @iconify-json/mdi, js-yaml, markdown-it-deflist, markdown-it-imsize, sitemap-ts, @types/node, unplugin-icons (+37 more)

### Community 2 - "Sensor"
Cohesion: 0.08
Nodes (29): Get a list of sensors upon which this sensor depends., MathSensor, Sensor with a 16-bit/32-bit register registers., Math sensor, add multiple registers., Decode the inverter serial number., Return the source of the sensor., Sensor equality is based on the ID only., Sensor (+21 more)

### Community 3 - "Adaptors & Wiring"
Cohesion: 0.06
Nodes (31): (A) Cabling & connection, (B) Configuration, (C) Reducing timeouts, Check line voltage / termination resistor, Check the Modbus Server ID, Direct serial, Fault finding, Only a single connection to the serial port (+23 more)

### Community 4 - "sensors.py"
Cohesion: 0.13
Nodes (23): Sunsynk / Deye 16kW hybrid inverter sensor definitions., Sunsynk 5kW&8kW hybrid inverter sensor definitions., Sunsynk 5kW&8kW hybrid 3-phase inverter sensor definitions., Sunsynk/Deye hybrid 3-phase high voltage (HV) inverter sensor definitions., Sunsynk/Deye hybrid 3-phase LV inverter sensor definitions., Sensor classes represent modbus registers for an inverter., EnumSensor, FaultSensor (+15 more)

### Community 5 - "a_inverter.py"
Cohesion: 0.11
Nodes (23): MQTTOptions, init_connector(), init_driver(), ValType, React to sensor updates., Sunsynk driver factory., Init Sunsynk driver for each inverter., sensor_on_update() (+15 more)

### Community 6 - "compilerOptions"
Cohesion: 0.06
Nodes (30): docs/.vitepress/build_sitemap.ts, docs/.vitepress/**/*.ts, docs/.vitepress/**/*.vue, dom, dom.iterable, esnext, node_modules, ./node_modules/@types (+22 more)

### Community 7 - "test_a_inverter.py"
Cohesion: 0.10
Nodes (26): ExceptionGroup, Lock, register_structure_hook, compact_exception_group(), Compact exception group., Get the connector for this inverter., Convert a string to a Time., time_structure_hook() (+18 more)

### Community 8 - "InverterState"
Cohesion: 0.13
Nodes (23): NumberRWSensor, Numeric sensor which can be read and written., Get the reg value from a display value., Constant, Sensor that always returns a constant value., InverterState, Keep the state of the inverter., Get a generator of all sensors. (+15 more)

### Community 9 - "RegType"
Cohesion: 0.11
Nodes (15): RegType, ValType, Return the constant value., Return the value from the registers., Reg to value for binary., Calculate the math value., Decode the temperature (offset)., Decode the SD card status. (+7 more)

### Community 10 - "percentile"
Cohesion: 0.10
Nodes (25): percentile(), Statistics utilities., Calculate the given percentile of the data., parametrize, Tests for sunsynk.utils.stats., Percentile must be 0..100 inclusive., 0 and 100 return min and max., One value: any valid percentile returns that value. (+17 more)

### Community 11 - "ASensor"
Cohesion: 0.11
Nodes (17): MQTTEntity, ASensor, ValType, Return True if the units are a measurement., Is entity visible on this inverter., MQTT entities for stats., Addon Sensor state & entity., Return the last value. (+9 more)

### Community 12 - "__main__.py"
Cohesion: 0.16
Nodes (16): Exception, callback_discovery_info(), Update HASS discovery & write RWSensors., log_error(), print_errors(), Print an error message., main_loop(), AsyncCallback (+8 more)

### Community 13 - "AInverter"
Cohesion: 0.12
Nodes (15): AInverter, MQTT topic: ``online`` / ``offline`` reflect poll-loop lifecycle (retained)., Return the inverter power., Create discovery info for the inverter., Discover all sensors., Initialize the sensors., Addon Inverter state (per inverter)., build_callback_schedule() (+7 more)

### Community 14 - "RWSensor"
Cohesion: 0.13
Nodes (19): State of a sensor & entity., Entity definition for the timeout sensor., TimeoutState, Deals with inverter time format conversion complexities., Initialize from string or register value., SSTime, Get the available values for this sensor., Switch Sensor. The original implementation. (+11 more)

### Community 15 - "RegType"
Cohesion: 0.13
Nodes (11): RegType, ValType, Get the reg value from a display value, or the current reg value if out of…, Ensure correct parameters., Ensure correct parameters., Reg to value for binary., Get the reg value from a display value, or the current reg value if out of…, Get the reg value from a display value. (+3 more)

### Community 16 - "PySunsynk"
Cohesion: 0.16
Nodes (15): ModbusBaseClient, PySunsynk, Sunsync Modbus interface., Read a holding register., Sunsync Modbus class., Get client, connect if needed., Connect. Will create a new client if required., Write to a register - Sunsynk supports modbus function 0x10. (+7 more)

### Community 17 - "SolarmanSunsynk"
Cohesion: 0.13
Nodes (14): PySolarmanV5Async, Sunsynk lib using PySolarman., Read a holding register., Sunsynk class using PySolarmanV5., Get client, connect if needed., Write to a register - Sunsynk supports modbus function 0x10., SolarmanSunsynk, Any (+6 more)

### Community 18 - "sensor_options.py"
Cohesion: 0.16
Nodes (12): get_sensors(), Parse sensors from options., A dict of sensors from the configuration., Add a sensor. Keep dependencies for later., Parse options and get the various sensor lists., SensorOptions, get_schedule(), Get the schedule for the sensor. (+4 more)

### Community 19 - "ModbusUnit underlay"
Cohesion: 0.10
Nodes (19): Architecture: modbus-connection and sunsynk, Class layout, If Components come later, Layers, Modelling mismatch, Add-on, Class layout, Construction (+11 more)

### Community 20 - "sunsynk/helpers.py"
Cohesion: 0.13
Nodes (18): as_num(), ensure_tuple(), int_round(), patch_bitmask(), NumType, T, ValType, Combine bitmask values. (+10 more)

### Community 21 - ".read_sensors"
Cohesion: 0.14
Nodes (10): AInverterLifecycle, ValType, Publish retained lifecycle availability (no-op if MQTT is not connected)., Start or extend stale quiet: refresh deadline, set lifecycle, and log., Handle stale quiet or run a serial probe when quiet has elapsed., Return whether the last read left the serial register matching config., Read from the Modbus interface., Write to the Modbus interface. (+2 more)

### Community 22 - ".connected_client"
Cohesion: 0.16
Nodes (8): Any, Get client, connect if needed., Open a synchronous serial (RTU) transport and client., Run a client method, awaiting or threading depending on the transport., Connect. Will create a new client if required., Drop the client so the next call reconnects., Write to a register - Sunsynk supports modbus function 0x10., Read a holding register.

### Community 23 - "BinarySensor"
Cohesion: 0.15
Nodes (14): Read & write time sensor., SystemTimeRWSensor, BinarySensor, test_systemtime_rw(), test_binary_sensor(), Sunsynk sensor state., Test history with numeric values., Test if we have a ValueError. (+6 more)

### Community 24 - "Groups of sensors"
Cohesion: 0.13
Nodes (15): Adding sensors, All sensors, Available sensors, Battery, Diagnostics, Energy management, Generator, Groups of sensors (+7 more)

### Community 25 - "unpack_value"
Cohesion: 0.19
Nodes (14): pack_value(), RegType, Pack a value into register format. Args: value: The value to pack bits: Number…, Unpack register value(s) into an integer. Args: regs: Register values (1 or 2…, unpack_value(), extract_ints(), Test pack_value and unpack_value functions., Extract numbers from a string. (+6 more)

### Community 26 - "Sunsynk"
Cohesion: 0.23
Nodes (12): Sunsync Modbus class., Sunsynk, LogCaptureFixture, parametrize, patch, Test sunsynk library., A malformed response must not mix new words with cached registers., test_ss_not_implemented() (+4 more)

### Community 27 - "definitions.md"
Cohesion: 0.14
Nodes (9): Lovelace examples, Power Distribution card, Example #1, Example #2, System settings card, Sunsynk Power Flow Card, Energy Management, Home Assistant (+1 more)

### Community 28 - "utils/__init__.py"
Cohesion: 0.27
Nodes (10): PrettyTable, init_schedules(), Initialize the schedules., Override existing sensors with new definitions., pretty_table(), pretty_table_sensors(), T, Convert a list of dictionaries to a table data format. (+2 more)

### Community 29 - "tests/conftest.py"
Cohesion: 0.18
Nodes (11): Config, fixture, Item, Any, pytest_addoption(), pytest_collection_modifyitems(), pytest_configure(), Support command line marks. (+3 more)

### Community 30 - "Run standalone using docker compose"
Cohesion: 0.17
Nodes (12): amd64 / aarch64 / armv6 / armv7, CLI: amd64 / aarch64 / armv6 / armv7, Docker CLI examples, Docker-Compose examples, Example Configuration, Explanation of Environment Variables, Local Docker-Compose Builds, Mbusd (+4 more)

### Community 31 - "ToggleLogCallback"
Cohesion: 0.24
Nodes (6): Set log level to critical, and reset after duration., Toggle the log level., Toggle the log level to critical for a short time, to suppress expected errors., Calculate the next run times., Return next run seconds of entry 0., ToggleLogCallback

### Community 32 - ".get"
Cohesion: 0.20
Nodes (6): NumType, ValType, Return the average of the history., Get the current value of a sensor., Get the current value of a sensor., Resolve a number helper.

### Community 33 - "Available addons"
Cohesion: 0.20
Nodes (8): ESP add-on, Available addons, EskomSePush Add-on, Getting Started, Installation, Modbus TCP to Modbus RTU Gateway Add-on, Sunsynk/Deye Inverter Add-on (edge/dev), Sunsynk/Deye Inverter Add-on (multi)

### Community 34 - "Configuration"
Cohesion: 0.20
Nodes (10): Configuration, Debug options, Driver, Home Assistant Discovery options, Inverters, MQTT Settings, Port, Schedules (+2 more)

### Community 35 - "Single-phase register backfill (proposal)"
Cohesion: 0.22
Nodes (8): Background, Conflicts (verify before changing), Deye BMS block (large, separate effort), High value, Lower priority / per-phase & generator, Proposed additions, Single-phase register backfill (proposal), Suggested order of work

### Community 36 - "Unreleased"
Cohesion: 0.22
Nodes (8): Add-on behaviour, Changelog, Diagnostics and library, Docs and repo hygiene, GitHub issues (in progress), Internal / developer, Sensor definitions, Unreleased

### Community 37 - "hex_str"
Cohesion: 0.22
Nodes (6): hex_str(), Convert register values to hex strings., ValType, Write to a register - Sunsynk support function code 0x10., Read a holding register., test_hex_str()

### Community 38 - "test_options.py"
Cohesion: 0.25
Nodes (5): patch, Legacy umodbus driver and serial:// ports are migrated to pymodbus., test_load_env(), test_umodbus_remap(), test_unique()

### Community 39 - "Inverter Automation"
Cohesion: 0.22
Nodes (7): Battery charging to optimise Time-of-Use tariffs, Charge the battery in case of low forecast, Detecting power failures / Load shedding, Inverter Automation, Load Limit, Config packages, Home Assistant Examples

### Community 40 - "Deye/Sunsynk Inverters"
Cohesion: 0.25
Nodes (6): [Overview](./overview), Alternatives, Credits, Deye/Sunsynk Inverters, Home Assistant Sunsynk Add-On, Sunsynk Python Library

### Community 41 - ".reg_value"
Cohesion: 0.29
Nodes (5): setter, Get the register value., Convert from a register value., Get the value in hh:mm format., Parse a string in hh:mm format.

### Community 43 - "Schedules"
Cohesion: 0.29
Nodes (5): Keys, Proposed schedule overrides for Solarman, Schedule entries, Schedules, Sensor modifiers

### Community 44 - "Issue related to"
Cohesion: 0.33
Nodes (5): Describe the issue/bug, Issue related to, Logs, Your configuration, Your environment

### Community 45 - "Deye/Sunsynk Inverters"
Cohesion: 0.33
Nodes (5): Deye/Sunsynk Inverters, Documentation, Home Assistant Sunsynk Add-On, Installation, Sunsynk Python Library

### Community 46 - ".__post_init__"
Cohesion: 0.33
Nodes (3): Post-initialization processing., Ensure correct parameters., Ensure correct parameters.

### Community 47 - "build_prep.sh"
Cohesion: 0.40
Nodes (4): ADDON, PACKAGE, build_prep.sh script, VER

### Community 48 - "Sunsynk — align with Cursor rules"
Cohesion: 0.40
Nodes (4): Conflicts, Current rule files (index), Sunsynk — align with Cursor rules, What to do

### Community 49 - "Issue related to the Python sunsynk library"
Cohesion: 0.40
Nodes (4): Describe the issue/bug, Expected behavior, Issue related to the Python sunsynk library, Logs (if applicable)

### Community 50 - "Custom/My Sensors"
Cohesion: 0.40
Nodes (5): Creating your own sensor, Custom/My Sensors, Example: Simple division, Example: Time sensor, Using the sensor

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

### Community 58 - "ensure_str"
Cohesion: 0.67
Nodes (3): ensure_str(), Any, Ensure a value is a string.

## Knowledge Gaps
- **198 isolated node(s):** `build_prep.sh script`, `ADDON`, `VER`, `PACKAGE`, `run.sh script` (+193 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Sensor` connect `Sensor` to `SensorDefinitions`, `.get`, `sensors.py`, `a_inverter.py`, `InverterState`, `RegType`, `ASensor`, `AInverter`, `RWSensor`, `sensor_options.py`, `sunsynk/helpers.py`, `.read_sensors`, `BinarySensor`, `Sunsynk`, `utils/__init__.py`?**
  _High betweenness centrality (0.103) - this node is a cross-community bridge._
- **Why does `InverterState` connect `InverterState` to `.get`, `Sensor`, `sensors.py`, `a_inverter.py`, `test_a_inverter.py`, `AInverter`, `RWSensor`, `RegType`, `PySunsynk`, `BinarySensor`, `Sunsynk`, `utils/__init__.py`, `tests/conftest.py`?**
  _High betweenness centrality (0.074) - this node is a cross-community bridge._
- **Why does `AInverter` connect `AInverter` to `a_inverter.py`, `test_a_inverter.py`, `InverterState`, `percentile`, `ASensor`, `__main__.py`, `RWSensor`, `sensor_options.py`, `.read_sensors`, `Sunsynk`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `Sensor` (e.g. with `SensorOption` and `SensorOptions`) actually correct?**
  _`Sensor` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `InverterState` (e.g. with `AInverter` and `NumberRWSensor`) actually correct?**
  _`InverterState` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `AInverter` (e.g. with `ASensor` and `InverterOptions`) actually correct?**
  _`AInverter` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `RWSensor` (e.g. with `AInverter` and `ASensor`) actually correct?**
  _`RWSensor` has 10 INFERRED edges - model-reasoned connections that need verification._