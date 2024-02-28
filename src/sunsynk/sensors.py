"""Sensor classes represent modbus registers for an inverter."""
from __future__ import annotations

import logging
from typing import Optional, Union

import attrs

from sunsynk.helpers import (
    NumType,
    RegType,
    ValType,
    ensure_tuple,
    int_round,
    signed,
    slug,
)

_LOGGER = logging.getLogger(__name__)


@attrs.define(slots=True, eq=False)
class Sensor:
    """Sunsynk sensor."""

    # pylint: disable=too-many-instance-attributes
    address: RegType = attrs.field(converter=ensure_tuple)
    name: str = attrs.field()
    unit: str = attrs.field(default="")
    factor: float = attrs.field(default=1)
    bitmask: int = attrs.field(default=0)

    @property
    def id(self) -> str:
        """Get the sensor ID."""
        return slug(self.name)

    def reg_to_value(self, regs: RegType) -> ValType:
        """Return the value from the registers."""
        regs = self.masked(regs)
        val: NumType = regs[0]
        if len(regs) == 2:
            val += regs[1] << 16
        elif self.factor < 0:  # Indicates this register is signed
            val = signed(val)
        val = int_round(val * abs(self.factor))
        _LOGGER.debug("%s=%s%s %s", self.id, val, self.unit, regs)
        return val

    def masked(self, regs: RegType) -> RegType:
        """Return the masked reg."""
        if self.bitmask:
            return tuple(r & self.bitmask for r in regs)
        return regs

    def __hash__(self) -> int:
        """Hash the sensor id."""
        return hash((self.address, self.name))

    def __eq__(self, other: object) -> bool:
        """Sensor equality is based on the ID only."""
        if not isinstance(other, Sensor):
            raise TypeError(str(type(other)))
        return self.id == other.id


@attrs.define(slots=True, eq=False)
class BinarySensor(Sensor):
    """Binary sensor."""

    off: Optional[int] = attrs.field(default=None)
    on: Optional[int] = attrs.field(default=None)

    def reg_to_value(self, regs: RegType) -> ValType:
        """Reg to value for binary."""
        res = super().reg_to_value(regs)
        if self.on is not None and self.off is not None:
            if res not in [self.on, self.off]:
                return None
        if self.on is not None:
            return res == self.on
        if self.off is not None:
            return res != self.off
        return bool(res)


@attrs.define(slots=True)
class SensorDefinitions:
    """Definitions."""

    all: dict[str, Sensor] = attrs.field(factory=dict)
    deprecated: dict[str, str] = attrs.field(factory=dict)
    """map of 'old_name': 'new_name'"""

    @property
    def serial(self) -> Sensor:
        """Get the serial sensor."""
        return self.all["serial"]

    @property
    def rated_power(self) -> Sensor:
        """Get the rated power sensor."""
        return self.all["rated_power"]

    def __add__(
        self, item: Union[Sensor, tuple[Sensor, ...], list[Sensor]]
    ) -> SensorDefinitions:
        """Add new sensors."""
        if isinstance(item, Sensor):
            self.all[item.id] = item
            return self
        if isinstance(item, (tuple, list)):
            for itm in item:
                self.all[itm.id] = itm
        return self

    def copy(self) -> SensorDefinitions:
        """Copy the sensor definitions."""
        return SensorDefinitions(all=self.all.copy(), deprecated=self.deprecated.copy())


@attrs.define(slots=True, eq=False)
class MathSensor(Sensor):
    """Math sensor, add multiple registers."""

    factors: tuple[float, ...] = attrs.field(default=None, converter=ensure_tuple)
    no_negative: bool = attrs.field(default=False)
    absolute: bool = attrs.field(default=False)

    def reg_to_value(self, regs: RegType) -> ValType:
        """Calculate the math value."""
        val = int_round(sum(signed(i) * s for i, s in zip(regs, self.factors)))
        if self.absolute and val < 0:
            val = -val
        if self.no_negative and val < 0:
            val = 0
        return val

    def __attrs_post_init__(self) -> None:
        """Ensure correct parameters."""
        assert len(self.address) == len(self.factors)


@attrs.define(slots=True, eq=False)
class TempSensor(Sensor):
    """Offset by 100 for temperature."""

    def reg_to_value(self, regs: RegType) -> ValType:
        """Decode the temperature (offset by 100)."""
        try:
            val = regs[0]
            return int_round((float(val) * abs(self.factor)) - 100)  # type: ignore
        except (TypeError, ValueError) as err:
            _LOGGER.error("Could not decode temperature: %s", err)
        return None


