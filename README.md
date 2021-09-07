# Sunsynk Hybrid Inverter **ALPHA**

Sunsynk Hybrid Inverter library for Python 3. The library is intended to integrate Sunsynk Inverters into Home Assistant.

See <https://www.sunsynk.org/> for more information on sunsynk inverters.

This code was developed on a Sunsynk 5.5 kWh

> DISCLAIMER: Use at your own risk! Especially when writing any settings.

## Tested Inverters

There are several inverters that are rebranded Deye inverters, so you might have success with other inverter brands as well, please add your inverter by editing tis file and creating a Pull Request if you have success

| Inverter Model | Battery     | Version  | User      |
| -------------- | ----------- | -------- | --------- |
| Sunsynk 5.5kW  | Hubble AM-2 | beta/all | @kellerza |

## Hardware

I used a RS485 adaptor sourced from Banggood, very similar to [this](https://www.robotics.org.za/RS485-MINI?search=rs485)

Mine is wired to the Sunsynk **BMS 485** port (top left). I also have a **RS485** port (bottom right) but this did not work.

The wiring and Ethernet color code according to TI-586A. The colours is probably not important, but it is important to use a twisted pair for RS485. Ideally always use either 586A/586B

| RJ45 Pin | RS485 adaptor | Color (586A) |
| -------- | ------------- | ------------ |
| 1        | B/D-          | Green-White  |
| 2        | A/D+          | Green        |

## Credits

Information in the Power forum was especially helpful to get this up and running, see [this thread](https://powerforum.co.za/topic/8646-my-sunsynk-8kw-data-collection-setup/)

Special Kudos to Bloubul7, @jacauc and Sc00bs

The original Node-RED flows can be found on @jacauc's repor [here](https://github.com/jacauc/SunSynk-NodeRed)
