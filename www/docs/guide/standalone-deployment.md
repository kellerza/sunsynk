# Run standalone using docker compose

If you are running only Home Assistant Core, or do not have Home Assistant Supervisor,
you might want to run this addon as a standalone service.
Docker Compose is commonly used to manage services that run in docker containers.

As a standalone service, this addon does not depend on Home Assistant Core, Supervisor or OS.
You can run this addon and send data to any MQTT server without using other HA services.

Another benefit of this setup is to run this addon along with `mbusd` on a
Raspberry Pi without having to install Home Assistant on it.

## Local Docker-Compose Builds

In these example commands we prefix the `docker-compose build` commands with the
environment variable definition `BUILD_FROM=...`,
which specifies which base image is used. For a Raspberry Pi you would need to
use `BUILD_FROM=homeassistant/armhf-base-python:3.9`, and for a 64bit PC you
would use `BUILD_FROM=homeassistant/amd64-base-python:3.9`.
A list of available base images can be found in
`hass-addon-sunsynk-multi/build.yaml` and `hass-addon-mbusd/build.yaml`.
Use the one that is most appropriate for your host computer.

### Sunsynk Multi

::: details **options.yaml** example

Create your own `options.yaml` file with the following content:

```yaml
---
DRIVER: "pymodbus"
INVERTERS:
  - SERIAL_NR: "007"
    HA_PREFIX: SS
    MODBUS_ID: 1
    DONGLE_SERIAL_NUMBER: "0"
    PORT: tcp://mbusd:502
SENSOR_DEFINITIONS: single-phase
SENSORS:
  - energy_management
  - power_flow_card
  - pv2_power
SENSORS_FIRST_INVERTER:
  - settings
MANUFACTURER: Sunsynk
READ_ALLOW_GAP: 2
READ_SENSORS_BATCH_SIZE: 20
SCHEDULES:
  - KEY: W
    READ_EVERY: 5
    REPORT_EVERY: 60
    CHANGE_ANY: false
    CHANGE_BY: 80
    CHANGE_PERCENT: 0
NUMBER_ENTITY_MODE: "auto"
MQTT_HOST: core-mosquitto
MQTT_PORT: 1883
MQTT_USERNAME: hass
MQTT_PASSWORD: ""
# DEBUG: 0
# DEBUG_DEVICE: "/dev/ttyAMA0"
```

Adjust the `INVERTERS` section to match your inverter setup. `tcp://mbusd:502` points toward a DNS entry, or most likely container named `mbusd` included in this docker compose stack.

:::

* Build the image `BUILD_FROM=<base_image> docker compose build sunsynk-multi`
* Run the container `docker compose up -d sunsynk-multi`
* See the container logs `docker compose logs -f sunsynk-multi`

### Mbusd

* Edit `docker-compose.yaml` changing the values under `environment` to match your configuration, leaving the device set to `/dev/ttyUSB0` as we mount the correct port to this location in the next step.
* Under `volumes` change `/dev/ttyRS485` to the RS485 port of your host computer.
* Build the image `BUILD_FROM=<base_image> docker compose build mbusd`
* Run the container `docker compose up mbusd`
* View container logs `docker compose logs -f mbusd`

## Using Pre-built Docker Images

The repo also contains prebuilt Docker images for Sunsynk Multi. You can see the different images for the various supported architectures [here](https://github.com/kellerza?tab=packages&repo_name=sunsynk).

### Docker-Compose examples:

#### amd64

``` yaml
services:
  sunsynk-multi:
    restart: unless-stopped
    image: ghcr.io/kellerza/hass-addon-sunsynk-multi/amd64:stable
    volumes:
      - ${PWD}/options.yaml:/data/options.yaml
```

#### aarch64

``` yaml
services:
  sunsynk-multi:
    restart: unless-stopped
    image: ghcr.io/kellerza/hass-addon-sunsynk-multi/aarch64:stable
    volumes:
      - ${PWD}/options.yaml:/data/options.yaml
```

#### armv7

``` yaml
services:
  sunsynk-multi:
    restart: unless-stopped
    image: ghcr.io/kellerza/hass-addon-sunsynk-multi/armv7:stable
    volumes:
      - ${PWD}/options.yaml:/data/options.yaml
```

### Docker CLI examples

Below are examples using the docker CLI.

> ℹ️ **Note:** Replace ${PWD} with the path to the location of your `options.yaml` file.

#### amd64

``` bash
docker run -d --name sunsynk-multi \
--restart unless-stopped \
-v ${PWD}/options.yaml:/data/options.yaml \
ghcr.io/kellerza/hass-addon-sunsynk-multi/amd64:stable
```

#### aarch64

``` bash
docker run -d --name sunsynk-multi \
--restart unless-stopped \
-v ${PWD}/options.yaml:/data/options.yaml \
ghcr.io/kellerza/hass-addon-sunsynk-multi/aarch64:stable
```

#### armv7

``` bash
docker run -d --name sunsynk-multi \
--restart unless-stopped \
-v ${PWD}/options.yaml:/data/options.yaml \
ghcr.io/kellerza/hass-addon-sunsynk-multi/armv7:stable
```
