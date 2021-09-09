ARG BUILD_FROM
FROM ${BUILD_FROM}

RUN pip3 install --no-cache-dir paho-mqtt~=1.5.0 attrs pymodbus sunsynk icecream

RUN set -ex \
    && ping dl-cdn.alpinelinux.org -c 4 \
    && apk add --no-cache \
        git

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY config.ini *.py ./

# CMD ["tail", "-f", "/dev/null"]
CMD ["./run.py"]
