# Sunsynk Inverters

This repo enables access to Sunsynk Hybrid Inverter through a Python 3 library. It also provides an Add-On that can be installed in the Home Assistant OS.

See <https://www.sunsynk.org/> for more information on Sunsynk inverters.

This code was developed on a Sunsynk 5.5 kWh

> DISCLAIMER: Use at your own risk! Especially when writing any settings.

## Sunsynk Python Library

[![codecov](https://codecov.io/gh/kellerza/sunsynk/branch/main/graph/badge.svg?token=ILKRC5UTXI)](https://codecov.io/gh/kellerza/sunsynk)

The Python library is available through pip:

```bash
pip install sunsynk
```

## Home Assistant Sunsynk Add-On

For the Add-On you require Home Assistant OS and a RS-485 adaptor to connect to your Sunsynk inverter. Sensors are read using the Modbus protocol and sent to a MQTT server. Below an example of the HomeAssistant Energy management dashboard using sensors from the Sunsynk.

![HASS Energy management](./hass-addon-sunsynk/energy.png)

### Add-On Installation

1. Add the repository to your Supervisor
   <br>[![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fkellerza%2Fsunsynk)
   `https://github.com/kellerza/sunsynk` <br><br>
2. Install the Sunsynk Add-On from the **Add-On Store** and configure through the UI

## Tested Inverters

There are several inverters that are rebranded Deye inverters, so you might have success with other inverter brands as well, please add your inverter by editing tis file and creating a Pull Request if you have success

| Inverter Model | Battery     | Version  | User      |
| -------------- | ----------- | -------- | --------- |
| Sunsynk 5.5kW  | Hubble AM-2 | beta/all | @kellerza |

## Hardware

I used a RS485 adaptor sourced from Banggood, very similar to [this](https://www.robotics.org.za/RS485-MINI?search=rs485)

Mine is wired to the Sunsynk **BMS 485** port (top left). I also have a **RS485** port (bottom right) but this did not work.

The wiring and Ethernet color code to an RJ-45 plug crimped according to TI-568A. RJ45 requires a twisted pair, but you can use either TI-568A or TI-568B

| RJ45 Pin | RS485 adaptor | Color (568A) |
| -------- | ------------- | ------------ |
| 1        | B/D-          | Green-White  |
| 2        | A/D+          | Green        |

## Credits

Information in the Power forum was especially helpful to get this up and running, see [this thread](https://powerforum.co.za/topic/8646-my-sunsynk-8kw-data-collection-setup/)

Special Kudos to Bloubul7, @jacauc and Sc00bs

The original Node-RED flows can be found on @jacauc's repo [here](https://github.com/jacauc/SunSynk-NodeRed)
