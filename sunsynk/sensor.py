"""Sensor classes represent modbus registers for an inverter."""
import attr


@attr.s(slots=True)
class Sensor:
    """sunsynk sensor."""

    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-few-public-methods
    register: int = attr.ib()
    name: str = attr.ib()
    unit: str = attr.ib(default="")
    factor: float = attr.ib(default=1)
    high: int = attr.ib(default=None)  # The high register for 32-bit values


# convert
# a = (msg.payload.data / 10)
# if (a > 32767) {
# msg.payload = (a - 65535) / 10;
# } else {
#     msg.payload = (a) / 1;
# }
