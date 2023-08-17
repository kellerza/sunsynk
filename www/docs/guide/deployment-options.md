# Deployment options

If the Inverter is close to your server/SBC running Home Assistant, you can use the standard deployment option, else you can extend the RS485 over Ethernet via a gateway or even MQTT

1. Standard

   The Sunsynk Add-on runs on the Home Assistant OS, reads the Inverter's Modbus registers over RS-485, and publishes sensor values to the MQTT server.
   The architecture is shown below:

   ![Deployment Option](https://github.com/kellerza/sunsynk/raw/main/images/deploy.png)

2. A Modbus TCP to RTU/serial gateway

   This can be another Raspberry Pi, even an old one, running the gateway software, like [mbusd](./mbusd).

   You can also use a commercial Modbus gateway, like the USR-W630

   ![Deployment Option Gateway](https://github.com/kellerza/sunsynk/raw/main/images/deploy-gw.png)

3. Extend with an MQTT gateway

   This remote option runs the Sunsynk Addon close to the Inverter, and then sends MQTT messages over your network toward the MQTT server (typically on the same server as Home Assistant)

   ![Deployment Option MQTT](https://github.com/kellerza/sunsynk/raw/main/images/deploy-mqtt.png)

4. Standalone in Docker

   This runs the addon on its own in a docker container, without depending on Home Assistant

   Read more [here](./standalone-deployment).

   ![Deployment Option Standalone](https://github.com/kellerza/sunsynk/raw/main/images/deploy-standalone.png)
