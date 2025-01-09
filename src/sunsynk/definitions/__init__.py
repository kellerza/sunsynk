"""Sensor definitions."""

from sunsynk.sensors import EnumSensor, SerialSensor

PROG_CHARGE_OPTIONS = {
    0: "No Grid or Gen",
    1: "Allow Grid",
    2: "Allow Gen",
    3: "Allow Grid & Gen",
}
PROG_MODE_OPTIONS = {
    0 << 2: "None",
    1 << 2: "General",
    2 << 2: "Backup",
    3 << 2: "Charge",
}

DEVICE_TYPE = EnumSensor(
    0,
    "Device type",
    options={
        2: "Inverter",
        3: "Single phase hybrid",
        4: "Microinverter",
        5: "Low voltage three phase hybrid",
        6: "High voltage three phase hybrid",
    },
)

SERIAL_SENSOR = SerialSensor((3, 4, 5, 6, 7), "Serial")
