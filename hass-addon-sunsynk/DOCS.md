# Configuration

## Parameters

- `PORT`

  The serial port for RS485 communications. List available ports under _Supervisor_ -> _System_ tab -> _Host_ card **&vellip;** -> _Hardware_

- `PORT_ADDRESS`

  The `host:port` or `ip:port` of a Modbus TCP server.

  This repository contains a mbusd TCP gateway add-on that can be used for this purpose.

  If defined, `PORT_ADDRESS` will be preferred above `PORT`

- `SUNSYNK_ID`

  The serial number of your inverter. When you start the add-on the connected serial will be displayed in the log.

  The add-on will not run if the expected/configured serial number is not found.

- `SENSORS`

  A list of sensors to poll. You can use any sensor defined in the sunsynk Python library - [here](https://github.com/kellerza/sunsynk/blob/main/sunsynk/definitions.py)

- `MQTT_*`

  You will need a working MQTT sevrer since all values will be sent via MQTT.
  The default configuration assumes the Mosquitto broker add-on and you simply have to
  fill in your password.

- `DEBUG`

  The values received will continuously be printed to the add-on's log. This will confirm
  that you receive values.

  The serial device

## Sensor modifiers - Min/Max/Average/Smart

Sensors fields can be modified by adding a modifier to the end of the field name.
Without any modifier, the sensor will have a smart interval.
The average will be reported every 60 seconds.
will be reported immediately.
These type of fields can be used in automations that will respond within the measurement
interval of the SMA Energy meter (1 second)

Other modifiers

| Modifier | Description                                                                                                                      |
| -------- | :------------------------------------------------------------------------------------------------------------------------------- |
| `:max`   | the maximum value over the last 60 seconds. <br/> Ideal for _counters_ where you are typically interested only in the last value |
| `:min`   | the minimum value over the last 60 seconds.                                                                                      |

## Home Assistant Energy Management

An example of a hybrid inverter with a battery

```yaml
SENSORS:
  - total_active_power:last
  - total_grid_export:last
  - total_grid_import:last
  - total_pv_power:last
  - total_load_power:last
  - total_battery_charge:last
  - total_battery_discharge:last
```

![HASS Energy management](energy.png)
