# Sensor modifiers

## Sensor modifiers - Min/Max/Now/Average/Step

Sensors fields can be modified by adding a modifier to the end of the field name.
Without any modifier, a [default modifier](https://github.com/kellerza/sunsynk/blob/main/hass-addon-sunsynk/filter.py#L135) will be added based on the field name.



| Modifier       | Description                                                                                                                                                                                    |
| -------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `:avg`         | the average over the last 60 seconds.                                                                                                                                                          |
| `:max`         | the maximum value over the last 60 seconds. Ideal for _counters_ where you are typically interested only in the last value.                                                                    |
| `:min`         | the minimum value over the last 60 seconds.                                                                                                                                                    |
| `:now`         | the maximum value over the last 2 seconds. Useful to see current sensor value.                                                                                                                 |
| `:round_robin` | cycle over all configured settings. Ideal for config settings.                                                                                                                                 |
| `:step`        | the average over the last minute will be reported, except if there is a significant change (>50) then it will be reported immediately. This is useful for automations using the current power. |
