# Deye/Sunsynk Inverters

This repo enables access to Deye Hybrid Inverters & Deye branded inverters like Sunsynk through a Python 3 library. It also provides an Add-On that can be installed in the Home Assistant OS.

This code was developed on a [Sunsynk](https://www.sunsynk.org/) 5.5 kWh inverter.

> DISCLAIMER: Use at your own risk! Especially when writing any settings.

## Documentation

Refer to [https://kellerza.github.io/sunsynk/](https://kellerza.github.io/sunsynk/)

## Home Assistant Sunsynk Add-On

For the Add-On you require Home Assistant OS and a RS-485 adaptor to connect to your Sunsynk inverter. Sensors are read using the Modbus protocol and sent to a MQTT server. See [deployment options](https://kellerza.github.io/sunsynk/guide/deployment-options) for examples of tested hardware.

### Installation

1. Add this repository to your HA Supervisor

   [![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fkellerza%2Fsunsynk)

   `https://github.com/kellerza/sunsynk`

2. Install the Sunsynk Add-On from the **Add-On Store** and configure through the UI

   ![Install Sunsynk Addon](https://github.com/kellerza/sunsynk/raw/main/images/addon-install.png)


Below an example of the HomeAssistant Energy management dashboard using sensors from the Sunsynk.

![HASS Energy management](https://github.com/kellerza/sunsynk/raw/main/images/energy.png)

## Sunsynk Python Library
[![PyPI version](https://badge.fury.io/py/sunsynk.svg)](https://pypi.org/project/sunsynk/)
[![codecov](https://codecov.io/gh/kellerza/sunsynk/branch/main/graph/badge.svg?token=ILKRC5UTXI)](https://codecov.io/gh/kellerza/sunsynk)

The Python library is available through pip: `pip install sunsynk`
