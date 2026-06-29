# Single-phase register backfill (proposal)

> **Status: NOT IMPLEMENTED — plan only.** None of the sensors below have been added to the
> definitions yet. This document captures a comparison between the single-phase profile
> (`src/sunsynk/definitions/single_phase.py`) and the register dump shared in
> [issue #650](https://github.com/kellerza/sunsynk/issues/650) (scraped from `api.sunsynk.net` for a
> `SYNK-8K-SG05LP1`). Use it as a backlog when adding new single-phase sensors.

## Background

The API register numbers in #650 line up almost exactly with our single-phase Modbus map (e.g. `60`
Etoday, `79` Fac, `90` DcTemp, `109` Vpv1, `182` BatteryTemp, `190` BatteryPower, `312` ChargeVolt),
so the list is a trustworthy reference for the **single-phase** profile.

The core of the list is already mapped: rated power, run state, all the daily/monthly/yearly/total
energy counters, faults, PV1-3 V/I/P, grid/inverter/load V·I·P·Hz, battery temp/V/SOC/power/current,
charge voltage and the charge/discharge current limits, and the load limit.

## Proposed additions

Read-only sensors that align well with the existing map and could be backfilled.

### High value

| Reg | #650 name         | Proposed sensor                    | Notes                                                                                        |
| --- | ----------------- | ---------------------------------- | -------------------------------------------------------------------------------------------- |
| 179 | UpsLoadPowerL1    | UPS/Essential load L1 power (W)    | Directly-measured essential load — complements the computed `Essential power` math           |
| 180 | UpsLoadPowerL2    | UPS/Essential load L2 power (W)    |                                                                                              |
| 185 | UpsLoadPowerTotal | UPS/Essential load total power (W) | ⚠️ Currently reused as `Gen L2 current` — see [Conflicts](#conflicts-verify-before-changing) |
| 316 | RealtimeCap       | BMS SOC (%)                        |                                                                                              |
| 317 | RealtimeVolt      | BMS battery voltage (V)            |                                                                                              |
| 318 | RealtimeCurrent   | BMS battery current (A)            |                                                                                              |
| 319 | RealtimeTemp      | BMS battery temperature (°C)       |                                                                                              |
| 313 | DischargeVolt     | Battery discharge voltage (V)      | Pairs with `312` charge voltage                                                              |
| 93  | Pf                | Power factor                       | factor `0.001`                                                                               |

### Lower priority / per-phase & generator

| Reg | #650 name        | Proposed sensor              | Notes                                                               |
| --- | ---------------- | ---------------------------- | ------------------------------------------------------------------- |
| 107 | BattCalibration  | BMS battery capacity (Ah)    |                                                                     |
| 151 | Grid vacL2       | Grid L2 voltage (V)          |                                                                     |
| 155 | InvVacL2         | Inverter L2 voltage (V)      |                                                                     |
| 157 | LoadL1           | Load L1 voltage (V)          |                                                                     |
| 158 | LoadL2           | Load L2 voltage (V)          |                                                                     |
| 162 | LimiterL1        | CT/Limiter L1 current (A)    |                                                                     |
| 163 | LimiterL2        | CT/Limiter L2 current (A)    |                                                                     |
| 165 | InvCurrentL2     | Inverter L2 current (A)      |                                                                     |
| 170 | AcLimiter1Power  | CT L1 power (W)              |                                                                     |
| 171 | AcLimiter2Power  | CT L2 power (W)              |                                                                     |
| 173 | InvL1Power       | Inverter L1 power (W)        |                                                                     |
| 174 | InvL2Power       | Inverter L2 power (W)        |                                                                     |
| 62  | GenToday         | Generator energy/run today   | units unclear (seconds?)                                            |
| 83  | GenDailyTime     | Generator daily run time (h) |                                                                     |
| 195 | AlternatorStatus | Generator/alternator status  |                                                                     |
| 196 | FreqGen          | Generator frequency (Hz)     |                                                                     |
| 115 | Vpv4             | PV4 voltage (V)              | SG05LP1 reports `0`; likely only relevant on 3-MPPT / 16kW variants |
| 116 | Ipv4             | PV4 current (A)              | as above                                                            |

### Deye BMS block (large, separate effort)

We currently expose only `Bat1 SOC` (`603`) and `Bat1 Cycle` (`611`). #650 reveals a full Deye BMS
map that is only populated on Deye-protocol batteries:

- **Summary** `10000`-`10022` — device type, protocol/pack count, V/A/SOC/SOH/temp, charge &
  discharge limits, faults/alarms.
- **Per-pack detail** starting `10032` for pack 1, then `+38` per pack up to pack 22 (SN, module
  V/A, cell temps, SOC/SOH, capacities, max/min cell, cycle count, MOS status, warnings/faults,
  SW/HW version).

This is BMS-specific and a much larger structured addition, so it should be tackled as its own piece
rather than alongside the simple sensors above.

## Conflicts (verify before changing)

A few existing single-phase mappings disagree with the #650 labels. These may be portal mislabels,
so they should **not** be changed without a second source:

| Reg | Current mapping               | #650 label                                   |
| --- | ----------------------------- | -------------------------------------------- |
| 92  | `SD status`                   | `GenTotalLow` (#650 puts `SdStatus` at `94`) |
| 95  | `Environment temperature`     | `GenTotalHigh`                               |
| 61  | `Day reactive energy` (kVarh) | `Netoday`                                    |
| 185 | `Gen L2 current`              | `UpsLoadPowerTotal`                          |

## Suggested order of work

1. Low-risk, clearly-useful read-only sensors: essential/UPS load power (`179`/`180`), BMS realtime
   (`316`-`319`), discharge voltage (`313`), power factor (`93`).
2. Resolve the `185` conflict before adding UPS total power on that register.
3. Per-phase voltages/currents and generator status/frequency.
4. The Deye BMS `10000+` block as a dedicated effort.
