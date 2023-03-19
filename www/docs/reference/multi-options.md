# Configuration

## Driver

The `DRIVER` can be **umodbus** or **pymodbus**.

The preferred driver is **umodbus** as it is more resilient.

The only reason why **pymodbus** is still available is to test the addon under Windows (it is *not* recommended to run it with pymodbus)

The `READ_SENSOR_BATCH_SIZE` option allows you to customize how many registers may be read in a single request. Devices like the USR only allows 8 registers to be read. When using mbusd this can be much higher.

## Inverters

The `INVERTERS` option contains a list of inverters

::: warning
Currently only a single inverter is supported!
:::

The following options are required per inverter:

- `SERIAL_NR`

  The serial number of your inverter. When you start the add-on the connected serial will be displayed in the log.

  The add-on will not run if the expected/configured serial number is not found.

  > This must be a string. So if your serial is a number only surround it with quotes `'1000'`

- `HA_PREFIX`

  A prefix to add to all the MQTT Discovered Home Assistant Sensors (default: SS).

- `MODBUS_ID`

  The Modbus Server ID is a number typically 1. Might be different in multi-inverter setups.

- `PORT`

  The port for RS485 communications, which can be either:

    - A tcp:// port of a Modbus TCP server. Example:
      ```yaml
      PORT: tcp://homeassistant.local:502
      ```

      This repository contains a mbusd TCP gateway add-on that can be used for this purpose.

    - A serial:// port. List of available ports under _Supervisor_ -> _System_ tab -> _Host_ card **&vellip;** -> _Hardware_

      Example:
      ```yaml
      PORT: serial:///dev/ttyUSB0
      ```

      *In order to assist with the name of your USB device, you can get a list of the current devices by inspecting the `DEBUG_DEVICE` options (located at the bottom of you config)*

    - A RFC2217 compatible port (e.g. `tcp://homeassistant.local:6610`)


## Sensors

The `SENSOR_DEFINITION` option allows you to select between `single-phase` and `three-phase` sensor definitions.

The `SENSORS` accepts a list of sensors to poll. Refer to the [single](./definitions) and [three](./definitions3ph) docs

~~The `SENSORS_FIRST_INVERTER` accepts a list of sensors that will only be applied to the first inverter~~

## Home Assistant Discovery options

The `MANUFACTURER` option allows you to rename the inverter manufacturer that will be displayed on the Home Assistant device. It does not have to be Sunsynk ;-)

The `NUMBER_ENTITY_MODE` option allows you to change how read/write sensors which present as number entities in Home Assistant behave.
The default display mode is `auto`. This setting controls how the number entity should be displayed in the UI. Can be set to `box` or `slider` to force a display mode.

## MQTT Settings

You will need a working MQTT server since all values will be sent via MQTT toward Home
Assistant.

The default configuration assumes the Mosquitto broker add-on and you simply have to
fill in your password.

```yaml
MQTT_HOST: core-mosquitto
MQTT_PORT: 1883
MQTT_USERNAME: hass
MQTT_PASSWORD: my-secure-password
```

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
