ARG BUILD_FROM
FROM ${BUILD_FROM}

RUN pip3 install sunsynk[pymodbus,umodbus,solarman]==0.5.6 --no-cache-dir --disable-pip-version-check

# Install sunsynk from local source
#! COPY sunsynk sunsynk
#! RUN pip3 install -e sunsynk[pymodbus,umodbus,solarman] --no-cache-dir --disable-pip-version-check

COPY rootfs /

#! RUN chmod a+x /etc/services.d/sunsynk/run
#! RUN chmod a+x /etc/services.d/sunsynk/finish
