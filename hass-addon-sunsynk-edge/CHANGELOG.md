# Changelog

<https://github.com/kellerza/sunsynk/commits/>

## Unreleased

All items below are changes since add-on **0.10.1** (stable release on GitHub `main`).

### GitHub issues (in progress)

- [#639](https://github.com/kellerza/sunsynk/issues/639) – Loss of communication with one inverter
  blocked MQTT updates for **all** inverters; **per-inverter availability** is aimed at isolating
  failure to the affected device. Issue remains **open** until validated in the field.
- [#642](https://github.com/kellerza/sunsynk/issues/642) – Ongoing work to improve
  **AUX / generator port** alignment between **single-phase** and **three-phase** sensor definitions
  (issue **not closed**). _(GitHub thread title may also cover related inverter-side options.)_
- [#641](https://github.com/kellerza/sunsynk/issues/641) – Solarman / dongle connectivity (e.g. Fuji
  micro-inverter setups); **clearer warnings and validation** around **`DONGLE_SERIAL_NUMBER`** so
  misconfiguration shows up early in logs. Issue **open** while scenarios are confirmed.
- [#635](https://github.com/kellerza/sunsynk/issues/635) – New firmware **SELL** option per time
  program slot; **commented-out** proposed `SwitchRWSensor` definitions (`Prog1 sell` …
  `Prog6 sell`) are in `single_phase.py` for review—**not enabled** until register/bitmask behaviour
  is **verified** on hardware. Issue **open**.

### Add-on behaviour

- **Per-inverter availability** – Each inverter publishes its own retained lifecycle topic
  (`SS/availability_1_<HA_PREFIX>`). Home Assistant device discovery uses that together with the
  add-on MQTT session topic, so one inverter can enter a **stale** state (failed reads / timeouts)
  and its entities reflect **unavailable** without dragging the whole multi-inverter add-on offline.
- **`TIMEOUT`** – Modbus connect/read timeout in **seconds** (edge schema and translations). A full
  sensor batch/run is bounded by **`2 × TIMEOUT`** (`asyncio.timeout`) so slow buses can be tuned
  without changing schedule intervals alone.
- **`STALE_INVERTER_AFTER_SECONDS`** / **`STALE_INVERTER_SKIP_SECONDS`** – Grace period after the
  last good read before going stale, and how long to skip Modbus for that inverter while in stale
  quiet (then probe again). Defaults appear in edge `config.yaml`; see reference docs for details.
- **`DONGLE_SERIAL_NUMBER` (Solarman)** – Clearer **validation and logging** for the Wi-Fi dongle
  serial (non-zero integer, driver consistency, ignored values on non-Solarman drivers)—see
  [#641](https://github.com/kellerza/sunsynk/issues/641).

### Sensor definitions

- **Aliases** – Sensors may declare an `alias` (string or tuple). Each alias is registered in
  `SensorDefinitions.all` under a **slug** of that name, pointing at the **same** `Sensor` instance
  as the canonical `name`. Your `SENSORS` list can use either the primary id (from `name`) or any
  alias id (e.g. **Gen** vs **AUX** labelling on generator port registers) without duplicating
  registers in the definition set.
- **Single-phase / three-phase** – Commented register notes for **Essential power** math sensors;
  continued tweaks in `single_phase.py` and `three_phase_common.py` (including **Gen** / **AUX**
  port sensors) toward clearer parity across definitions.
- **Program slot SELL (proposed)** – Commented **`Prog1 sell` … `Prog6 sell`** `SwitchRWSensor`
  lines (one per slot) for the new firmware **SELL** bit; left disabled pending verification—see
  [#635](https://github.com/kellerza/sunsynk/issues/635).
- **Tooling and docs** – `gen_sensors.py`, **Solarman** read path, generated **reference group**
  HTML, and power-flow / Lovelace examples updated to stay in sync with definition changes.

### Diagnostics and library

- **RS485 timeout** – Per-inverter MQTT sensor reflecting timeout counters from the connector (helps
  spot noisy RS485 / Solarman issues).

### Docs and repo hygiene

- **rumdl** – Markdown rules wired into **pre-commit** and applied across the VitePress site, README
  files, and GitHub issue templates (consistent lists, headings, emphasis).
- **Wiring** – [Wiring guide](https://kellerza.github.io/sunsynk/guide/wiring.html) clarifies using
  the inverter **RS‑232 (DB9)** port: **Modbus RTU** at **RS‑232** signalling (TX/RX vs ground),
  **not** RS‑485 levels—use a **USB‑RS‑232** adapter or a gateway that supports that port when you
  want a dedicated serial link instead of the **RS‑485** terminal block bus.
- **Reference docs** – `multi-options.md` updated for `TIMEOUT`, stale options, and the two-level
  availability model; other guide/example fixes (e.g. fault-finding, Lovelace).

### Internal / developer

- **Cursor and Copilot instructions** – Added **Cursor** rules (e.g. `.cursor/rules/`) and
  **GitHub Copilot** repo instructions (`.github/copilot-instructions.md`) so contributors and AI
  assistants follow the same add-on layout and editing policy.
- **`sunsynk.utils`** split (e.g. stats vs. pretty table), expanded **`a_inverter`** tests, and
  related **`uv.lock`** / dependency updates from the same workstream.
