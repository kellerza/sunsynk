"""Sensor classes represent modbus registers for an inverter."""

from __future__ import annotations

import logging
from statistics import mean

import attrs

from sunsynk.helpers import (
    NumType,
    RegType,
    ValType,
    ensure_tuple,
    int_round,
    slug,
    unpack_value,
)

_LOGGER = logging.getLogger(__name__)


@attrs.define(slots=True, eq=False)
class Sensor:
    """Sunsynk sensor."""

    # pylint: disable=too-many-instance-attributes
    address: RegType = attrs.field(converter=ensure_tuple)
    name: str
    unit: str = ""
    factor: float = 1
    bitmask: int = 0

    @property
    def id(self) -> str:
        """Get the sensor ID."""
        return slug(self.name)

    def reg_to_value(self, regs: RegType) -> ValType:
        """Return the value from the registers."""
        regs = self.masked(regs)
        val: NumType = unpack_value(regs, signed=self.factor < 0)
        val = int_round(float(val) * abs(self.factor))
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
class Sensor16(Sensor):
    """Sensor with a 16-bit/32-bit register registers."""

    history1: list[int] = attrs.field(factory=list)
    """History of reg[1]. If last 10 are all > 0, unpack as 32-bit, else only 16-bit."""
    history0: list[int] = attrs.field(factory=list)

    def reg_to_value(self, regs: RegType) -> ValType:
        """Return the value from the registers."""
        regs = self.masked(regs)
        self.history1.append(regs[1])
        self.history0.append(regs[0])
        if len(self.history1) > 10:
            self.history1.pop(0)
            self.history0.pop(0)
        # _LOGGER.debug("%s %s", hex_str(regs), mean(self.history0))
        if (
            any(r == 0 for r in self.history1)  # reg[1] between negative and positive
            or (  # a big drop in reg[0] could also be close to a neg to pos transition
                regs[1] == 0xFFFF and mean(self.history0) - regs[0] > 10000
            )
        ):
            regs = (regs[0],)
        val: NumType = unpack_value(regs, signed=self.factor < 0)
        val = int_round(float(val) * abs(self.factor))
        return val

    def __attrs_post_init__(self) -> None:
        """Ensure correct parameters."""
        assert len(self.address) == 2


@attrs.define(slots=True, eq=False)
class TextSensor(Sensor):
    """Text/non-numeric sensors are discovered differently."""


@attrs.define(slots=True, eq=False)
class BinarySensor(Sensor):
    """Binary sensor."""

    off: int = 0
    on: int | None = None

    def reg_to_value(self, regs: RegType) -> ValType:
        """Reg to value for binary."""
        res = super().reg_to_value(regs)
        if res is None:
            return None
        if self.on is not None:
            return res == self.on
        return res != self.off


@attrs.define(slots=True)
class SensorDefinitions:
    """Definitions."""

    all: dict[str, Sensor] = attrs.field(factory=dict)
    deprecated: dict[str, str] = attrs.field(factory=dict)
    """map of 'old_name': 'new_name'"""

    @property
    def device_type(self) -> Sensor:
        """Get the device type."""
        return self.all["device_type"]

    @property
    def protocol(self) -> Sensor:
        """Get the device type."""
        return self.all["protocol"]

    @property
    def serial(self) -> Sensor:
        """Get the serial sensor."""
        return self.all["serial"]

    @property
    def rated_power(self) -> Sensor:
        """Get the rated power sensor."""
        return self.all["rated_power"]

    def __add__(
        self, item: Sensor | tuple[Sensor, ...] | list[Sensor]
    ) -> SensorDefinitions:
        """Add new sensors."""
        if isinstance(item, Sensor):
            self.all[item.id] = item
            return self
        if isinstance(item, (tuple | list)):
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
    no_negative: bool = False
    absolute: bool = False

    def reg_to_value(self, regs: RegType) -> ValType:
        """Calculate the math value."""
        val = int_round(
            sum(
                unpack_value((i,), signed=True) * s
                for i, s in zip(regs, self.factors, strict=False)
            )
        )
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

    offset: int = 100

    def reg_to_value(self, regs: RegType) -> ValType:
        """Decode the temperature (offset)."""
        try:
            val = regs[0]
            return int_round((float(val) * abs(self.factor)) - self.offset)  # type: ignore[]
        except (TypeError, ValueError) as err:
            _LOGGER.error("Could not decode temperature: %s", err)
        return None


@attrs.define(slots=True, eq=False)
class SDStatusSensor(TextSensor):
    """SD card status."""

    def reg_to_value(self, regs: RegType) -> ValType:
        """Decode the SD card status."""
        return {
            1000: "fault",
            2000: "ok",
        }.get(regs[0]) or f"unknown {regs[0]}"


