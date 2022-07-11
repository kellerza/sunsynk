ARG BUILD_FROM
FROM ${BUILD_FROM}

# Required for the Debian base
#   https://packages.debian.org/bullseye/python3-dev
# RUN apt-get update && apt-get install -y \
#     python3-dev=3.9.2-3 \
#     python3-pip \
#   && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir --disable-pip-version-check paho-mqtt~=1.5.0 pyyaml~=5.4.1 sunsynk[pymodbus,umodbus]==0.2.0

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY . ./

# local test - install sunsynk
# RUN pip3 install -e sunsynk[pymodbus,umodbus]

#CMD ["tail", "-f", "/dev/null"]
CMD ["./run.py"]
