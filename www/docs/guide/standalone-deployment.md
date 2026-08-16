# Run standalone using Docker

If you are running only Home Assistant Core, or do not have Home Assistant Supervisor, you can run
the Sunsynk Multi add-on as a standalone Docker service. It does not need Home Assistant Core,
Supervisor, or HAOS — only an MQTT broker to publish to.

A common setup is Docker Compose on a Raspberry Pi (or similar) with `mbusd` converting an RS-485
serial link to Modbus TCP.

## Example docker-compose.yaml

```yaml
services:
  sunsynk-multi:
    restart: unless-stopped
    image: ghcr.io/kellerza/hass-addon-sunsynk-multi:stable
    volumes:
      - ${PWD}/options.yaml:/data/options.yaml
      - /etc/localtime:/etc/localtime:ro  # map localtime for whenever - #670
      - ${PWD}/mysensors.py:/share/hass-addon-sunsynk/mysensors.py # custom sensors - optional

  mbusd:
    restart: unless-stopped
    image: 3cky/mbusd:0.5.3
    ports:
      - 502:502
    privileged: true
    volumes:
      - /dev/ttyRS485:/dev/ttyUSB0
      - ${PWD}/mbusd.conf:/etc/mbusd.conf
```

Notes:

* Pre-built images are on the
  [Github Container Registry](https://github.com/kellerza?tab=packages&repo_name=sunsynk).
* Tags `:stable` and `:edge` match the two add-ons (Multi and Edge).
* Change `/dev/ttyRS485` on the host side of the `mbusd` volume to your RS-485 serial device. Keep
  `/dev/ttyUSB0` as the path inside the container (see `mbusd.conf` below).
* For [custom sensors](../reference/mysensors.md), place `mysensors.py` next to `options.yaml` and
  mount it at **`/share/hass-addon-sunsynk/mysensors.py`**. Remove that volume line if you do not
  use custom sensors.

## Addon configuration — options.yaml

Create **options.yaml** next to your compose file:

```yaml
---
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

Adjust `INVERTERS` for your setup. `PORT: tcp://mbusd:502` reaches the `mbusd` service on the
Compose network (the service name is the hostname).

Set `MQTT_HOST` to your broker hostname. On a standalone stack that is usually another Compose
service name (for example `mqtt`), not `core-mosquitto` (that name is for Home Assistant OS
add-ons).

## Mbusd configuration — mbusd.conf

Create **mbusd.conf** next to your compose file (see also
[3cky/mbusd](https://github.com/3cky/mbusd)):

```conf
# Logging
loglevel = 2
logfile = -

# Serial port (device path inside the container)
device = /dev/ttyUSB0
speed = 9600
mode = 8N1

# TCP
address = 0.0.0.0
port = 502
timeout = 5
```

`device` must stay `/dev/ttyUSB0` when you use the volume mapping in the compose example. Baud rate
and mode should match your inverter’s RS-485 settings. `logfile = -` sends logs to stdout for
`docker compose logs`.

## Start the stack

```bash
docker compose up -d
docker compose logs -f
```

Or start services individually: `docker compose up -d mbusd sunsynk-multi`.

## Addon configuration — environment variables

Instead of (or in addition to) `options.yaml`, you can pass the same options as environment
variables. You must set `S6_KEEP_ENV=1` so the s6 init system forwards them (see
[s6-overlay](https://github.com/just-containers/s6-overlay#customizing-s6-overlay-behaviour)).

Minimal example (MQTT via env; other options still from `options.yaml`):

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

::: details Full example (all options via environment)

```yaml
services:
  sunsynk-multi:
    restart: unless-stopped
    image: ghcr.io/kellerza/hass-addon-sunsynk-multi:stable
    environment:
      MQTT_HOST: mqtt
      MQTT_PORT: 1883
      MQTT_USERNAME: ${MQTT_USER}
      MQTT_PASSWORD: ${MQTT_PASSWORD}
      S6_KEEP_ENV: 1
      SENSOR_DEFINITIONS: "single-phase"
      SENSORS: '["energy_management", "power_flow_card", "pv2_power"]'
      SENSORS_FIRST_INVERTER: '["settings"]'
      MANUFACTURER: "Sunsynk"
      READ_ALLOW_GAP: 2
      READ_SENSORS_BATCH_SIZE: 20
      NUMBER_ENTITY_MODE: "auto"
      INVERTERS: '[{"SERIAL_NR":"1234567890","HA_PREFIX":"SUN-10k-dsaxz","MODBUS_ID":1,"DONGLE_SERIAL_NUMBER":"1234567890","PORT":"solarman://192.168.1.123:8899"}]'
      SCHEDULES: '[{"key":"w","read_every":5,"report_every":60,"change_by":80,"change_percent":0,"change_any":0}]'
```

:::

### Environment variable notes

* Keys match `options.yaml`: uppercase with underscores (`SENSOR_DEFINITIONS`, `READ_ALLOW_GAP`, …).
* **INVERTERS** and **SCHEDULES** are JSON strings.
* For Solarman use `PORT` like `solarman://host:8899` (plus dongle serial); otherwise `tcp://`,
  `serial-tcp://`, `udp://`, or a serial device path.

## Docker CLI

Without Compose:

> ℹ️ **Note:** Replace `${PWD}` with the directory that contains your `options.yaml`.

```bash
docker run -d --name sunsynk-multi \
  --restart unless-stopped \
  -v ${PWD}/options.yaml:/data/options.yaml \
  ghcr.io/kellerza/hass-addon-sunsynk-multi:stable
```
