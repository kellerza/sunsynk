# Deye/Sunsynk Inverters

This project enables access to Deye Hybrid Inverters & Deye branded inverters like Sunsynk through a Python 3 library. It also provides an Add-On that can be installed in the Home Assistant OS.

This code was developed on a [Sunsynk](https://www.sunsynk.org/) 5.5 kWh inverter.

::: warning Disclaimer
DISCLAIMER: Use at your own risk! Especially when writing any settings.
:::

## Home Assistant Sunsynk Add-On

An add-on to receive Sunsynk Inverter Values and push them to Home Assistant through MQTT.

It supports Home Assistant auto-discovery for the sensors and flexible scheduling when to read and when to report.

![HASS Energy management](https://github.com/maslyankov/sunsynk/raw/main/images/energy.png)

For the Add-On you require Home Assistant OS and a RS-485 adaptor to connect to your Sunsynk inverter. Sensors are read using the Modbus protocol and sent to a MQTT server.

## Alternatives

There are several alternative ways to access your inverter data. These include:

- ESP32
- Node-RED
- Solar Assistant (a commercial application)

I have posted [why](https://powerforum.co.za/topic/16136-home-assistant-inverter-integration-options/?do=findComment&comment=146782) I believe this addon is the easiest and most flexible way to do this:

- Reconfigure your inverter settings with the Home Assistant UI (dropdowns & sliders) or automations
- Automatic updates in HASS & maintained by a couple of community members
- Data filters to reduce the number of updates & writes to low-cost SD cards, but still have 1 or 2 second automation response to big changes in load **Now based on schedules**
- Various options to connect to the inverter wireless or wired (preferred, since it updates every second)

While a wired setup is more work, the addon reads several sensors each second and personally I would rather do this over a wired gateway/cable.

## Sunsynk Python Library

[![PyPI version](https://badge.fury.io/py/sunsynk.svg)](https://pypi.org/project/sunsynk/)
[![codecov](https://codecov.io/gh/kellerza/sunsynk/branch/main/graph/badge.svg?token=ILKRC5UTXI)](https://codecov.io/gh/kellerza/sunsynk)

This addon uses the Python sunsynk library. The Python library is available through pip: `pip install sunsynk`

::: info
Please note that the addon is an example of how the library can be used and no support can be given for your own Python applications.
:::

## Credits

- Powerforum users Bloubul7, @jacauc and Sc00bs. See [this thread](https://powerforum.co.za/topic/8646-my-sunsynk-8kw-data-collection-setup/).
- @Ivan-L for adding the writable sensors.
- @kababook & @archi for the 3-phase definitions.
- Other [contributors](https://github.com/maslyankov/sunsynk/graphs/contributors)
