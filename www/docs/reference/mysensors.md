# Custom Sensors

You can add custom sensors by creating a sensors definition file called in `/share/hass-addon-sunsynk/mysensors.py`.

In it's most basic form a sensor the RS486 register and a name. You can find the RS485 protocol document at various places online, search the [Power Forum](https://www.powerforum.co.za) or [Github issue #59](https://github.com/kellerza/sunsynk/issues/59)

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

```txt
2023-03-19 16:25:00,156 INFO    Importing /share/hass-addon-sunsynk/mysensors.py...
2023-03-19 16:25:00,158 INFO      custom sensors: my_custom_sensor
```

## Using the sensor

Once a sensor is loaded, you still have to add it to your configuration:

```yaml
SENSORS:
 - my_custom_sensor
```

You can also add **all** the custom sensors, using the special group called `mysensors`.

```yaml
SENSORS:
  - mysensors
```

## More examples

### Time sensor

::: info
Write is only partially implemented in the example below
:::

::: details

```python
import attr
import re

# from sunsynk import AMPS, CELSIUS, KWH, VOLT, WATT
from sunsynk.rwsensors import RWSensor, ResolveType
from sunsynk.sensors import RegType, ValType, SensorDefinitions

SENSORS = SensorDefinitions()


@attr.define(slots=True, eq=False)
class SystemTimeRWSensor(RWSensor):
    """Read & write time sensor."""

    def value_to_reg(self, value: ValType, resolve: ResolveType) -> RegType:
        """Get the reg value from a display value."""
        redt = re.compile(r"(2\d{3})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})")
        match = redt.fullmatch(value)
        if not match:
            raise ValueError("Invalid datetime {value}")
        y, m, d = int(match.group(1)) - 2000, int(match.group(2)), int(match.group(3))
        h, mn, s = int(match.group(4)), int(match.group(5)), int(match.group(6))
        regs = (
            (y << 8) + m,
            (d << 8) + h,
            (mn << 8) + s,
        )
        raise ValueError(f"{y}-{m:02}-{d:02} {h}:{mn:02}:{s:02} ==> {regs}")
        return regs

    def reg_to_value(self, regs: RegType) -> ValType:
        """Decode the register."""
        y = ((regs[0] & 0xFF00) >> 8) + 2000
        m = regs[0] & 0xFF
        d = (regs[1] & 0xFF00) >> 8
        h = regs[1] & 0xFF
        mn = (regs[2] & 0xFF00) >> 8
        s = regs[2] & 0xFF
        return f"{y}-{m:02}-{d:02} {h}:{mn:02}:{s:02}"


SENSORS += SystemTimeRWSensor((22, 23, 24), "Date", unit="")
```

:::
