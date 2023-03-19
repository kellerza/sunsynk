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


## Connect to your Inverter with RS485
RS485 requires a twisted pair, this works with CAT5 network cable and RJ-45 connectors.

If the RJ-45 connector on the inverter side is crimped according to [T568A](https://en.wikipedia.org/wiki/ANSI/TIA-568#Wiring), you can use the pinout in the following table.

| RJ45 Pin<br>(inverter side) | Wire Color<br>(when using T568A) | RS485<br>pins |
| :-------------------------: | :------------------------------: | :-----------: |
|              1              |           Green-White            |     B/D-      |
|              2              |              Green               |     A/D+      |
|              3              |           Orange-White           |      GND      |

### USB-to-RS485 adaptors

1. Wave USB-to-RS485 [example](https://www.robotics.org.za/W17286)

   This is my preferred adaptor. It includes a GND and lightning/ESD protection, TVS diodes and a resettable fuse.

   Wave also has a RS485-to-Ethernet module. (not tested)

   <img src="https://github.com/kellerza/sunsynk/raw/main/images/usb-wave-rs485.jpg" width="55%">

1. USB-to-RS485 adaptor with cable [example](https://www.robotics.org.za/index.php?route=product/product&product_id=5947)

   Includes a GND and TVS diode and USB self recovery options.

   <img src="https://github.com/kellerza/sunsynk/raw/main/images/usb-rs485-cable.jpg" width="55%">

Other tested adaptors
- USB-to-RS485 3 Pin adaptor [example](https://www.robotics.org.za/RS485-3P)

  Includes a GND and TVS diode and USB self recovery options.


- 2-Wire USB-to-RS485 [example](https://www.robotics.org.za/RS485-MINI)

  This is the adaptor I started with. It works, but does not include a GND, so your success might vary.

  <img src="https://github.com/kellerza/sunsynk/raw/main/images/usb-rs485-rj45.png" width="35%">

### RS485 gateways

1. USR-W630 Wifi-to-RS485

   This is a tested Wifi-to-RS485 gateway, which also includes a GND.

   Requires `READ_SENSORS_BATCH_SIZE` set to 8 or less

2. HF5142B  Modbus/serial to ethernet (4x RS232/485/422 to 4x E-Ports)

   ![settings](https://github.com/kellerza/sunsynk/raw/main/images/eth-hf5142.png)

   This gateway was tested with the Deye 8k EU Hybrid inverter. The following serial settings were used:

   <img src="https://github.com/kellerza/sunsynk/raw/main/images/eth-hf5142-settings.png" width="80%" alt="settings">
