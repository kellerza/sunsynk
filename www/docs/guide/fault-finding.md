# Fault finding

## Startup process

The addon follows the following startup process:

1. Load config, sensor definitions and schedules

   The logs will show if you use any unknown or deprecated sensors, if you have anything wrong in
   your custom sensors, and the intended schedule for reading sensors.

2. Connect to the Inverter

   Connect and read the inverter identity (device type, protocol, serial) from registers 0–7, then
   rated power from the selected sensor definitions. This is the first step to ensure the connection
   is working.

   If this read fails, you need to follow the fault finding guide below. It could be a cabling
   issue, a configuration issue, or a hardware issue.

   If successful, the serial number in your config is checked against the inverter. A warning is
   logged when `SENSOR_DEFINITIONS` does not match the device type. The log will show identity
   details and the rated-power startup read.

   If the identity and rated power reads succeed, it will read all configured sensors to ensure you
   have some values at startup

3. Connect to the MQTT server

   Publish the discovery data for Home Assistant, and also remove discovery data if required

   If this step fails, you will not see any entities in Home Assistant and you need to check your
   MQTT server settings.

Once the startup is complete, the addon will continue to read & publish sensor data. During this
process you will occasionally see read failures. As long as this does not happen on every read, you
can probably continue using the addon, but can consider reducing sensors, relaxing the read
schedules, etc.

