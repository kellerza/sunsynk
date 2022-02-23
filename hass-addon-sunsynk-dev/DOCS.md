# Configuration

## Parameters

- `PORT_URL`

  The port for RS485 communications, which can be either:

  - A serial:// port (e.g. /dev/ttyUSB0 as `serial:///dev/ttyUSB0`)

    List of available ports under _Supervisor_ -> _System_ tab -> _Host_ card **&vellip;** -> _Hardware_

  - A tcp:// port of a Modbus TCP server. (e.g. `tcp://homeassistant.local:502`)

    This repository contains a mbusd TCP gateway add-on that can be used for this purpose.

  - A RFC2217 compatible port (e.g. `tcp://homeassistant.local:6610`)

- `SUNSYNK_ID`

  The serial number of your inverter. When you start the add-on the connected serial will be displayed in the log.

  The add-on will not run if the expected/configured serial number is not found.

  > This must be a string. So if your serial is a number only surround it with quotes `'1000'`

- `MODBUS_SERVER_ID`

  The Modbus Server ID, typically 1. Might be different in multi-inverter setups.

- `SENSOR_PREFIX`

  A prefix to add to all the MQTT Discovered Home Assistant Sensors (e.g. try SS).

- `PROFILES`

  > BETA!!
  >
  > This writes settings, use at your own risk!

  Enables reading / writing settings to your inverter.

  The profiles will be presented as a Home Assistant Select Entity, with options for the different profiles.

  Available profiles:

  - **system_mode** The system mode, including time, grid charging, target SOC
  - **system_mode_voltages** The system mode charging voltages (likely used when you dont have a Battery with a BMS)

  The Inverter setting is only read when the Add-On starts, if you want to force re-reading the inverter settings and any configuratio, choose the **UPDATE** option in the Select Entity. (You can schedule **UPDATE** through automations if this is important for you)

  When you **UPDATE** a profile, the Add-On performs the following actions:
  - Read all the settings related to the profile from the Inverter.
  - Read all the profile presets from `/share/hass-addon-sunsynk/*.yml`.
  - The value of the Home Assistant Select entity will reflect the matching presets.
    - If the current settings is not part of existing presets, a new profile will be created.

      You can customize the name of the presets in the Yaml files (followed by an **UPDATE**).
      One option to access these files is though the Samba Add-On.

- `SENSORS`

  A list of sensors to poll. You can use any sensor defined in the sunsynk Python library - [here](https://github.com/kellerza/sunsynk/blob/main/sunsynk/definitions.py)

- `MQTT_*`

  You will need a working MQTT sevrer since all values will be sent via MQTT. The default configuration assumes the Mosquitto broker add-on and you simply have to fill in your password.

- `DEBUG`

  The values received will continuously be printed to the add-on's log. This will confirm that you receive values.

| Value | Description                 |
| ----- | --------------------------- |
| `0`   | No debug messages           |
| `1`   | Messages for filter changes |
| `2`   | Debug level logging         |

## Sensor modifiers - Min/Max/Now/Average/Step

Sensors fields can be modified by adding a modifier to the end of the field name. Without any modifier, a default modifier will be added based on the field name.

Other modifiers:

| Modifier | Description                                                                                                                      |
| -------- | :------------------------------------------------------------------------------------------------------------------------------- |
| `:max`   | the maximum value over the last 60 seconds. Ideal for _counters_ where you are typically interested only in the last value.      |
| `:min`   | the minimum value over the last 60 seconds.                                                                                      |
| `:now`   | the maximum value over the last 2 seconds. Useful to see current sensor value.                                                   |
| `:round_robin` | cycle over all configured settings. Ideal for config settings.                                                             |
| `:avg`   | the average over the last 60 seconds.                                                                                            |
| `:step`  | the average over the last minute will be reported, except if there is a significant change (>80) then it will be reported immediately. This is useful for automations using the current power. |

## Home Assistant

### Energy Management

You can read more Energy Management in Home Assistant [here](https://www.home-assistant.io/blog/2021/08/04/home-energy-management/) or [here](https://www.home-assistant.io/docs/energy/).

Example sensors that you can use with Energy Management (a hybrid inverter with PV and a battery).

```yaml
SENSORS:
  - total_active_power
  - total_grid_export
  - total_grid_import
  - total_pv_power
  - total_load_power
  - total_battery_charge
  - total_battery_discharge
```

Add these sensors to the Home Assistant Energy Panel

[![Open your Home Assistant instance and show your Energy configuration panel.](https://my.home-assistant.io/badges/config_energy.svg)](https://my.home-assistant.io/redirect/config_energy/)

[![Open your Home Assistant instance and show your Energy panel.](https://my.home-assistant.io/badges/energy.svg)](https://my.home-assistant.io/redirect/energy/)

### Templates

You can view sensor values under Home Assistant using the "Developer Tools" -> Templates tab.

```jinja
{% set s186 = states("sensor.ss_pv1_power")|float -%}      PV1:{{s186}}W
{%- set s187 = states("sensor.ss_pv2_power")|float %}      PV2:{{s187}}W
{%- set s190 = states("sensor.ss_battery_power")|float %}
{%- set s166 = states("sensor.ss_aux_power")|float %}      Gen:{{s166}}W

{%- set s169 = states("sensor.ss_grid_power")|float %}
{%- set s167 = states("sensor.ss_grid_l1_power")|float %}
{%- set s168 = states("sensor.ss_grid_l2_power")|float %}

Grid power:     {{s169}} = {{s167}} + {{s168}}
Grid CT power:  {% set s172 = states("sensor.ss_grid_ct_power")|float -%}   {{s172}}

{%- set s178 = states("sensor.ss_load_power")|float %}
{%- set s176 = states("sensor.ss_load_l1_power")|float %}
{%- set s177 = states("sensor.ss_load_l2_power")|float %}

Load Power: {{s178}} = {{s176}} + {{s177}}

Inv out: {% set s175 = states("sensor.ss_inverter_output_power")|float %} {{s175}}

Batt:    {{ s190 }}
Ess:     {{ states("sensor.ss_essential_power") }}   {{ s175-s166+s167 }} [175-166+167]
Non-Ess: {{ states("sensor.ss_non_essential_power") }}  {{ s172 -s167 }} [172-167]={{s172}}-{{s167}}
Grid CT: {{ s172 }} [172]
```
