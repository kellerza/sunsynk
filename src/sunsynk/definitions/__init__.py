"""Sensor definitions."""

from sunsynk.sensors import EnumSensor, SerialSensor

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