If you poll several inverters on one RS485 bus and one unit stops replying, it might enter a
**stale** state so the bus is not blocked. Tune `STALE_INVERTER_AFTER_SECONDS` and
`STALE_INVERTER_SKIP_SECONDS` in the Supervisor options (see
[Multi add-on options](../reference/multi-options#stale-inverter-global)). After each **successful**
Modbus read, a timer is armed: if reads are still failing once that many seconds have passed since
the last success, the add-on pauses normal polling for that inverter for the configured skip period,
then probes the serial register once before resuming or extending stale quiet.

A parallel AC setup (inverter **Parallel Mode** Client / Server) does **not** mean both inverters
share the RS485 Modbus bus. If the second inverter never appears, see
[Parallel inverters](#parallel-inverters) below.

If you fail to get a reply from the inverter, typically if step #2 fails, please check the
following:

## (A) Cabling & connection

While fault finding use as short as possible cable, outside any sprague/trunking. Once everything
works, you can switch to a more permanent, much longer cable.

If you cannot establish a connection, check the RS485 adaptor and cabling. Are you plugged into the
correct port, is your connector crimped correctly?

::: tip

Many newer Sunsynk/Deye hybrids use one **BMS** RJ45 socket for both **RS485** (what this add-on
uses) and **CAN** (battery management). If the battery already uses that port, you cannot simply
“share” a normal patch cable—you need a splitter or Y-cable that keeps CAN on its pair and RS485 on
**pins 1–3** only on the adaptor leg. Pinout, splitter layouts, and what goes wrong if all eight
wires are duplicated to both sides are covered in
**[Adaptors & Wiring](./wiring.md#combined-rs485-can-bms-port)** (continue through
**If the battery already uses this port** and **Pin reference**).

:::

Other factors that might impact connection, or reliability:

- Use a RJ45 converter with a GROUND pin. Ensure the ground is connected.
- Re-crimp your RJ45 connector.
- Use a good quality solid CAT5e/CAT6 cable.
  - Ensure the data line is using a twisted pair.
- Ensure your RS485 cable does not run parallel to other electrical cables (AC or DC), to reduce
  interference. e.g. in trunking.
  - If interference is a problem, are you using a twisted pair in the cable?
  - If interference is a problem, it could also help to use a shielded cable. Ground the shield at
    ONE end only (i.e. on the USB adaptor side and then just use normal plastic RJ45 connector on
    the inverter side.)
- If you still fail to make a connection, test the line voltage resistor (see Reducing timeouts
  below)

## (B) Configuration

### Check the Modbus Server ID

Ensure the Modbus Server ID (`MODBUS_ID` config setting) matches the configured **Modbus SN** value
of the inverter. This value must not be zero.

View/update the Modbus server ID on your inverter under "Advanced Settings" / "Multi-Inverter".

Please note that this can be reset to zero after a software upgrade on your inverter, and this will
stop the addon from reading data from your inverter. Resetting it to the previous value (the value
the value in `MODBUS_ID` if you had this working previously), and then restarting the inverter
should fix the
[issue](https://powerforum.co.za/topic/15779-home-assistant-no-longer-getting-data-after-sunsynk-firmware-update-solved/).

![Modbus Server ID](../images/modbus_sn.png =70%x)

### Only a single connection to the serial port

Ensure you only have a single addon connected to the serial port. The following can all potentially
access the USB port: mbusd, Node RED, the normal and dev addon version.

If you need to have multiple connections to the serial port: ONLY connect mbusd to the serial port.
Connect all addons to mbusd (e.g. tcp://192.168.1.x:503).

## (C) Reducing timeouts {#c-reducing-timeouts}

If you get many timeouts, or if the addon does not read all your sensors on startup (i.e. you see
**Retrying individual sensors** in the log), you can try the following. The **RS485 timeout**
diagnostic sensor on each inverter ([Stats](#stats)) shows whether timeouts are still climbing.

- Set `READ_SENSORS_BATCH_SIZE` to a smaller value, i.e. 8.
- Direct serial and TCP wait `READ_MESSAGE_SPACING` seconds after each reply (default **0.05**).
  Raising `TIMEOUT` only waits longer for a missing reply; it does not add that gap. Try **0.1** or
  **0.15** if timeouts continue.
- The most reliable way to connect is to use mbusd to the serial port & connect the addon to mbusd
  at `tcp://<ip>:502`. The mbusd instance/addon can be on the same physical device or a remote
  device.

Check the cabling and connection again. Use a 1m cable and stand next to the inverter while testing.

### Direct serial

If your RS485 adaptor is plugged directly into your host, connecting directly to the serial port
`PORT: "/usb/ttyX"` might not give you the best results.

Once you have a working connection (reading the serial), consider introducing **mbusd** into your
setup, in this configuration mbus connects to the serial port and the addon connects via TCP,
typically: `PORT: tcp://homeassistant.local:502`

**mbusd** over `tcp://` is a reliable setup. Direct serial (`PORT: /dev/ttyUSB0`) is also supported
(tmodbus); see [configuration](../reference/multi-options#port). If direct serial is flaky, prefer
mbusd.

### Check line voltage / termination resistor

If your RS485 adapter has a termination resistor (typically 120 ohms), try removing it.

To check, disconnect the adapter and use a multimeter to measure the resistance between A & B.

The d.c. voltage between A/B on the sunsynk RS485 connection should idle around 4-5v with nothing
connected, but this may drop to around 0.5v with the 120 ohm load.

RS485 devices are typically multi-drop with a termination resistor on the first and last devices.
However, the RS485 BMS port may only be intended to connect to a single device.

![RS485](../images/rs485-term.jpg =70%x)

## (D) Parallel inverters — second inverter not responding {#parallel-inverters}

The add-on can poll several inverters on **one** adaptor when they share a physical RS485 bus: same
`PORT`, unique `MODBUS_ID` (and `SERIAL_NR` / `HA_PREFIX`) per unit. See
[Shared RS485 bus](../reference/multi-options#port).

Parallel Mode does **not** automatically daisy-chain Modbus. If only one inverter answers, or the
other goes **stale** / startup shows no response, test **one inverter at a time** with the **same**
USB adaptor. Change only which RJ45 you plug into and the single `INVERTERS` entry. The inverter LCD
may still say Master / Slave for Parallel Mode; this add-on uses **Client** / **Server**. See
[Modbus](./overview.md#modbus).

1. **Baseline — inverter 1 only.** Plug the cable into inverter 1. Configure one `INVERTERS` entry
   for that unit (`MODBUS_ID` matching its **Modbus SN**). If this fails, it is a normal connection
   problem — follow (A)–(C).

2. **Inverter 2 on its own socket.** Move the **same** cable to inverter 2. Change the config to
   inverter 2 only (`HA_PREFIX`, `MODBUS_ID`, `SERIAL_NR`). If this fails while plugged into
   inverter 2, inverter 2 is not answering Modbus: check its Modbus SN, cabling, and whether that
   model exposes RS485 on the port you are using when Parallel Mode is Server.

3. **Is the bus shared?** Plug the cable back into inverter 1. Keep the **inverter 1** config. Then
   move the cable to inverter 2 **without changing the config**.

   - If inverter 1 still answers with the cable on inverter 2, the RS485 bus **is** shared — use the
     **same** `PORT` for both `INVERTERS` entries, with unique `MODBUS_ID`s.
   - If it goes silent, the bus is **not** shared. Use **two adaptors** (two `PORT`s), one per
     inverter.

4. **Optional cross-check.** Cable on inverter 1, config for inverter 2 only. A reply means inverter
   2 is reachable through inverter 1's socket (shared bus). No reply means the bus is not shared, or
   inverter 2's `MODBUS_ID` is wrong.

When using two adaptors, `MODBUS_ID` must match whatever unit actually answers on **that** adaptor.
Some units in Server mode still answer as `1` on their own RS485 port even when the display shows a
different Modbus SN.

## Stats {#stats}

Each inverter publishes two **diagnostic** MQTT entities (not listed under `SENSORS`). They appear
on the inverter device in Home Assistant under **Diagnostic**, and update every **120 seconds**.

### RS485 timeout

Cumulative Modbus timeout count for that inverter since the add-on started (reads and writes,
including gateway **0x0B**). Occasional increases are normal. A steadily rising count means the bus
is dropping replies — see [(C) Reducing timeouts](#c-reducing-timeouts).

### Callback stats

Duration of that inverter's poll cycle. The state is the **mean** time in seconds over the last
120s. Attributes add `count`, `min`, `max`, `median`, `stdev`, `p5`, `p95`, plus:

- `busy_count` — a new poll was skipped because the previous one was still running
- `error_count` — the poll raised an error

If **mean** / **p95** approach the schedule interval, or **busy_count** climbs, the add-on cannot
keep up: reduce sensors, relax schedules, or fix timeouts. `error_count` should stay near zero.
