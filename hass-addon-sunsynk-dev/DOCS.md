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

  > This must be a string. So if your serial is a number only place it in single quotes `'1000'`

- `SENSOR_PREFIX`

  A prefix to add to all the MQTT Discovered Home Assistant Sensors (e.g. try SS)

- `PROFILES`

  > BETA!!
  >
  > This writes settings, use at your own risk!

  Enables reading / writing settings to your inverter

  The profiles will be presented as a Home Assistant Select Entity, with options for the different profiles.

  The Inverter setting is only read when the Add-On starts, if you want to force re-reading the inverter settings and any configuratio, choose the **UPDATE** option in the Select Entity. (You can schedule **UPDATE** through automations if this is important for you)

  When you **UPDATE** a profile, the Add-On performs the following actions:
  - Read all the settings related to the profile from the Inverter.
  - Read all the profile presets from `/share/hass-addon-sunsynk/*.yml`
  - The value of the Home Assistant Select entity will reflect the matching presets.
    - If the current settings is not part of existing presets, a new profile will be created.

      You can customize the name of the presets in the Yaml files (followed by an **UPDATE**).
      One option to access these files is though the Samba Add-On.


- `SENSORS`

  A list of sensors to poll. You can use any sensor defined in the sunsynk Python library - [here](https://github.com/kellerza/sunsynk/blob/main/sunsynk/definitions.py)

- `MQTT_*`

  You will need a working MQTT sevrer since all values will be sent via MQTT.
  The default configuration assumes the Mosquitto broker add-on and you simply have to
  fill in your password.

- `DEBUG`

  The values received will continuously be printed to the add-on's log. This will confirm
  that you receive values.

| Value | Description                 |
| ----- | --------------------------- |
| `0`   | No debug messages           |
| `1`   | Messages for filter changes |
| `2`   | Debug level logging         |

## Sensor modifiers - Min/Max/Now/Average/Step

Sensors fields can be modified by adding a modifier to the end of the field name.
Without any modifier, a default modifier will be added based on the field name

Other modifiers

| Modifier | Description                                                                                                                      |
| -------- | :------------------------------------------------------------------------------------------------------------------------------- |
| `:max`   | the maximum value over the last 60 seconds. <br/> Ideal for _counters_ where you are typically interested only in the last value |
| `:min`   | the minimum value over the last 60 seconds.                                                                                      |
| `:now`   | the maximum value over the last 2 seconds. Useful to see current sensor value                                                    |
| `:avg`   | the average over the last 60 seconds                                                                                             |
| `:step`  | the average over the last minute will be reported, except if there is a significant change (>80) then it will be reported immediately. This is useful for automations using the current power |

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
