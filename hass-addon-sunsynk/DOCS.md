# Configuration

## Parameters

- `MQTT_*`

  You will need a working MQTT sevrer since all values will be sent via MQTT.
  The default configuration assumes the Mosquitto broker add-on and you simply have to
  fill in your password.

- `SENSORS`

  A list of sensors to poll. You can use any sensor defined in the sunsynk Python library - [here](https://github.com/kellerza/sunsynk/blob/main/sunsynk/definitions.py)

- `DEBUG`

  The values received will continuously be printed to the add-on's log. This will confirm
  that you receive values.

  The serial device

- SUNSYNK ID

  A unique Identifier for all values from this Sunsynk Inverter

<!--
## Sensor modifiers - Min/Max/Average/Smart

Sensors fields can be modified by adding a modifier to the end of the field name.
Without any modifier, the sensor will have a smart interval.
The average will be reported every 60 seconds.
will be reported immediately.
These type of fields can be used in automations that will respond within the measurement
interval of the SMA Energy meter (1 second)

Other modifiers

| Modifier | Description                                                                                                                      |
| -------- | :------------------------------------------------------------------------------------------------------------------------------- |
| `:max`   | the maximum value over the last 60 seconds. <br/> Ideal for _counters_ where you are typically interested only in the last value |
| `:min`   | the minimum value over the last 60 seconds.                                                                                      |
| `:<s>`   | any integer will allow you to get the average over the indicated amount of seconds. `:5`=5 seconds, `:60`=60 seconds             |

## Home Assistant Utility meter

The utility meter can be used to calaculate kwH usage per-day and per-month on
consume**counter** fields

Add a **FIELDS** entry: `pconsumecounter:max` will give you the max counter value over
the last 60 seconds

The utility meter will record these values and give you total energy used (kWh) every
day and every month.

Example utility meter configuration.

```yaml
utility_meter:
  sma_daily_total:
    source: sensor.pconsumecounter
    cycle: daily
  sma_monthly_total:
    source: sensor.pconsumecounter
    cycle: monthly
```
-->
