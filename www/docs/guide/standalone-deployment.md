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
use `BUILD_FROM=ghcr.io/home-assistant/armhf-base-python:3.12`, and for a 64bit PC you
would use `BUILD_FROM=ghcr.io/home-assistant/amd64-base-python:3.12`.
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

### Docker-Compose examples

#### amd64 / aarch64 / armv6 / armv7

```yaml
services:
  sunsynk-multi:
    restart: unless-stopped
    image: ghcr.io/kellerza/hass-addon-sunsynk-multi:stable
    volumes:
      - ${PWD}/options.yaml:/data/options.yaml
```

```yaml
services:
  sunsynk-multi:
    restart: unless-stopped
    image: ghcr.io/kellerza/hass-addon-sunsynk-multi:stable
    volumes:
      - ${PWD}/options.yaml:/data/options.yaml
    environment:
      MQTT_HOST: mqtt
      MQTT_PORT: 1883
      MQTT_USERNAME: ${MQTT_USER}
      MQTT_PASSWORD: ${MQTT_PASSWORD}
      S6_KEEP_ENV: 1
```

For env vars to work, you need to add one additional env var (more [here](https://github.com/just-containers/s6-overlay#customizing-s6-overlay-behaviour))

```yaml
S6_KEEP_ENV: 1
```

### Docker CLI examples

Below are examples using the docker CLI.

> ℹ️ **Note:** Replace `${PWD}` with the path to the location of your `options.yaml` file.

#### CLI: amd64 / aarch64 / armv6 / armv7

```bash
docker run -d --name sunsynk-multi \
--restart unless-stopped \
-v ${PWD}/options.yaml:/data/options.yaml \
ghcr.io/kellerza/hass-addon-sunsynk-multi:stable
```

## Using Environment Variables with Docker Compose

If you prefer to use environment variables instead of an `options.yaml` file, you can configure the Sunsynk Multi service entirely with environment variables. All configuration options that would normally be set in the `options.yaml` file can be set as environment variables.

### Example Configuration

Here is an example of how to run the Sunsynk Multi service using environment variables in a `docker-compose.yml` file:

```yaml
services:
  sunsynk-multi-amd64:
    restart: unless-stopped
    profiles: ['sunsynk-amd64']
    image: ghcr.io/kellerza/hass-addon-sunsynk-multi:stable
    environment:
      MQTT_HOST: mqtt
      MQTT_PORT: 1883
      MQTT_USERNAME: ${MQTT_USER}
      MQTT_PASSWORD: ${MQTT_PASSWORD}
      S6_KEEP_ENV: 1
      DRIVER: "pymodbus"
      SENSOR_DEFINITIONS: "single-phase"
      SENSORS: '["energy_management", "power_flow_card", "pv2_power"]'
      SENSORS_FIRST_INVERTER: '["settings"]'
      MANUFACTURER: "Sunsynk"
      READ_ALLOW_GAP: 2
      READ_SENSORS_BATCH_SIZE: 20
      NUMBER_ENTITY_MODE: "auto"
      INVERTERS: '[{"SERIAL_NR":"1234567890","HA_PREFIX":"SUN-10k-dsaxz","MODBUS_ID":1,"DONGLE_SERIAL_NUMBER":"1234567890","PORT":"tcp://192.168.1.123:8899"}]'
      SCHEDULES: '[{"key":"w","read_every":5,"report_every":60,"change_by":80,"change_percent":0,"change_any":0}]'
```

### Explanation of Environment Variables

* **MQTT_HOST**: The MQTT broker host.
* **MQTT_PORT**: The MQTT broker port (typically 1883).
* **MQTT_USERNAME**: The username for the MQTT broker.
* **MQTT_PASSWORD**: The password for the MQTT broker.
* **S6_KEEP_ENV**: Set to `1` to ensure environment variables are passed to the container processes when using the `s6` init system.
* **DRIVER**: The driver to use for modbus communication (e.g., `pymodbus`, `umodbus`).
* **INVERTERS**: A JSON string representing the configuration for your inverters. Adjust the values for `SERIAL_NR`, `HA_PREFIX`, `MODBUS_ID`, `DONGLE_SERIAL_NUMBER`, and `PORT` to match your setup.
* **SCHEDULES**: A JSON string representing the schedules for sensor reading and reporting.
* **Other Configuration Options**: Any other configuration option that is typically defined in `options.yaml` can be passed as an environment variable. The keys from `options.yaml` should be written in uppercase and underscores (e.g., `SENSOR_DEFINITIONS`, `READ_ALLOW_GAP`, `SENSORS`, etc.).
