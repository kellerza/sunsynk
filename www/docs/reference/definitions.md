## Sensor definitions

The sensor definition includes the modbus register number (or several registers), the name of the sensor, the unit and other optional parameters. For example:

```python
Sensor(183, "Battery voltage", VOLT, 0.01),
Sensor(184, "Battery SOC", "%"),
```

The last parameter in the battery sensor definition is a factor, in this case a value of 1 in the register represents 0.01V. When the factor is negative for normal sensors it indicates that the number in the register is Signed

When you add the *Battery voltage* sensor to your configuration you can use any of the following formats

```yaml
- battery_voltage
- Battery Voltage
- BATTERY_voltage
```

In the logs you will typically see the first format (no space and all lower case)

## Single Phase Inverter Sensor Definitions

These definitions apply to the single phase inverters. In the Home Assistant addon these are selected with the following configuration:

```yaml
SENSOR_DEFINITIONS: single-phase
```

These definitions can be view online at <https://github.com/kellerza/sunsynk/blob/main/sunsynk/definitions.py>

## Three Phase Inverter Sensor Definitions

These definitions apply to the three phase inverters. In the Home Assistant addon these are selected with the following configuration:

```yaml
SENSOR_DEFINITIONS: three-phase
```

These definitions can be view online at <https://github.com/kellerza/sunsynk/blob/main/sunsynk/definitions3ph.py>
