# Configuration

## DRIVER

The `DRIVER` can be **umodbus** or **pymodbus**.

Th preferred driver is **umodbus** as it is more resilient.

The only reason why **pymodbus** is still available is to test the addon under Windows (it is *not* recommended to run it with pymodbus)

## INVERTERS

- `INVERTERS` contains a list of inverters - currently only a single one supported! Refer to the section on Inverter settings to see what is supported per inverter.

- `SERIAL_NR`

  The serial number of your inverter. When you start the add-on the connected serial will be displayed in the log.

  The add-on will not run if the expected/configured serial number is not found.

  > This must be a string. So if your serial is a number only surround it with quotes `'1000'`

- `MODBUS_ID`

  The Modbus Server ID, typically 1. Might be different in multi-inverter setups.

- `HA_PREFIX`

  A prefix to add to all the MQTT Discovered Home Assistant Sensors (default: SS).

- `PORT`

  The port for RS485 communications, which can be either:

    - A serial:// port. List of available ports under _Supervisor_ -> _System_ tab -> _Host_ card **&vellip;** -> _Hardware_

      Example:
      ```yaml
      PORT: serial:///dev/ttyUSB0
      ```

    - A tcp:// port of a Modbus TCP server. Example:
      ```yaml
      PORT: tcp://homeassistant.local:502
      ```

      This repository contains a mbusd TCP gateway add-on that can be used for this purpose.

    - A RFC2217 compatible port (e.g. `tcp://homeassistant.local:6610`)


## SENSORS

- `SENSORS`

  A list of sensors to poll. You can use any sensor defined in the sunsynk Python library - [here](https://github.com/kellerza/sunsynk/blob/main/sunsynk/definitions.py).

- `NUMBER_ENTITY_MODE`

  When adding read/write sensors which present as number entities in Home Assistant, the default display mode is `auto`. This setting controls how the number entity should be displayed in the UI. Can be set to `box` or `slider` to force a display mode.

## MQTT Settings

You will need a working MQTT sevrer since all values will be sent via MQTT toward Home
Assistant.

The default configuration assumes the Mosquitto broker add-on and you simply have to
fill in your password.

```yaml
MQTT_
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