@attrs.define(slots=True, eq=False)
class SDStatusSensor(Sensor):
    """SD card status."""

    def reg_to_value(self, regs: RegType) -> ValType:
        """Decode the SD card status."""
        return {
            1000: "fault",
            2000: "ok",
        }.get(regs[0]) or f"unknown {regs[0]}"


@attrs.define(slots=True, eq=False)
class InverterStateSensor(Sensor):
    """Inverter status."""

    def reg_to_value(self, regs: RegType) -> ValType:
        """Decode the inverter status."""
        if regs[0] == 2:
            return "ok"
        return f"unknown {regs[0]}"


@attrs.define(slots=True, eq=False)
class SerialSensor(Sensor):
    """Decode the inverter serial number."""

    def reg_to_value(self, regs: RegType) -> ValType:
        """Decode the inverter serial number."""
        val = ""
        for b16 in regs:
            val += chr(b16 >> 8)
            val += chr(b16 & 0xFF)
        return val


@attrs.define(slots=True, eq=False)
class EnumSensor(Sensor):
    """Sensor with a set of enum values. Like a read-only SelectRWSensor"""

    options: dict[int, str] = attrs.field(factory=dict)

    def available_values(self) -> list[str]:
        """Get the available values for this sensor."""
        return list(self.options.values())

    def reg_to_value(self, regs: RegType) -> ValType:
        """Decode the register."""
        regsm = self.masked(regs)
        res = self.options.get(regsm[0])
        if res is None:
            _LOGGER.warning("%s: Unknown register value %s", self.id, regsm[0])
        return res


@attrs.define(slots=True, eq=False)
class FaultSensor(Sensor):
    """Decode Inverter faults."""

    def reg_to_value(self, regs: RegType) -> ValType:
        """Decode Inverter faults."""
        faults = {
            13: "Working mode change",
            18: "AC over current",
            20: "DC over current",
            23: "F23 AC leak current or transient over current",
            24: "F24 DC insulation impedance",
            26: "F26 DC busbar imbalanced",
            29: "Parallel comms cable",
            35: "No AC grid",
            42: "AC line low voltage",
            47: "AC freq high/low",
            56: "DC busbar voltage low",
            63: "ARC fault",
            64: "Heat sink tempfailure",
        }
        err = []
        off = 0
        for b16 in regs:
            for bit in range(16):
                msk = 1 << bit
                if msk & b16:
                    msg = f"F{bit+off+1:02} " + faults.get(off + msk, "")
                    err.append(msg.strip())
            off += 16
        return ", ".join(err)


@attrs.define(slots=True, eq=False)
class HVFaultSensor(Sensor):
    """Decode HV Inverter faults."""

    def reg_to_value(self, regs: RegType) -> ValType:
        """Decode HV Inverter faults."""
        faults = {
            1: "DC Inversed Failure",
            7: "DC START Failure",
            13: "Working mode change",
            15: "AC over current SW Failure",
            10: "Aux Power Board Failure",
            16: "DC Ground Leakage current fault",
            18: "AC over current TZ",
            20: "DC over current",
            21: "DC HV Bus over current",
            22: "Remote Emergency stop",
            23: "AC leakage current is transient over current",
            24: "DC insulation impedance",
            26: "DC busbar imbalanced",
            29: "Parallel comms cable",
            34: "AC Overload (backup)",
            35: "No AC grid",
            41: "Parallel system stopped",
            42: "AC line low voltage",
            46: "Battery 1 fault",
            49: "Battery 2 fault",
            47: "AC grid freq too high",
            48: "AC grid freq too low",
            52: "DC voltage too high",
            53: "DC voltage too low",
            54: "battery 1 voltage high",
            55: "battery 2 voltage high",
            56: "battery 1 voltage low",
            57: "battery 2 voltage low",
            58: "bms communication lost",
            62: "DRM stop activated",
            63: "ARC fault",
            64: "Heat sink tempfailure",
        }
        err = []
        off = 0
        for b16 in regs:
            for bit in range(16):
                msk = 1 << bit
                if msk & b16:
                    msg = f"F{bit+off+1:02} " + faults.get(off + msk, "")
                    err.append(msg.strip())
            off += 16
        return ", ".join(err)
