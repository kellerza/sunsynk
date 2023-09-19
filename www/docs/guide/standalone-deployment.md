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

* Copy `options.yaml.template` to `options.yaml` and make changes to `options.yaml` to match your setup. Use `PORT: tcp://mbusd:502` for the inverter port if you want to use the `mbusd` included in this docker compose stack.
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
The repo also contains prebuilt Docker images for Sunsynk Multi. You can see the different images [here](https://github.com/kellerza?tab=packages&repo_name=sunsynk).

### Docker-Compose examples:
#### amd64
``` yaml
services:
  sunsynk-multi:
    restart: unless-stopped
    image: ghcr.io/kellerza/hass-addon-sunsynk-multi/amd64:stable
    volumes:
      - ${PWD}/options.yaml:/usr/src/.local.yaml
```

#### aarch64
``` yaml
services:
  sunsynk-multi:
    restart: unless-stopped
    image: ghcr.io/kellerza/hass-addon-sunsynk-multi/aarch64:stable
    volumes:
      - ${PWD}/options.yaml:/usr/src/.local.yaml
```

#### armv7
``` yaml
services:
  sunsynk-multi:
    restart: unless-stopped
    image: ghcr.io/kellerza/hass-addon-sunsynk-multi/armv7:stable
    volumes:
      - ${PWD}/options.yaml:/usr/src/.local.yaml
```

### Docker CLI examples:

#### amd64
``` bash
docker run -d --name sunsynk-multi \
--restart unless-stopped \
-v ${PWD}/options.yaml:/usr/src/.local.yaml \
ghcr.io/kellerza/hass-addon-sunsynk-multi/amd64:stable
```

#### aarch64
``` bash
docker run -d --name sunsynk-multi \
--restart unless-stopped \
-v ${PWD}/options.yaml:/usr/src/.local.yaml \
ghcr.io/kellerza/hass-addon-sunsynk-multi/aarch64:stable
```

#### armv7
``` bash
docker run -d --name sunsynk-multi \
--restart unless-stopped \
-v ${PWD}/options.yaml:/usr/src/.local.yaml \
ghcr.io/kellerza/hass-addon-sunsynk-multi/armv7:stable
```


