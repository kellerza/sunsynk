ARG BUILD_FROM
FROM ${BUILD_FROM}

# Required for the Debian base
#   https://packages.debian.org/bullseye/python3-dev
# RUN apt-get update && apt-get install -y \
#     python3-dev=3.9.2-3 \
#     python3-pip \
#   && rm -rf /var/lib/apt/lists/*

# RUN python3 -m pip install --no-cache-dir --disable-pip-version-check paho-mqtt~=1.5.0 async_modbus umodbus sunsynk==0.1.3
RUN python3 -m pip install --no-cache-dir --disable-pip-version-check paho-mqtt~=1.5.0 connio umodbus async_modbus sunsynk==0.1.3

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY . ./

# local test - install sunsynk
# RUN pip3 install -e sunsynk

#CMD ["tail", "-f", "/dev/null"]
CMD ["./run.py"]
