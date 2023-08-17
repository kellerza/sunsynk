# Sensors

You can add sensors under the `SENSORS` and `SENSORS_FIRST_INVERTER` keys in the configuration.

The page does not list all the sensors available, only the most frequently used ones. You might have to explore the sensor definitions for available sensors, or even the Modbus protocol document to add your own definitions.

## Sensor groups

Sensors groups will allow you to add several sensors with a single sensor entry.

### Energy management

These sensors are mostly related to energy or kWh and required for the Home Assistant [Energy Management](../guide/energy-management)

```yaml
SENSORS:
  - energy_management
```

::: details Sensors included

```yaml
total_battery_charge
total_battery_discharge
total_grid_export
total_grid_import
total_pv_energy
```

:::

### Power flow card: `power_flow_card`

These are all sensors used by the [Power Flow Card](../examples/lovelace#sunsynk-power-flow-card)

```yaml
SENSORS:
  - power_flow_card
```

::: details Sensors included

```yaml
aux_power
battery_current
battery_power
battery_soc
battery_voltage
day_battery_charge
day_battery_discharge
day_grid_export
day_grid_import
day_load_energy
day_pv_energy
essential_power
grid_connected
grid_ct_power
grid_frequency
grid_power
grid_voltage
inverter_current
inverter_power
load_frequency
non_essential_power
overall_state
priority_load
pv1_current
pv1_power
pv1_voltage
use_timer
```

:::

### Settings

Sensors used for changing the System Operating Mode - see [here](../examples/lovelace-settings)

These can be under `SENSORS` or `SENSORS_FIRST_INVERTER`

```yaml
SENSORS_FIRST_INVERTER:
  - settings
```

::: details Sensors included

```yaml
prog1_capacity
prog1_charge
prog1_time
prog2_capacity
prog2_charge
prog2_time
prog3_capacity
prog3_charge
prog3_time
prog4_capacity
prog4_charge
prog4_time
prog5_capacity
prog5_charge
prog5_time
prog6_capacity
prog6_charge
prog6_time
```

:::

### Custom Sensors

If you have [custom sensors](./mysensors), you can add them all with the `mysensors` group.

```yaml
SENSORS:
  - mysensors
```

## Sensor definitions

The sensor definition includes the modbus register number (or several registers), the name of the sensor, the unit and other optional parameters. For example:

```python
Sensor(183, "Battery voltage", VOLT, 0.01),
Sensor(184, "Battery SOC", "%"),
```

The last parameter in the battery sensor definition is a factor, in this case a value of 1 in the register represents 0.01V. When the factor is negative for normal sensors it indicates that the number in the register is Signed

When you add the *Battery voltage* sensor to your configuration you can use any of the following formats

```yaml
SENSORS:
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

These definitions can be viewed online at <https://github.com/kellerza/sunsynk/blob/main/sunsynk/definitions.py>

## Three Phase Inverter Sensor Definitions

These definitions apply to the three phase inverters. In the Home Assistant addon these are selected with the following configuration:

```yaml
SENSOR_DEFINITIONS: three-phase
```

These definitions can be viewed online at <https://github.com/kellerza/sunsynk/blob/main/sunsynk/definitions3ph.py>
