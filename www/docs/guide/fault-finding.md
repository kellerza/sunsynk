# Fault finding

The addon follows the following process:
1. Load all your sensor definitions. The logs will show if you use any unknown or deprecated sensors
2. Read the Inverter's serial number (and rated power)

  If this read is successful, it will display the serial number
  ```
  INFO    ############################################################
  INFO                Inverter serial number '2105x0x0x0'
  INFO    ############################################################
  ```
3. Connect to the MQQT server
4. Publish the discovery data for Home Assistant, and also remove discovery data if required

After which it will continue to publish sensor data

If you fail to get a reply from the inverter, typically if step #2 fails, please check the following

## (a) Only a single connection to the serial port

Ensure you only have a single addon connected to the serial port. The following can all potentially access the USB port: mbusd, Node RED, the normal and dev addon version.

If you need to have multiple connections to the serial port: ONLY connect mbusd to the serial port. Connect all addons to mbusd (e.g. tcp://192.168.1.x:503 )

## (b) Check the Modbus Server ID

Ensure the Modbus Server ID (`MODBUS_ID` config setting) matches the configured **Modbus SN** value of the inverter. This value must not be zero.

View/update the Modbus server ID on your inverter under "Advanced Settings" / "Multi-Inverter"

<img src="https://github.com/kellerza/sunsynk/raw/main/images/modbus_sn.png" width="80%">

## (c) Reducing timeouts

If you get many timeouts, or if the addon does not read all your sensors on startup (i.e. you see **Retrying individual sensors** in the log), you can try the following:

- Set `READ_SENSORS_BATCH_SIZE` to a smaller value, i.e. 8
- The most reliable way to connect is to use mbusd to the serial port & connect the addon to mbusd at `tcp://<ip>:502`. The mbusd instance/addon can be on the same physical device or a remote device.

The hardware and cabling also has a big impact:

- Use a RJ45 converter with a GROUND pin. Ensure the ground is connected.
- Ensure the data line is on a twisted pair
- Re-crimp your RJ45 connector
- Use a good quality solid CAT5e/CAT6 cable
- Ensure your RS485 cable does not run parallel to other electrical cables (AC or DC), to reduce interference. e.g. in trunking
  - It could also help to use a shielded cable. Ground the shield at ONE end only (i.e. on the USB adaptor side and then just use normal platic RJ45 connector on the inverter side.
  - While fault finding use as short as possible cable, completely outside any sprague/trunking etc.

## (d) Check line voltage / termination resistor

If your RS485 adapter has a termination resistor (typically 120 ohms), try removing it.

To check, disconnect the adapter and use a multimeter to measure the resistance between A & B.

The d.c. voltage between A/B on the sunsynk RS485 connection should idle around 4-5v with nothing connected,
but this may drop to around 0.5v with the 120 ohm load.

RS485 devices are typically multi-drop with a termination resistor on the first and last devices.
However, the RS485 BMS port may only be intended to connect to a single device.

<img src="https://github.com/kellerza/sunsynk/raw/main/images/rs485-term.jpg">