@attrs.define(slots=True, eq=False)
class InverterStateSensor(TextSensor):
    """Inverter status."""

    def reg_to_value(self, regs: RegType) -> ValType:
        """Decode the inverter status."""
        return {
            0: "standby",
            1: "selfcheck",
            2: "ok",
            3: "alarm",
            4: "fault",
            5: "activating",
        }.get(regs[0]) or f"unknown {regs[0]}"


@attrs.define(slots=True, eq=False)
class SerialSensor(Sensor):
    """Decode the inverter serial number."""

    def reg_to_value(self, regs: RegType) -> ValType:
        """Decode the inverter serial number."""
        return "".join(chr(b16 >> 8) + chr(b16 & 0xFF) for b16 in regs)


@attrs.define(slots=True, eq=False)
class EnumSensor(TextSensor):
    """Sensor with a set of enum values. Like a read-only SelectRWSensor."""

    options: dict[int, str] = attrs.field(factory=dict)
    unknown: str | None = None
    """Unknown value format string. Default to none, can include the register value as {}."""
    _warn: bool = True

    def available_values(self) -> list[str]:
        """Get the available values for this sensor."""
        return list(self.options.values())

    def reg_to_value(self, regs: RegType) -> ValType:
        """Decode the register."""
        regsm = self.masked(regs)
        res = self.options.get(regsm[0])
        if res is None:
            if self.unknown:
                return self.unknown.format(regsm[0])
            if self._warn:
                _LOGGER.warning(
                    "%s: Unknown register value %s. "
                    "Consider extending the definition with a PR. "
                    "https://github.com/kellerza/sunsynk/tree/main/src/sunsynk/definitions",
                    self.id,
                    regsm[0],
                )
            self._warn = False
            return None
        self._warn = True
        return res


@attrs.define(slots=True, eq=False)
class FaultSensor(TextSensor):
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
                    msg = f"F{bit + off + 1:02} " + faults.get(off + msk, "")
                    err.append(msg.strip())
            off += 16
        return ", ".join(err)


@attrs.define(slots=True, eq=False)
class HVFaultSensor(TextSensor):
    """Decode HV Inverter faults."""

    def reg_to_value(self, regs: RegType) -> ValType:
        """Decode HV Inverter faults."""
        faults = {
            1: "DC Inversed Failure",
            2: "DC insula�on impedance permanent fault",
            3: "DC leakage current fault",
            4: "Ground fault GFDI",
            5: "Read the memory error",
            6: "Write the memory error",
            7: "DC START Failure",
            8: "GFDI grounding touch failure",
            9: "IGBT damaged by excessive drop voltage",
            10: "Auxiliary power supply failure",
            11: "AC main contactor errors",
            12: "AC auxiliary contactor errors",
            13: "Working mode change",
            14: "DC over current SW Failure",
            15: "AC over current SW Failure",
            16: "DC Ground Leakage current fault",
            18: "AC over current TZ",
            19: "All hardware failure synthesis",
            20: "DC over current",
            21: "DC HV Bus over current",
            22: "Remote Emergency stop",
            23: "AC leakage current is transient over current",
            24: "DC insulation impedance",
            25: "DC feedback fault",
            26: "DC busbar imbalanced",
            27: "DC end insula�on error",
            28: "Inverter 1 DC high fault",
            29: "Parallel comms cable/AC load switch failure",
            30: "AC main contactor failure",
            31: "Relay open circuit fault",
            32: "Inverter 2 dc high fault",
            33: "AC Overcurrent",
            34: "AC Overload (backup)",
            35: "No AC grid",
            36: "AC grid phase error",
            37: "AC three-phase voltage unbalance failure",
            38: "AC three-phase current unbalance failure",
            39: "AC over current (one cycle)",
            40: "DC over current",
            41: "Parallel system stopped",
            42: "AC line low voltage",
            43: "AC Line V,W over voltage",
            44: "AC Line V,W low voltage",
            45: "AC Line U,V over voltage",
            46: "Battery 1 fault",
            47: "AC grid freq too high",
            48: "AC grid freq too low",
            49: "Battery 2 fault",
            50: "V phase grid current DC component over current",
            51: "W phase grid current DC component over current",
            52: "DC voltage too high",
            53: "DC voltage too low",
            54: "battery 1 voltage high",
            55: "battery 2 voltage high",
            56: "battery 1 voltage low",
            57: "battery 2 voltage low",
            58: "bms communication lost",
            59: "AC grid V over current",
            60: "AC grid W over current",
            61: "Reactor A phase over current",
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
                    msg = f"F{bit + off + 1:02} " + faults.get(off + msk, "")
                    err.append(msg.strip())
            off += 16
        return ", ".join(err)


@attrs.define(slots=True, eq=False)
class ProtocolVersionSensor(Sensor):
    """Protocol version sensor."""

    def reg_to_value(self, regs: RegType) -> ValType:
        """Reg to value for communication protocol."""
        val = regs[0]
        return f"{val >> 8}.{val & 0xFF}"
