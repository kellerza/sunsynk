# Configuration

## Driver

The `DRIVER` should be **pymodbus** or **solarman**. **umodbus** can be used as a last resort.

The `READ_SENSOR_BATCH_SIZE` option allows you to customize how many registers may be read in a single request. Devices like the USR only allows 8 registers to be read. When using mbusd this can be much higher.

The `READ_ALLOW_GAP` option allows you to set the amount of gap between requested registers. In some cases it makes more sense to read a couple of additional registers in 1 or two requests, than trying to read exactly what you are looking for in multiple requests.

## Inverters

The `INVERTERS` option contains a list of inverters

The following options are required per inverter:

- `SERIAL_NR` – The serial number of your inverter. When you start the add-on the connected serial will be displayed in the log.

  The add-on will not run if the expected/configured serial number is not found.

  ::: tip

  This must be a string. So if your serial is a number only surround it with quotes `'1000'`

  :::

- `HA_PREFIX` – A prefix to add to MQTT discovered Home Assistant entities (default: SS).
- `MODBUS_ID` – The Modbus Server ID is a number, typically 1. Might be different in multi-inverter setups.

- `DONGLE_SERIAL_NUMBER` – The **solarman** driver requires the dongle's serial number.

- `PORT` – The port used for communications. Format depends on the driver. See [Port](#port)

### Port

The port for RS485 communications, which can be either:

- A `tcp://` port toward a Modbus TCP gateway. Either mbusd or one of the hardware options

  ```yaml
  INVERTERS:
    - PORT: tcp://homeassistant.local:502
  ```

  If your gateway do not support Modbus TCP to Modbus RTU conversion, you can try using `serial-tcp://` or `serial-udp://` as the port protocol. This will send Modbus RTU framed data over TCP/UDP (RTU-over-TCP).

  ::: details Solarman driver details

  The Solarman driver typically uses `tcp://`, with a port value of **8899**. You will need to find the dongle's local IP on your network. You can find the IP on your router, or use a utility like [netscan](https://www.portablefreeware.com/?id=730).

  You probably want to set a fixed IP for the dongle on your router.

  ```yaml
  DRIVER: solarman
  INVERTER:
    - PORT: tcp://192.168.1.182:8899
  ```

  Refer to the [Schedules](./schedules) section for recommended schedule overrides.

  :::

- A serial port. List of available ports under _Supervisor_ -> _System_ tab -> _Host_ card **&vellip;** -> _Hardware_ (You can also use the text in the DEBUG_PORT as reference)

  ```yaml
  DRIVER: pymodbus
  INVERTERS:
    - PORT: /dev/ttyUSB0
  ```

  ::: tip
  This repository contains a [mbusd](../guide/mbusd) add-on, a very reliable Modbus TCP to Modbus RTU gateway.

  If you have any issues connecting directly to a serial port, please try mbusd - also see [this](https://github.com/kellerza/sunsynk/issues/131) issue
  :::

  ::: details umodbus driver

  The driver can also be umodbus, but this should be used as a last resort only, especially for serial connections.

  umodbus requires a `serial://` prefix

  ```yaml
  DRIVER: umodbus
  INVERTERS:
    - PORT: serial:///dev/ttyUSB0
  ```

  :::

- For the first inverter in the list, you can use an empty string. The serial port selected under `DEBUG_DEVICE` will be used (located at the bottom of you config)*

  ```yaml
  INVERTERS:
    - PORT: ""
  ```

- umodbus supports an RFC2217 compatible port (e.g. `tcp://homeassistant.local:6610`)

## Sensors

- `SENSOR_DEFINITION` – Allows you to select between `single-phase`, `single-phase-16kw`, `three-phase` and `three-phase-hv` sensor definitions.

- `SENSORS` – Accepts a list of sensors to poll. Refer to [Sensor definitions](./definitions).

- `SENSORS_FIRST_INVERTER` – Accepts a list of sensors that applies to the first inverter.

## Schedules

Refer to [Schedules](./schedules)

## Home Assistant Discovery options

`HA_PREFIX` – a per-inverter option that will be used for the Device (Inverter) name and as prefix for all the entity Ids in Home Assistant

`MANUFACTURER` - allows you to rename the inverter manufacturer that will be displayed on the Home Assistant device. It does not have to be Sunsynk ;-)

`NUMBER_ENTITY_MODE` - allows you to change how read/write number entities display in Home Assistant.
The default display mode is `auto`. This setting controls how the number entity should be displayed in the UI. Can be set to `box` or `slider` to force a display mode.

`PROG_TIME_INTERVAL` – allows you to change the time interval in the lists for setting the program time.
Be aware that if you set this to 5 minutes you will have a very long select list of times to scroll through.

## MQTT Settings

If you are running on a standard Home Assistant OS installation, you don't need any MQTT configuration. The add-on will query the HA Supervisor for the MQTT server and login details. If successful, it will prefer information from the supervisor and ignore the configuration.

The MQTT integration in Home Assistant needs to publish MQTT Birth (**online**) and Last will (**offline**) messages to `homeassistant/status`. This can be done by clicking _Re-configure MQTT_ in the UI.

::: details MQTT configuration options (optional)

Configuration from the supervisor will be preferred if you don't have `MQTT_CUSTOM: true` set.

```yaml
MQTT_CUSTOM: true   # Force the add-on to use this MQTT configuration
MQTT_HOST: core-mosquitto
MQTT_PORT: 1883
MQTT_USERNAME: hass
MQTT_PASSWORD: my-secure-password
```

:::

## Debug options

- `DEBUG`

  The values received will continuously be printed to the add-on's log. This will confirm
  that you receive values.

  | Value | Description                  |
  | ----- | ---------------------------- |
  | `0`   | No debug messages.           |
  | `1`   | Messages for filter changes. |
  | `2`   | Debug level logging.         |

- `DEBUG_DEVICE` allows you to select the USB port in the UI. It will only be used if `PORT` is empty. But you have to select something.
