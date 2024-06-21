# Schedules

Schedules gives you a flexible way to define when to read sensors from the inverter and when to report these sensors to MQTT (or Home Assistant). The same schedule can apply to many sensors.

The default behaviour, without any configuration override will assign the following schedules to the sensors:

```text
+-----------+-----+------+--------+-----------+----------+------------+
|    Key    | src | Read | Report | Change by | Change % | Change any |
+-----------+-----+------+--------+-----------+----------+------------+
| date_time |     |  60  |   60   |           |          |    True    |
|     rw    |     |  5   |  300   |           |          |    True    |
|     w     |     |  5   |   60   |     80    |          |            |
|    kwh    |     | 300  |  300   |           |          |            |
|  any_unit |     |  15  |  300   |           |          |            |
|  no_unit  |     |  15  |  300   |           |          |    True    |
+-----------+-----+------+--------+-----------+----------+------------+
```

What this means is that:

1. Specific sensors, based on the sensor's name
   - Read & report the `date_time` sensor every minute
2. Configuration sensors (`key = 'rw'`):
   - Read every 5 seconds, report every 5 minutes. If there is any change, report immediately.
3. Based on the sensor's unit
   - For sensors with a unit of `W`, read every 5 seconds, and report every minute. If there is a significant change of 80Watts report immediately.
   - For sensors with a unit of `kWH`, read & report every 5 minutes. These are typically used by Home Assistant's Energy Management and aggregated every hour, so you really don't need to update them often.
4. Sensors with any unit (`key = 'any_unit'`)
   - Read every 15 seconds and report the avreage every 60 seconds.
5. Sensors without a unit (`key = 'no_unit'`)
   - Read every 15 seconds, report every 5 minutes, or if there is any change.

You can add any (more specific) schedule and even override the defaults in the configuration.

::: info
Sensor modifiers have been replaced with schedules.
:::

## Schedule entries

A schedule entry is defined with the following fields:

| Field                      | Description                                                                                                           |
|----------------------------|-----------------------------------------------------------------------------------------------------------------------|
| KEY                        | The sensor name, unit or one of the special keys. See [keys](#keys)                                                   |
| READ_EVERY                 | Read the sensor every x seconds.                                                                                      |
| REPORT_EVERY               | Report the sensor value to MQTT every x seconds.                                                                      |
| CHANGE_ANY                 | Report the value immediately upon any change. Useful for configuration and text based sensors. (true/false)                        |
| CHANGE_BY         | Report the sensor when there is a significant change. Example. Report power immedialtely when the power changes by x. |
| CHANGE_PERCENT | Report when there is an x percent change in the sensor value.                                                         |

## Keys

The `KEY` value of the sensor is used to identify sensors, these are show in the table below. The key is unique and can be used to change the default behaviour.

| Order | Key value  | Description                                                                                |
|-------|------------|--------------------------------------------------------------------------------------------|
| 1     | *name*     | A specific name of a sensor.                                                               |
| 2     | `rw`       | Read & write sensors (RWSensors in the definitions). Used for all configuration            |
| 3     | *unit*     | A Sensor unit. Can be W, kWh, V, A, etc                                                    |
| 4     | `any_unit` | A catch-all for sensors with any unit. These are typically numerical sensors of some type. |
| 5     | `no_unit`  | A catch-all for sensors without any unit. Typically non-numeric sensors.                   |

To find a  schedule for any specific sensor, the search order in column 1 will be followed. This allows you to be very specific for sensors with a proper name, or be very generic for sensors with & without units.

## Proposed schedule overrides for Solarman

When using the `solarman` driver, the Solarman dongle can be overwhelmed when constantly being read. Ideally you should not read more than once every 10 seconds.

The following schedule overrides are recommended for Solarman:

```yaml
SCHEDULES:
- KEY: W
  READ_EVERY: 15
  REPORT_EVERY: 60
  CHANGE_BY: 80
- KEY: RW
  READ_EVERY: 15
  REPORT_EVERY: 60
  CHANGE_ANY: true
- KEY: any_unit
  READ_EVERY: 30
  REPORT_EVERY: 60
  CHANGE_BY: 80
```

An Example to change the battery sensor to update on all changes, including changing the read time to 30s instead of the default 15s.
```yaml
- KEY: "%"
  READ_EVERY: 30
  REPORT_EVERY: 300
  CHANGE_ANY: true
```
you can also use the sensors name 'battery_soc'
