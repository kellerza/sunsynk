ARG BUILD_FROM
FROM ${BUILD_FROM}

# RUN set -ex \
#    && ping dl-cdn.alpinelinux.org -c 4 \
#    && apk add --no-cache \
#        gcc libc-dev

#build-base
# RUN pip3 install --no-cache-dir paho-mqtt~=1.5.0 attrs pymodbus[repl] icecream pyserial-asyncio
RUN pip3 install --no-cache-dir paho-mqtt~=1.5.0 attrs pymodbus icecream pyserial-asyncio

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# local test - install sunsynk
COPY sunsynk /usr/src/app/sunsynk
RUN pip3 install -e sunsynk

COPY *.py ./

#CMD ["tail", "-f", "/dev/null"]
CMD ["./run.py"]
