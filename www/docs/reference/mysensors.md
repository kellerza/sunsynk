# Custom Sensors

You can create custom sensors by defining them in a file called `mysensors.py` in the `/share/hass-addon-sunsynk/` directory. This allows you to add sensors that are not included in the default definitions.

In it's most basic form a sensor the RS486 register and a name. You can find the RS485 protocol document at various places online, search the [Power Forum](https://www.powerforum.co.za) or [Github issue #59](https://github.com/kellerza/sunsynk/issues/59)

The `/share/` folder can be accessed through the Samba addon in Home Assistant. You can create the `hass-addon-sunsynk` folder & the `mysensors.py` file

This is a Python file and follows the same logic as the definitions.py & definitions3p.py. It exposes a single `SENSORS` global variable to which you can add the individual sensor definitions.

An example `mysensors.py` file:

```python
from sunsynk import AMPS, CELSIUS, KWH, VOLT, WATT, Sensor, SensorDefinitions
from sunsynk.rwsensors import NumberRWSensor, SelectRWSensor, TimeRWSensor
from sunsynk.sensors import MathSensor, TempSensor

# Initialize the sensor definitions
SENSORS = SensorDefinitions()

# Add your custom sensors
SENSORS += (
    # Basic sensor example
    Sensor(178, "My Custom Power Sensor", WATT, -1),

    # Math sensor example (combining multiple registers)
    MathSensor((175, 172), "Custom Combined Power", WATT, factors=(1, 1)),

    # Read/Write sensor example
    NumberRWSensor(130, "Custom Control Setting", "%", min=0, max=100),
)
```

The sensor definition parameters are:

- First parameter: Register number(s)
- Second parameter: Sensor name
- Third parameter: Unit (WATT, VOLT, AMPS, etc.)
- Last parameter: Scale factor (optional)

You can create different types of sensors:

- `Sensor`: Basic read-only sensor
- `MathSensor`: Combines multiple registers with mathematical operations
- `NumberRWSensor`: Read/write sensor for configurable values
- `SelectRWSensor`: Read/write sensor with predefined options
- `SwitchRWSensor`: Read/write sensor for boolean values

An example of adding a custom selling load sensor, the takes the ct power off the inverter output is

```python
MathSensor((175, 172), "Selling Load Power direct", WATT, factors=(1, 1)),
```

Once defined, your custom sensors will be loaded automatically when the addon starts, and you'll see them listed in the startup logs:

```log
INFO    Importing /share/hass-addon-sunsynk/mysensors.py...
INFO      custom sensors: my_custom_power_sensor, custom_combined_power, custom_control_setting
```

## Using the sensor

Once a sensor is loaded, you still have to add it to your configuration:

```yaml
SENSORS:
 - my_custom_sensor_1
 - my_custom_sensor_2
```

You can also add **all** the custom sensors, using the special group called `mysensors`.

```yaml
SENSORS:
  - mysensors
```

## More examples

### Python based sensor

This sensors divides 2 registers (reg 10/reg 20)

```python
import attrs
from sunsynk import Sensor, SensorDefinitions, WATT
from sunsynk.helpers import unpack_value

@attrs.define(slots=True, eq=False)
class MyCustomSensor(Sensor):
    """Custom sensor, using multiple registers."""

    def reg_to_value(self, regs: RegType) -> ValType:
        """Calculate the value."""
        val1 = unpack_value((regs[0],), signed=True)
        val2 = unpack_value((regs[1],), signed=True)
        return val1 / val2


SENSORS = SensorDefinition()

# Use the class above with register 10 and 20
SENSORS += MyCustomSensor((10, 20), "Mysensor1", WATT)
```

### Time sensor

::: info
Write is only partially implemented in the example below
:::

::: details

```python
import attrs
import re

from sunsynk import RegType, ValType, SensorDefinitions
from sunsynk.rwsensors import RWSensor, ResolveType

SENSORS = SensorDefinitions()


@attrs.define(slots=True, eq=False)
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
