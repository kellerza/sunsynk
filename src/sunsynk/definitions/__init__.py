"""Sensor definitions."""

from sunsynk.sensors import EnumSensor

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
