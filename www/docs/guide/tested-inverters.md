# Tested Inverters

There are several inverters that are rebranded Deye inverters, so you might have success with other inverter brands as well, please add your inverter by editing this file and creating a Pull Request if you are successful.

| Inverter Model | Battery           | Version  | User          | Port(s)                  |
| -------------- | ----------------- | -------- | ------------- | ------------------------ |
| Sunsynk 3.6kW  | Sunsynk SSLB1     | beta/all | @reedy        | BMS485 (top left)        |
| Sunsynk 3.6kW Ecco | Sunsynk Sun-Batt 5.12 | multi | @Fr3d | RS485/CAN (top left)     |
| Sunsynk 5.5kW  | Hubble AM-2       | beta/all | @kellerza     | BMS485 (top left)        |
| Sunsynk 8.8kW  | BSL 8.2 kWH       | 0.0.8    | @dirkackerman | RS485 (1 in image below) |
| Deye  8kW      | Pylontech US3000C | 0.1.3dev | @Kladrie      | RS485 (top left)         |
| Turbo-E   5kW  | DIY with JKBMS    | 0.1.4    | @agtconf      | BMS485 (top left)        |

### Sunsynk 3.6kW Inverter

<img src="https://github.com/kellerza/sunsynk/raw/main/images/inv-ss-3-6kw.png" width="80%">

### Sunsynk Ecco 3.6kW Hybrid Inverter

Model number: `SUN-3.6K-SG04LP1-EU`

This likely applies to similar models in the Ecco range: `SUN-3K-SG04LP1-24-EU / SUN-3K-SG04LP1-EU / SUN-5K-SG04LP1-EU / SUN-6K-SG04LP1-EU`

The Ecco inverters have a combined RS485 and CAN-BUS port. If your battery is already using the port for its CAN-BUS communications, an RJ45 splitter is required to separate the communications between RS485 and CAN-BUS.
[SolarAssistant have a helpful page](https://solar-assistant.io/help/deye/2_in_1_bms_port) that explains the wiring of the port and the splitter required.

<img src="https://github.com/kellerza/sunsynk/raw/main/images/inv-ss-ecco-3-6kw.png" width="80%">

[Closer view of the RS485/CAN port](https://github.com/kellerza/sunsynk/raw/main/images/inv-ss-ecco-3-6kw-485can.png)

### Sunsynk 5.5kW Inverter

Tested with: USB-to-RS485 adaptor sourced from Banggood, very similar to [this](https://www.robotics.org.za/RS485-MINI?search=rs485).

NOTE: RJ-45 port marked **RS485** (bottom right) does not work.

### Sunsynk 8.8kW Inverter

<img src="https://github.com/kellerza/sunsynk/raw/main/images/inv-ss-8kw.png" width="80%">

Tested with: USB-to-485 adaptor sourced from Micro Robotics, [here](https://www.robotics.org.za/index.php?route=product/product&product_id=5947)

### Deye 8kW Inverter

<img src="https://github.com/kellerza/sunsynk/raw/main/images/inv-deye-8kw.png" width="80%">

RS485 is the blue line - top left, as with the Sunsynk inverters. Yellow is the CAN-comms with the Pylontech batteries

### Turbo-Energy 5kW Inverter

Tested with: USB-to-RS485 adaptor sourced from Aliexpress, very similar to [this](https://www.robotics.org.za/RS485-3P).
