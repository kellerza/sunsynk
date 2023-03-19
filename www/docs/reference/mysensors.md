# Custom Sensors

You can add custom sensors by creating a sensors definition file called in `/share/hass-addon-sunsynk/mysensors.py`

The `/share/` folder can be accessed through the Samba addon in Home Assistant. You can create the `hass-addon-sunsynk` folder & the `mysensors.py` file

This is a Python file and follows the same logic as the definitions.py & definitions3p.py. It exposes a single `SENSORS` global variable to which you can add the individual sensor definitions.

An example `mysensors.py` file:

```python
from sunsynk import AMPS, CELSIUS, KWH, VOLT, WATT
from sunsynk.rwsensors import NumberRWSensor, SelectRWSensor, TimeRWSensor
from sunsynk.sensors import (
    MathSensor,
    Sensor,
    SensorDefinitions,
    TempSensor,
)

SENSORS = SensorDefinitions()

SENSORS += Sensor(178, "My Custom Sensor", WATT, -1)
```

Once you have a file, you will see it in your addon's startup log:

```
2023-03-19 16:25:00,156 INFO    Importing /share/hass-addon-sunsynk/mysensors.py...
2023-03-19 16:25:00,158 INFO      custom sensors: my_custom_sensor
```

## Using the sensor

Once the sensor is available, you can add it to your configuration:

```
SENSORS:
 - my_custom_sensor
```