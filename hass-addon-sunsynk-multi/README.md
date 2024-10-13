# Sunsynk Inverter Add-on (Multi)

An add-on to read Inverter Sensors and push them to MQTT.
It supports Home Assistant auto-discovery.

The addon supports multiple inverters and allows you to update the inverter settings.

See the docs for more info - [https://kellerza.github.io/sunsynk](https://kellerza.github.io/sunsynk/reference/multi-options)

Example of Home Assistant Energy Management, enabled by this addon.

![HASS Energy management](https://github.com/kellerza/sunsynk/raw/main/images/energy.png)

## Usage of env vars

You can also use env vars for config options. For them to work, you need to add one additional env var**: 

S6_KEEP_ENV: 1

** More info here: https://github.com/just-containers/s6-overlay#customizing-s6-overlay-behaviour