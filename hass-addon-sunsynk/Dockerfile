ARG BUILD_FROM
FROM ${BUILD_FROM}

# RUN set -ex \
#    && ping dl-cdn.alpinelinux.org -c 4 \
#    && apk add --no-cache \
#        gcc libc-dev
RUN pip3 install --no-cache-dir paho-mqtt~=1.5.0 sunsynk[pymodbus]==0.1.3

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY . ./

# local test - install sunsynk
# RUN pip3 install -e sunsynk

#CMD ["tail", "-f", "/dev/null"]
CMD ["./run.py"]
