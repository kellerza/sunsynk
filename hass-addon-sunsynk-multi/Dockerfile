ARG BUILD_FROM
FROM ${BUILD_FROM}

RUN pip3 install --no-cache-dir --disable-pip-version-check \
    sunsynk[pymodbus,umodbus]==0.4.0 \
    mqtt-entity==0.0.3 \
    pysolarmanv5==3.0.0 \
    pyyaml==6.0.1

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY . ./

# local test - install sunsynk
# RUN pip3 install -e sunsynk[pymodbus,umodbus]

#CMD ["tail", "-f", "/dev/null"]
CMD ["./run.py"]
