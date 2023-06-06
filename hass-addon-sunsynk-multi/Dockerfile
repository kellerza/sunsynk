ARG BUILD_FROM
FROM ${BUILD_FROM}

COPY requirements.txt .
RUN pip3 install -r requirements.txt

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY . ./

CMD ["./run.py"]
