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

## Run locally using docker compose

In these example commands we prefix the `docker-compose build` commands with the 
environment variable definition `BUILD_FROM=homeassistant/amd64-base-python:3.9`, 
which specifies which base image is used. For a Raspberry Pi you would need to 
use `BUILD_FROM=homeassistant/armhf-base-python:3.9`.
A list of available base images can be found in 
`hass-addon-sunsynk-multi/build.yaml` and `hass-addon-mbusd/build.yaml`.
Use the one that is most appropriate for your host computer.

### Sunsynk Multi
* Copy `options.json.template` to `options.json` and make changes to `options.json` to match your setup. Use `"PORT": "tcp://mbusd:502"` for the inverter port if you want to use the `mbusd` included in this docker compose stack. 
* Build the image `BUILD_FROM=homeassistant/amd64-base-python:3.9 docker compose build sunsynk-multi`
* Run the container `docker compose up -d sunsynk-multi`
* See the container logs `docker compose logs -f sunsynk-multi`

### Mbusd
* Edit `docker-compose.yaml` changing the values under `environment` to match your configuration, leaving the device set to `/dev/ttyUSB0` as we mount the correct port to this location in the next step.
* Under `volumes` change `/dev/ttyRS485` to the RS485 port of your host computer.
* Build the image `BUILD_FROM=homeassistant/amd64-base-python:3.9 docker compose build mbusd`
* Run the container `docker compose up mbusd`
* View container logs `docker compose logs -f mbusd`

Note: the options.json will use the port address `tcp://mbusd:502` to refer to this mbusd container. 